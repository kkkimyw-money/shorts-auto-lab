# 스마트폰 전용 0원 Shorts MVP

## 준비
- GitHub 계정, Google/YouTube 채널, 스마트폰 브라우저(데스크톱 사이트 모드 권장)
- GitHub에서 **새 public repository**를 만들고 이 압축 파일의 내용을 업로드합니다. `.github/workflows/daily.yml` 경로를 유지하세요.
- GitHub → Actions → Daily Shorts MVP → Run workflow를 실행합니다.
- 완료 후 해당 실행의 Artifacts → shorts-output을 다운로드하면 MP4와 manifest.json을 확인할 수 있습니다.
- 기본 상태에서는 **YouTube에 업로드하지 않습니다**. 비공개 자동 업로드는 아래 OAuth 연결 이후에만 작동합니다.

## 업로드 연동(고급)
1. Google Cloud Console에서 프로젝트를 만들고 YouTube Data API v3를 활성화합니다.
2. OAuth 동의 화면을 구성하고 YouTube 업로드 범위를 설정합니다. 테스트 모드의 refresh token은 짧게 만료될 수 있어 운영에는 게시 상태와 검증 요건을 확인해야 합니다.
3. OAuth 2.0 클라이언트 ID/시크릿과 `youtube.upload` 범위의 refresh token을 합법적인 OAuth 승인 흐름에서 발급받습니다. 스마트폰만으로 토큰 발급은 번거로울 수 있습니다. **비밀번호나 토큰을 공개 저장소에 넣지 마세요.**
4. GitHub → Settings → Secrets and variables → Actions에 `YT_CLIENT_ID`, `YT_CLIENT_SECRET`, `YT_REFRESH_TOKEN`을 등록합니다.
5. 다음 실행부터 비공개(private) 업로드를 시도합니다. 비공개 업로드를 검수한 뒤 YouTube Studio 앱에서 직접 공개하세요.

## 한계 및 다음 단계
- 현 버전은 **실제로 실행 가능한 영상 제작 MVP**이며 바이럴 영상 자동 발굴, AI 자유 대본 생성, 자동 성과 수집은 **미구현**입니다. 템플릿은 사실관계 검토가 필요한 일반 정보 6종입니다.
- edge-tts는 외부 무료 음성 서비스에 의존하며 호출 제한·서비스 변경·약관을 확인해야 합니다. 실패하면 Actions가 실패합니다.
- GitHub Actions 무료 사용량/정책은 변경될 수 있고, 예약 실행은 지연되거나 누락될 수 있습니다.
- YouTube API 프로젝트의 업로드 검증 상태에 따라 게시에 제한이 걸릴 수 있습니다.
- 코드에는 타인의 영상을 다운로드하거나 재업로드하는 기능이 없습니다. 텍스트 슬라이드만 렌더링합니다.
- 현재는 하루 한 개(A/B 교대)입니다. 최소 30개가 모이면 YouTube Studio에서 조회수·시청 지속 시간·구독자 증가를 수동 기록해 비교하세요.
- `main.py`의 `TOPICS`를 수정해 콘텐츠를 바꿀 수 있습니다. 원본성·정확성·저작권을 확인한 뒤 공개하세요.
