#!/usr/bin/env python3
"""
Google News URL에서 실제 블로그 URL 추출 테스트
"""

import requests
from bs4 import BeautifulSoup


def extract_real_url_from_google_news(google_news_url: str) -> str:
    """Google News URL에서 실제 블로그 URL 추출"""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

        print(f"\n원본 URL: {google_news_url[:100]}...")

        # Google News 페이지에 접근
        response = requests.get(google_news_url, headers=headers, timeout=10, allow_redirects=True)

        print(f"리다이렉트 후 URL: {response.url[:100]}...")

        # HTML 파싱
        soup = BeautifulSoup(response.content, "html.parser")

        # 실제 기사 링크 찾기
        links = soup.find_all("a", href=True)
        for link in links[:5]:
            href = link.get("href", "")
            print(f"발견한 링크: {href[:100]}")

        return response.url

    except Exception as e:
        print(f"오류: {e}")
        return google_news_url


# 테스트
test_url = "https://news.google.com/rss/articles/CBMiS0FVX3lxTE1IRnhyYnhuZG10UmdjbDE4VjM3ODNnN3RlQVQ4dFhaT0w3Q3RpT3RTdzBnR01iRmZZNjlpWERUbE95b1Myc2FpRG9BYw?oc=5"

print("Google News URL 추출 테스트")
print("=" * 80)
result = extract_real_url_from_google_news(test_url)
print(f"\n최종 URL: {result}")
