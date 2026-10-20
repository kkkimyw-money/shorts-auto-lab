import os, json, random, subprocess, asyncio, textwrap
from pathlib import Path
from datetime import datetime, timezone
from PIL import Image, ImageDraw, ImageFont
import edge_tts

ROOT=Path(__file__).parent
OUT=ROOT/'output'; OUT.mkdir(exist_ok=True)
FONT="/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
TOPICS={
 'A': [
 ('숫자를 볼 때 주의할 점','조회수가 높다고 모두 좋은 콘텐츠는 아닙니다.','채널 규모와 업로드 후 경과 시간을 함께 비교하세요.','성과는 절대 조회수보다 상대적인 증가 속도로 보세요.'),
 ('무료 도구를 고를 때','무료라는 표현보다 실제 사용 제한을 확인하세요.','API 할당량과 실행 시간과 저장 공간을 확인해야 합니다.','도구보다 반복 가능한 작업 흐름이 중요합니다.'),
 ('정보를 빠르게 검증하는 방법','놀라운 주장을 발견하면 출처부터 확인하세요.','게시 날짜와 원문과 반대 근거를 찾아보세요.','확인되지 않은 숫자는 영상에 넣지 마세요.')],
 'B': [
 ('작은 사업의 첫 번째 지표','매출만 보고 사업이 잘된다고 판단하면 위험합니다.','판매 한 건의 변동비와 고객 획득 비용을 계산하세요.','반복 구매와 공헌이익이 사업의 지속성을 좌우합니다.'),
 ('자동화 전에 할 일','반복 업무를 자동화하기 전에 절차부터 표준화하세요.','입력과 출력과 예외 상황을 문서화하세요.','잘못된 프로세스를 자동화하면 오류만 빨라집니다.'),
 ('AI를 업무에 도입할 때','AI 도구를 늘리는 것이 생산성 향상은 아닙니다.','반복 시간과 오류율을 도입 전후로 측정하세요.','측정할 수 있는 한 가지 업무부터 시작하세요.')]
}
def text_image(lines, path):
    im=Image.new('RGB',(720,1280),(17,23,36)); d=ImageDraw.Draw(im)
    font=ImageFont.truetype(FONT,49); small=ImageFont.truetype(FONT,29)
    d.rounded_rectangle((38,90,682,1190),radius=38,fill=(30,42,61))
    y=260
    for line in lines:
        # Korean-friendly wrap by measured width
        words=line.split(' '); buf=''; chunks=[]
        for w in words:
            test=(buf+' '+w).strip()
            if d.textbbox((0,0),test,font=font)[2]>560 and buf:
                chunks.append(buf);buf=w
            else: buf=test
        if buf:chunks.append(buf)
        for chunk in chunks:
            d.text((80,y),chunk,font=font,fill=(245,247,251));y+=80
        y+=85
    d.text((80,1080),'AI SHORTS LAB  |  ORIGINAL',font=small,fill=(137,189,225))
    im.save(path)
async def voice(text, path):
    await edge_tts.Communicate(text,voice='ko-KR-SunHiNeural',rate='-5%').save(str(path))
def run(cmd): subprocess.run(cmd,check=True)
def make(kind, idx):
    title,*parts=TOPICS[kind][idx%len(TOPICS[kind])]
    key=f'{kind}_{datetime.now(timezone.utc).strftime("%Y%m%d")}_{idx}'
    png=OUT/(key+'.png'); mp3=OUT/(key+'.mp3'); mp4=OUT/(key+'.mp4')
    text_image([title]+parts,png)
    asyncio.run(voice(' '.join([title]+parts),mp3))
    # 9:16 H264 with still background, narration; length determined by audio
    run(['ffmpeg','-y','-loglevel','error','-loop','1','-framerate','25','-i',str(png),'-i',str(mp3),'-c:v','libx264','-preset','veryfast','-tune','stillimage','-c:a','aac','-b:a','128k','-pix_fmt','yuv420p','-shortest','-movflags','+faststart',str(mp4)])
    return {'kind':kind,'title':title,'video':str(mp4),'description':f'{title}\n직접 제작한 정보 콘텐츠입니다. #Shorts #정보' if kind=='A' else f'{title}\n업무와 사업을 위한 실행 아이디어. #Shorts #창업'}
def upload(item):
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    from google.auth.transport.requests import Request
    required=['YT_CLIENT_ID','YT_CLIENT_SECRET','YT_REFRESH_TOKEN']
    if any(not os.getenv(k) for k in required): return 'SKIPPED: credentials not configured'
    creds=Credentials(None,refresh_token=os.environ['YT_REFRESH_TOKEN'],token_uri='https://oauth2.googleapis.com/token',client_id=os.environ['YT_CLIENT_ID'],client_secret=os.environ['YT_CLIENT_SECRET'],scopes=['https://www.googleapis.com/auth/youtube.upload'])
    creds.refresh(Request())
    service=build('youtube','v3',credentials=creds,cache_discovery=False)
    req=service.videos().insert(part='snippet,status',body={'snippet':{'title':item['title'],'description':item['description'],'categoryId':'27'},'status':{'privacyStatus':'private','selfDeclaredMadeForKids':False}},media_body=MediaFileUpload(item['video'],mimetype='video/mp4',resumable=True))
    response=None
    while response is None: _,response=req.next_chunk()
    return 'PRIVATE VIDEO ID: '+response['id']
if __name__=='__main__':
    # Alternate categories daily; use a fixed topic index per day
    day=int(datetime.now(timezone.utc).strftime('%j'))
    kind='A' if day%2 else 'B'
    item=make(kind,day//2)
    item['upload_result']=upload(item)
    (OUT/'manifest.json').write_text(json.dumps(item,ensure_ascii=False,indent=2))
    print(json.dumps(item,ensure_ascii=False,indent=2))
