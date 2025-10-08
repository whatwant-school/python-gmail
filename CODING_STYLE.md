# Python Gmail Project - 코딩 스타일 가이드

## 개요

이 프로젝트는 현재 작성된 코드를 기준으로 **PEP 8**을 베이스로 하되, 실용적인 코딩 스타일을 적용합니다.
코드 품질 관리는 **Ruff**를 사용하여 통합적으로 처리합니다.

## 분석된 현재 코드 스타일

### 네이밍 컨벤션 (현재 코드 기준)

#### 함수명 & 변수명
- **snake_case** 사용
- 명확하고 의미있는 이름
```python
# ✅ 현재 코드 스타일
def send_email(sender_email, receiver_email, app_password, subject, text, html):
    message = MIMEMultipart("alternative")
    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")
```

#### 상수명
- **UPPER_CASE** 사용 (환경 변수, 설정 값)
```python
# ✅ 현재 코드 스타일
GMAIL_SENDER_EMAIL = os.getenv("GMAIL_SENDER_EMAIL")
SMTP_PORT = 465  # 추가 상수 예시
SMTP_SERVER = "smtp.gmail.com"
```

#### 모듈 변수
- **__변수명__** 형태 (매직 변수)
```python
# ✅ 현재 코드 스타일
__author__ = "whatwant"
__version__ = "0.1.0"
__license__ = "BEER-WARE"
```

### 코딩 스타일

#### 들여쓰기 & 줄 길이
- **4 spaces** 들여쓰기
- **최대 88자** 줄 길이
- 긴 줄은 자연스럽게 나누기

```python
# ✅ 현재 코드 스타일
if not all([sender_email, receiver_email, app_password]):
    raise ValueError("다음 환경 변수들을 설정해주세요: GMAIL_SENDER_EMAIL, GMAIL_RECEIVER_EMAIL, GMAIL_APP_PASSWORD")
```

#### Import 순서 (현재 코드 분석)
1. 표준 라이브러리
2. 외부 라이브러리
3. 조건부 import (try/except 블록)

```python
# ✅ 현재 코드의 import 패턴
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# 조건부 import
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass
```

#### 문자열 & 주석 스타일
- **Double quotes** 사용
- 한글 주석 허용 (실용적 접근)
- F-string 사용

```python
# ✅ 현재 코드 스타일
subject = "This is a lucky email from Python"
html = f"<html><body><p>{text}</p></body></html>"
# .env 파일이 있으면 로드 (python-dotenv가 설치된 경우)
```

## Ruff 도구 사용법

### 설치 및 기본 사용법
```bash
# 개발 도구 설치
uv sync --dev

# 코드 검사
uv run ruff check .

# 자동 수정 가능한 문제 수정
uv run ruff check --fix .

# 코드 포맷팅
uv run ruff format .
```

### 통합 검사 (권장)
```bash
# 포맷팅 + 린팅 한 번에
uv run ruff format . && uv run ruff check --fix .

# 타입 검사 추가
uv run mypy .
```

## 프로젝트별 규칙

### 허용하는 것들
- `print()` 사용 (간단한 스크립트이므로)
- 한글 주석 및 문자열
- 타입 힌트 없는 함수 (점진적 적용)
- 88자 줄 길이 (Black 호환)

### 금지하는 것들
- 탭 들여쓰기 (spaces만 사용)
- 불필요한 import
- 사용하지 않는 변수
- 복잡도 10 이상인 함수

## VS Code 설정

`.vscode/settings.json`에 추가:
```json
{
    "python.defaultFormatter": "charliermarsh.ruff",
    "python.linting.enabled": true,
    "python.linting.ruffEnabled": true,
    "[python]": {
        "editor.defaultFormatter": "charliermarsh.ruff",
        "editor.codeActionsOnSave": {
            "source.organizeImports.ruff": true,
            "source.fixAll.ruff": true
        },
        "editor.formatOnSave": true
    }
}
```

## 자동화 스크립트

### 코드 수정 (fix_code_style.sh)
```bash
#!/bin/bash
echo "🔧 코드 자동 수정 시작..."
uv sync --dev
uv run ruff format .
uv run ruff check --fix .
echo "✅ 코드 수정 완료"
```

### 코드 검사 (check_code_quality.sh)
```bash
#!/bin/bash
echo "🔍 코드 품질 검사 시작..."
uv sync --dev
uv run ruff check .
uv run ruff format --check .
uv run mypy .
echo "✅ 모든 검사 통과"
```

## 커밋 전 체크리스트

1. ✅ `uv run ruff format .` - 코드 포맷팅
2. ✅ `uv run ruff check --fix .` - 자동 수정 가능한 문제 해결
3. ✅ `uv run ruff check .` - 모든 규칙 검사 통과
4. ✅ `uv run mypy .` - 타입 검사 (경고만 확인)
5. ✅ 의미있는 변수명과 함수명 사용
6. ✅ 적절한 주석 작성

## 예외 및 특별 규칙

- **환경 변수명**: `GMAIL_SENDER_EMAIL` 형태의 UPPER_CASE 유지
- **외부 라이브러리 클래스**: `MIMEText`, `MIMEMultipart` 등 원래 이름 유지
- **매직 메소드**: `__main__`, `__author__` 등 Python 표준 따름
- **간단한 스크립트**: 과도한 타입 힌트보다는 가독성 우선

## 점진적 개선 계획

1. **1단계**: Ruff로 기본 스타일 통일
2. **2단계**: 중요 함수부터 타입 힌트 추가
3. **3단계**: Docstring 추가
4. **4단계**: 테스트 코드 작성

이 가이드는 현재 코드의 실제 스타일을 반영하여 작성되었으며, 실용적인 접근을 통해 점진적으로 코드 품질을 개선하는 것을 목표로 합니다.
