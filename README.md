# python-gmail
Send email via Gmail SMTP with Python

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
   ```

3. 환경 변수 설정:
   ```bash
   cp .env.example .env
   # .env 파일을 실제 Gmail 계정 정보로 수정
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
```

## 테스트 코드 실행

### uv로 테스트 실행 (권장)
```bash
uv run pytest test_python_gmail.py
```

### 일반 Python 환경에서 테스트 실행
```bash
pytest test_python_gmail.py
```

테스트 파일은 `test_python_gmail.py` 입니다. pytest가 설치되어 있어야 하며, 개발 환경에서는 `uv sync --dev`로 자동 설치됩니다.

자세한 환경 변수 설정 방법은 [ENVIRONMENT_SETUP.md](ENVIRONMENT_SETUP.md)를 참고하세요.

## 개발

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
