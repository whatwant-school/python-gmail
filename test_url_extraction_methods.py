#!/usr/bin/env python3
"""
Google News URL에서 실제 블로그 URL 추출 방법 테스트
"""

import requests
from bs4 import BeautifulSoup
import re


def method1_direct_request(google_url: str) -> str:
    """방법 1: 직접 요청 후 최종 URL 확인"""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        response = requests.get(google_url, headers=headers, timeout=10, allow_redirects=True)
        return response.url
    except Exception as e:
        print(f"방법 1 오류: {e}")
        return None


def method2_parse_html(google_url: str) -> str:
    """방법 2: HTML 파싱하여 실제 링크 찾기"""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.get(google_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, "html.parser")

        # 메타 태그에서 찾기
        meta_refresh = soup.find("meta", attrs={"http-equiv": "refresh"})
        if meta_refresh:
            content = meta_refresh.get("content", "")
            url_match = re.search(r'url=(.*)', content)
            if url_match:
                return url_match.group(1)

        # 링크에서 찾기
        for link in soup.find_all("a", href=True):
            href = link.get("href", "")
            if any(blog in href for blog in ["tistory.com", "blog.naver.com", "brunch.co.kr"]):
                return href

        return None
    except Exception as e:
        print(f"방법 2 오류: {e}")
        return None


def method3_google_news_api(google_url: str) -> str:
    """방법 3: Google News URL 디코딩"""
    try:
        # Google News URL에서 실제 URL 추출 시도
        # URL 패턴: /articles/BASE64_ENCODED_DATA

        # 기사 ID 추출
        match = re.search(r'/articles/([^?]+)', google_url)
        if not match:
            return None

        article_id = match.group(1)

        # Google News의 실제 기사 페이지로 이동
        news_page_url = f"https://news.google.com/articles/{article_id}"

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

        response = requests.get(news_page_url, headers=headers, timeout=10, allow_redirects=True)

        # JavaScript에서 URL 찾기
        content = response.text

        # 패턴 1: "url":"actual_url" 찾기
        url_matches = re.findall(r'"url":"([^"]+)"', content)
        for url in url_matches:
            if any(blog in url for blog in ["tistory.com", "blog.naver.com", "brunch.co.kr"]):
                # 유니코드 이스케이프 처리
                url = url.replace(r'\u003d', '=').replace(r'\u0026', '&')
                return url

        return None
    except Exception as e:
        print(f"방법 3 오류: {e}")
        return None


def method4_selenium_alternative(google_url: str) -> str:
    """방법 4: 페이지 소스에서 링크 패턴 찾기"""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "ko-KR,ko;q=0.9,en;q=0.8",
        }

        response = requests.get(google_url, headers=headers, timeout=10)
        content = response.text

        # 여러 URL 패턴 시도
        patterns = [
            r'https?://[^"\'>\s]+\.tistory\.com[^"\'>\s]*',
            r'https?://blog\.naver\.com/[^"\'>\s]+',
            r'https?://brunch\.co\.kr/[^"\'>\s]+',
        ]

        for pattern in patterns:
            matches = re.findall(pattern, content)
            if matches:
                # 가장 길고 구체적인 URL 선택
                best_match = max(matches, key=len)
                # HTML 엔티티 디코딩
                best_match = best_match.replace('&amp;', '&')
                return best_match

        return None
    except Exception as e:
        print(f"방법 4 오류: {e}")
        return None


# 테스트
test_urls = [
    "https://news.google.com/rss/articles/CBMie0FVX3lxTE00RHBoVEJlUjVybDRObU9ORjBnc1hqdWRMamRWQTh3V3pTWHJRUlpBeElQYlVQUWJmcWRqendscTI3aS05ZlA3Zy1LYkNTVU11Yy1NZEtiQU9mTERqN1NGVzN2WnZZcGE2a29pR0lYRklrR0pLcDA1X2Rhbw?oc=5",
]

print("=" * 80)
print("Google News URL에서 실제 블로그 URL 추출 테스트")
print("=" * 80)

for i, test_url in enumerate(test_urls, 1):
    print(f"\n테스트 {i}")
    print(f"원본 URL: {test_url[:80]}...")
    print("-" * 80)

    result = method1_direct_request(test_url)
    print(f"방법 1 (직접 요청): {result[:100] if result else 'None'}...")

    result = method2_parse_html(test_url)
    print(f"방법 2 (HTML 파싱): {result[:100] if result else 'None'}...")

    result = method3_google_news_api(test_url)
    print(f"방법 3 (Google News API): {result[:100] if result else 'None'}...")

    result = method4_selenium_alternative(test_url)
    print(f"방법 4 (페이지 소스 파싱): {result[:100] if result else 'None'}...")

print("\n" + "=" * 80)
