# python-gmail
Send email via Gmail SMTP with Python


![version](https://img.shields.io/badge/version-0.2.1-blue)

이 프로젝트는 Gmail SMTP를 통해 이메일을 전송하며, 이메일 본문에 현재 네트워크(IP) 정보와 지정한 지역의 실시간 날씨 정보를 자동으로 포함합니다.

## 주요 기능

- **Gmail SMTP 이메일 전송**: 앱 패스워드를 이용한 안전한 이메일 전송
- **네트워크 정보 자동 포함**: 로컬 IP와 공용 IP 정보 자동 조회
- **날씨 정보 자동 포함**: Open-Meteo API를 사용한 실시간 날씨 정보 (API 키 불필요)

> **예시:**
> 이메일 본문에 아래와 같은 정보가 자동으로 포함됩니다.
> - 현재 네트워크 정보 (로컬/공용 IP)
> - 지정 주소(예: 화성시 동탄) 날씨 정보 (기온, 습도, 풍속, 상태)

## 설치

### uv 사용 (추천)

1. uv 설치 (아직 설치하지 않은 경우):
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   # 또는 homebrew: brew install uv
   ```

2. 가상환경 생성 및 의존성 설치:
   ```bash
   uv sync
   # 또는 uv pip install requests python-dotenv
   ```

3. 환경 변수 설정:
   > **참고:** `.env.example` 파일이 없다면 아래와 같이 직접 생성하세요.
   > ```env
   > GMAIL_SENDER_EMAIL="your-email@gmail.com"
   > GMAIL_RECEIVER_EMAIL="receiver@example.com"
   > GMAIL_APP_PASSWORD="your_app_password"
   > WEATHER_ADDRESS="화성시 동탄"  # (선택) 날씨 정보에 사용할 주소, 미설정시 기본값 사용
   > ```
   ```bash
   cp .env.example .env
   # .env 파일을 실제 Gmail 계정 정보와 원하는 날씨 주소로 수정
   ```

### pip 사용

1. 가상환경 생성:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   # 또는 venv\Scripts\activate  # Windows
   ```

2. 의존성 설치:
   ```bash
   pip install -r requirements.txt
   # 또는 pip install requests python-dotenv
   ```

3. 환경 변수 설정:
   ```bash
   cp .env.example .env
   # .env 파일을 실제 Gmail 계정 정보로 수정
   ```

## 사용법

### uv 사용시
```bash
uv run python_gmail.py
```

### 일반 Python 사용시
```bash
python3 python_gmail.py
#### 이메일 본문 예시
```
[네트워크 정보]
로컬 IP: 192.168.0.2
공용 IP: 1.2.3.4

[날씨 정보 - 화성시 동탄]
기온: 18°C
습도: 60%
풍속: 2.5 m/s
상태: 맑음
```
```

실행 시, 이메일 본문에 네트워크 정보와 날씨 정보가 자동으로 포함됩니다.
날씨 정보의 주소는 환경 변수 `WEATHER_ADDRESS`로 지정할 수 있으며, 미설정시 기본값(화성시 동탄)이 사용됩니다.


## 테스트 코드 실행

### 모든 테스트 실행 (권장)
```bash
uv run pytest tests/
```

### 특정 테스트 파일만 실행
```bash
uv run pytest tests/test_python_gmail.py
uv run pytest tests/test_network_utils.py
uv run pytest tests/test_weather_utils.py
```

### 일반 Python 환경에서 테스트 실행
```bash
pytest tests/
pytest tests/test_python_gmail.py
pytest tests/test_network_utils.py
pytest tests/test_weather_utils.py
```

테스트 파일은 `tests/` 폴더에 있습니다. pytest가 설치되어 있어야 하며, 개발 환경에서는 `uv sync --dev`로 자동 설치됩니다.

자세한 환경 변수 설정 방법은 [ENVIRONMENT_SETUP.md](ENVIRONMENT_SETUP.md)를 참고하세요.

## 개발


### 주요 모듈 구조

- `python_gmail.py` : 메인 실행 파일 (이메일 전송, 네트워크/날씨 정보 포함)
- `module/` : 주요 유틸리티 모듈 폴더
   - `network_utils.py` : 네트워크(IP) 정보 조회 및 포맷팅 함수 제공
   - `weather_utils.py` : 주소 기반 날씨 정보 조회 및 포맷팅 함수 제공
- `tests/` : 단위 테스트 폴더
   - `test_python_gmail.py` : 메인 기능(이메일 전송 등) 테스트
   - `test_network_utils.py` : 네트워크 유틸리티 함수 테스트
   - `test_weather_utils.py` : 날씨 유틸리티 함수 테스트

### 코딩 스타일

이 프로젝트는 현재 작성된 코드를 기준으로 한 실용적인 코딩 스타일을 사용합니다:

- **Ruff**: 통합 린터 및 포맷터
- **MyPy**: 타입 체크 (점진적 적용)
- **88자 줄 길이**: Black 호환 설정
- **Snake_case**: 함수명 및 변수명
- **UPPER_CASE**: 상수 및 환경 변수

자세한 내용은 [CODING_STYLE.md](CODING_STYLE.md)를 참고하세요.

### 개발 도구 설치

```bash
# 개발 도구 설치
uv sync --dev
```

### 코드 품질 관리

```bash
# 코드 자동 수정 (포맷팅 + 자동 수정 가능한 린팅)
./fix_code_style.sh

# 코드 품질 검사
./check_code_quality.sh

# 개별 명령어
uv run ruff format .      # 포맷팅
uv run ruff check --fix . # 린팅 + 자동 수정
uv run ruff check .       # 린팅 검사만
uv run mypy .            # 타입 검사
```
