#!/bin/bash

# Python Gmail Project - 코드 자동 수정 스크립트
# Ruff를 사용한 통합 포맷팅 및 린팅

echo "🔧 Python Gmail 프로젝트 코드 자동 수정 시작..."
echo

# 개발 도구 설치 확인
echo "📦 개발 도구 설치 확인..."
uv sync --dev
echo

# Ruff 포맷팅 적용
echo "⚡ Ruff 코드 포맷팅 적용..."
uv run ruff format .
echo "✅ 코드 포맷팅 완료"
echo

# Ruff 자동 수정 가능한 린팅 문제 해결
echo "🔧 Ruff 자동 수정 적용..."
uv run ruff check --fix .
echo "✅ 자동 수정 완료"
echo

# 최종 확인
echo "🔍 수정 결과 확인..."
if uv run ruff check .; then
    echo "✅ Ruff 검사 통과"
else
    echo "⚠️  일부 수정이 필요한 문제가 있습니다. 수동으로 확인해 주세요."
fi

echo
echo "✨ 코드 자동 수정이 완료되었습니다!"
echo "💡 'git diff'로 변경사항을 확인해 보세요."
