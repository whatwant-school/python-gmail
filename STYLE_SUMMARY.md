# 코딩 스타일 요약 - 현재 코드 기준

## 🎯 적용된 스타일 분석

### 네이밍 규칙
```python
# ✅ 현재 코드에서 발견된 패턴들

# 함수명: snake_case
def send_email(sender_email, receiver_email, app_password, subject, text, html):

# 변수명: snake_case
sender_email = os.getenv("GMAIL_SENDER_EMAIL")
part1 = MIMEText(text, "plain")
part2 = MIMEText(html, "html")

# 상수: UPPER_CASE (환경 변수)
GMAIL_SENDER_EMAIL
GMAIL_RECEIVER_EMAIL
GMAIL_APP_PASSWORD

# 모듈 변수: __name__ 형태
__author__ = "whatwant"
__version__ = "0.1.0"
__license__ = "BEER-WARE"
```

### 코드 구조
```python
# ✅ 현재 적용된 구조

# 1. Shebang + 모듈 docstring
#!/usr/bin/env python3
"""
Send email via Gmail SMTP
"""

# 2. 모듈 변수
__author__ = "whatwant"

# 3. Import (표준 라이브러리 먼저)
import smtplib
import os
from email.mime.text import MIMEText

# 4. 조건부 import
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # 한글 주석 허용

# 5. 함수 정의
def send_email(...):

# 6. 메인 실행부
if __name__ == "__main__":
```

### 포맷팅 스타일
- **줄 길이**: 88자 (현재 긴 줄 자연스럽게 유지)
- **들여쓰기**: 4 spaces
- **문자열**: Double quotes 선호
- **주석**: 한글 허용 (실용적 접근)

## 🔧 Ruff 설정 완료

### 적용된 도구
```bash
# 설치된 도구
uv add --dev ruff mypy

# 사용법
uv run ruff format .      # 포맷팅
uv run ruff check --fix . # 린팅 + 자동수정
uv run ruff check .       # 검사만
uv run mypy .            # 타입 검사
```

### 자동화 스크립트
```bash
./fix_code_style.sh      # 자동 수정
./check_code_quality.sh  # 품질 검사
```

## 📋 현재 코드 품질 상태

✅ **완료된 사항**
- Ruff 린터/포맷터 설정 완료
- 현재 코드 스타일 분석 및 반영
- EditorConfig 설정
- VS Code 통합 설정
- 자동화 스크립트 작성

⚠️ **향후 개선 계획**
- 함수 타입 힌트 점진적 추가
- Docstring 추가
- 테스트 코드 작성

## 🎨 스타일 철학

1. **실용주의**: 현재 코드를 급격히 바꾸지 않음
2. **점진적 개선**: 타입 힌트 등은 천천히 추가
3. **도구 통합**: Ruff로 여러 도구 기능 통합
4. **한글 친화**: 주석과 문자열에 한글 허용
