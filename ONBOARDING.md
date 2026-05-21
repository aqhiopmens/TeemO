# TeemO 팀 셋업 가이드

> 우리 팀 4명이 같은 환경에서 작업하기 위한 30분짜리 셋업 가이드입니다.
> 막히는 부분은 바로 단톡에 물어봐 주세요.

## 우리가 만드는 것
- **TeemO**: 책 추천 웹앱 (사용자가 읽은 책 + 평점 → AI가 다음 책 추천)
- 알고리즘 수업 팀프로젝트 (2026-1)
- **발표일**: 2026-06-09 또는 06-11 (영어)

## 필요한 것
- 노트북 (Windows / Mac 모두 OK)
- 인터넷
- **VS Code** (수업에서 쓰는 그거. 없으면 https://code.visualstudio.com 에서 설치)
- GitHub 계정 (없으면 STEP 1)
- Claude 계정 정보 (단톡 별도 공지)

## 각 STEP 어디서 하는지

| STEP | 어디서 |
|---|---|
| STEP 1 — GitHub 가입 | 🌐 브라우저 |
| STEP 2 — Claude Code 설치 | ⌨️ VS Code 터미널 |
| STEP 3 — Claude 로그인 | ⌨️ VS Code 터미널 → 🌐 브라우저 (자동) → ⌨️ 터미널로 복귀 |
| STEP 4 — 저장소 clone | ⌨️ VS Code 터미널 |
| STEP 5 — 첫 실행 | ⌨️ VS Code 터미널 (Claude Code UI 열림) |

### VS Code 터미널 여는 법
1. VS Code 실행
2. 메뉴 **Terminal → New Terminal**
   - 또는 단축키: Windows/Linux `` Ctrl + ` ``  (백틱) / Mac `` Cmd + ` ``
3. 화면 아래쪽에 터미널 창이 열림 → 여기에 명령어 입력

> **Windows에서 셸이 PowerShell이 아니면**: 터미널 창 우측 상단 **`+` 옆 ▼** 클릭 → **PowerShell** 선택

---

## STEP 1 — GitHub 계정 만들기 (이미 있으면 STEP 2로)

📍 **어디서**: 🌐 브라우저

1. https://github.com/signup
2. 이메일 (학교 메일 OK) / 비밀번호 / **username 신중히** (커밋에 본인 이름으로 표시됨)
3. 가입 후 본인 username을 **단톡에 공유** → owner가 저장소에 collaborator로 초대
4. 메일로 초대장 도착 → **Accept invitation** 클릭

---

## STEP 2 — Claude Code 설치

📍 **어디서**: ⌨️ VS Code 터미널

> **이미 설치돼 있으면 이 단계 스킵.** 확인하려면 터미널에서 `claude --version` 실행 → 버전 번호 나오면 OK, STEP 3으로.

### Windows (PowerShell)
```powershell
irm https://claude.ai/install.ps1 | iex
```

### Mac / Linux
```bash
curl -fsSL https://claude.ai/install.sh | bash
```

### 어느 OS든 npm 있으면
```bash
npm install -g @anthropic-ai/claude-code
```

설치 확인:
```bash
claude --version
```

---

## STEP 3 — 공유 Claude 계정 로그인

📍 **어디서**: ⌨️ VS Code 터미널 → 🌐 브라우저 (자동으로 열림) → ⌨️ 터미널로 자동 복귀

교수님이 주신 Claude Max 계정을 4명이 공유합니다. 이 계정은 **Google 계정**과 연동돼 있어요. 단톡에서 다음 2가지를 받으세요:

1. **이메일** (Google 계정 주소)
2. **비밀번호**

> 비밀번호는 받은 즉시 본인 메모장으로 옮기고 단톡에선 지워주세요.

### 이미 본인 Claude 계정으로 로그인돼 있다면?

Claude Code 실행 후 슬래시 명령으로 계정 전환:
```bash
claude
```
Claude Code UI가 뜨면 그 안에 입력:
```
/login
```
→ 브라우저 열림 → 공유 계정으로 로그인 → 완료.

> **본인 개인 계정 데이터는 안 사라집니다.** 학기 끝나고 `/login`으로 본인 계정 다시 선택하면 그대로 돌아옴.
> 잘 안 되면 `/logout` 먼저 한 다음 `/login`.

### 처음 Claude Code 쓰는 경우

로그인:
```bash
claude
```
- 브라우저가 자동으로 열림
- **"Continue with Google"** 클릭
- 위 정보로 로그인
- "Trust this device / 이 기기 신뢰" 체크박스 보이면 체크
- 한 번 로그인하면 본인 노트북에 저장 → 다음부턴 자동

> ⚠️ **처음 로그인 시 Google이 "새 기기에서 로그인" 알림을 보낼 수 있습니다.** 본인이 맞으니 안내에 따라 "Yes, it was me" 클릭하면 됩니다. 계정이 일시 잠기면 단톡에 "로그인 막혔어" 한마디 → owner가 풀어줄 수 있음.

---

## STEP 4 — 저장소 받기

📍 **어디서**: ⌨️ VS Code 터미널

원하는 폴더에서 (예: `Documents` 안에):
```bash
git clone https://github.com/aqhiopmens/TeemO.git
cd TeemO
```

Git을 처음 쓰는 거라면 본인 정보 설정 (한 번만):
```bash
git config --global user.name "본인 이름"
git config --global user.email "본인 이메일"
```

---

## STEP 5 — 첫 실행

📍 **어디서**: ⌨️ VS Code 터미널 (실행 후 그 안에 Claude Code UI가 열림)

VS Code에서 **File → Open Folder** 로 방금 clone한 `TeemO` 폴더 열기.
그 다음 터미널 열고:

```bash
claude
```

Claude Code가 `CLAUDE.md`를 자동으로 읽어서 프로젝트 컨텍스트를 파악합니다.
시험 삼아 이렇게 물어보세요:

> "이 프로젝트가 뭐 하는 거고 내 역할이 뭐야?"

본인 역할에 맞는 답이 나오면 셋업 성공 ✅

---

## 팀 협업 규칙 (꼭 읽어주세요)

### 두 개의 트랙

| 트랙 | 브랜치 prefix | 담당자 | 만지는 폴더 |
|---|---|---|---|
| App | `feature/app-*` | 김강민 (BE) + 서은빈 (FE) | `backend/` (llm 제외), `frontend/` |
| LLM | `feature/llm-*` | 박병진 | `backend/llm/` |

### 새 작업 시작 시
```bash
git checkout main
git pull
git checkout -b feature/app-내작업이름   # 또는 feature/llm-내작업이름
```

### 작업 끝나고 push
```bash
git add 수정한_파일
git commit -m "한 줄 요약"
git pull --rebase origin feature/app-내작업이름   # App 트랙은 둘이 공유하니까 필수
git push -u origin feature/app-내작업이름
```

### PR 만들기
- push 후 터미널에 PR 생성 URL이 표시됨 → 클릭
- 다른 트랙 사람에게 리뷰 요청
- approve 받으면 **Merge** 버튼

### Claude 동시 사용 시 매너
- 4명이 **같은 계정 = 같은 rate limit 풀** 공유
- 일반적인 코딩 작업은 동시에 해도 거의 안 부족함
- 단, **무거운 작업** (예: 30분 이상 agent 세션, 전체 코드 리팩토링) 시작 전엔 단톡에 한마디:
  > "나 30분 정도 claude로 무거운 거 돌릴게"
- 본인 대화 기록은 **본인 노트북에만** 저장됨 (다른 사람 못 봄)

---

## 자주 막히는 곳

| 증상 | 해결 |
|---|---|
| `claude` 명령어 못 찾음 | 새 터미널 창 열기 (PATH 갱신) |
| 다른 Claude 계정으로 로그인돼 있음 | `claude` 실행 후 `/login` → 공유 계정으로 전환 |
| Google 로그인 시 "수상한 활동" 차단 | 단톡에 알림 → owner가 myaccount.google.com에서 "Yes, it was me" 클릭 |
| `git push` 거부됨 (permission denied) | collaborator 초대 수락 안 함 → STEP 1 마지막 확인 |
| Claude가 프로젝트 컨텍스트 모름 | `CLAUDE.md`가 있는 폴더에서 `claude` 실행했는지 확인 |
| 한국어 입력 깨짐 | Windows: `chcp 65001` 실행 |

---

## 다음 할 일

셋업 완료되면 단톡에 **"셋업 완료"** 알려주세요.
이후 각자 첫 작업은 다음과 같이 시작하면 됩니다:

- **김강민/서은빈**: `feature/app-` 으로 시작하는 첫 작업 정하기 (예: 검색 UI 다듬기, 새 알고리즘 추가)
- **박병진**: `feature/llm-` 으로 시작 (예: 프롬프트 v2, 응답 캐싱)
- **오세준 (PM)**: 일정·문서 정리, GitHub Issues로 할 일 트래킹

질문은 단톡에서 받습니다. 🚀
