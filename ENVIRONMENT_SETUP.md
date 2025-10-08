# 환경 변수 설정 가이드

## 환경 변수 설정 방법

### 1. Gmail 앱 패스워드 생성

1. Gmail 계정의 2단계 인증을 활성화
2. Google 계정 관리 > 보안 > 앱 패스워드 생성
3. 생성된 16자리 앱 패스워드를 복사

### 2. uv 설치 및 가상환경 설정 (추천)

1. uv 설치:
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   # 또는 homebrew: brew install uv
   ```

2. 가상환경 생성 및 의존성 설치:
   ```bash
   uv sync
   ```

### 3. 환경 변수 설정 방법

#### 방법 1: .env 파일 사용 (추천)

1. `.env.example` 파일을 `.env`로 복사:
   ```bash
   cp .env.example .env
   ```

2. `.env` 파일을 실제 정보로 수정:
   ```env
   GMAIL_SENDER_EMAIL=your-email@gmail.com
   GMAIL_RECEIVER_EMAIL=receiver@example.com
   GMAIL_APP_PASSWORD=abcdefghijklmnop
   ```

3. python-dotenv 라이브러리 설치:
   ```bash
   pip install python-dotenv
   ```

4. 코드에서 .env 파일 로드 (자동으로 환경 변수에 설정됨)

#### 방법 2: 직접 환경 변수 설정

**Linux/macOS/WSL:**
```bash
export GMAIL_SENDER_EMAIL="your-email@gmail.com"
export GMAIL_RECEIVER_EMAIL="receiver@example.com"
export GMAIL_APP_PASSWORD="your-16-character-app-password"
```

**Windows CMD:**
```cmd
set GMAIL_SENDER_EMAIL=your-email@gmail.com
set GMAIL_RECEIVER_EMAIL=receiver@example.com
set GMAIL_APP_PASSWORD=your-16-character-app-password
```

**Windows PowerShell:**
```powershell
$env:GMAIL_SENDER_EMAIL="your-email@gmail.com"
$env:GMAIL_RECEIVER_EMAIL="receiver@example.com"
$env:GMAIL_APP_PASSWORD="your-16-character-app-password"
```

#### 방법 3: 실행 시 환경 변수 지정

```bash
GMAIL_SENDER_EMAIL="your-email@gmail.com" \
GMAIL_RECEIVER_EMAIL="receiver@example.com" \
GMAIL_APP_PASSWORD="your-app-password" \
python3 python-gmail.py
```

### 4. 실행 및 확인

#### uv 사용시 (추천)
```bash
uv run python-gmail.py
```

#### 일반 Python 사용시
```bash
python3 python-gmail.py
```

### 보안 주의사항

- `.env` 파일을 Git에 커밋하지 마세요 (`.gitignore`에 포함됨)
- 앱 패스워드는 절대 코드에 하드코딩하지 마세요
- 앱 패스워드가 유출되면 즉시 Google 계정에서 해당 패스워드를 삭제하세요