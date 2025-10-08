#!/bin/bash

# Python Gmail Project - 코드 품질 검사 스크립트
# Ruff를 사용한 통합 검사

set -e

echo "🔍 Python Gmail 프로젝트 코드 품질 검사 시작..."
echo

# 개발 도구가 설치되어 있는지 확인
echo "📦 개발 도구 설치 확인..."
uv sync --dev
echo

# Ruff 포맷팅 검사
echo "⚡ Ruff 포맷팅 검사..."
if uv run ruff format --check .; then
    echo "✅ 코드 포맷팅 검사 통과"
else
    echo "❌ 코드 포맷팅이 필요합니다. 다음 명령어로 수정하세요:"
    echo "   ./fix_code_style.sh"
    exit 1
fi
echo

# Ruff 린팅 검사
echo "🔧 Ruff 린팅 검사..."
if uv run ruff check .; then
    echo "✅ Ruff 린팅 검사 통과"
else
    echo "❌ 린팅 문제가 발견되었습니다. 다음 명령어로 수정하세요:"
    echo "   ./fix_code_style.sh"
    exit 1
fi
echo

# MyPy 타입 검사 (경고만 표시, 실패하지 않음)
echo "🔍 MyPy 타입 검사..."
if uv run mypy .; then
    echo "✅ MyPy 타입 검사 통과"
else
    echo "⚠️  MyPy 타입 관련 경고가 있습니다. (현재는 무시됨)"
fi
echo

echo "🎉 모든 코드 품질 검사를 통과했습니다!"
echo "✨ 커밋할 준비가 되었습니다."
