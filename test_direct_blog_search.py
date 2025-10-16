#!/usr/bin/env python3
"""
블로그 플랫폼별 직접 검색 테스트
"""

import requests
import urllib.parse
from bs4 import BeautifulSoup
from datetime import datetime


def search_naver_blog(keyword: str, max_results: int = 3):
    """네이버 블로그 직접 검색"""
    print(f"\n{'=' * 80}")
    print(f"네이버 블로그 검색: {keyword}")
    print(f"{'=' * 80}")

    try:
        # 네이버 블로그 검색 API (비공식)
        search_url = f"https://s.search.naver.com/p/blog/search.naver"
        params = {
            "where": "blog",
            "query": keyword,
            "sort": "date",  # 최신순
            "start": 1,
        }

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

        response = requests.get(search_url, params=params, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, "html.parser")

        # 블로그 검색 결과 파싱
        results = []
        blog_items = soup.select(".api_subject_bx")[:max_results]

        for item in blog_items:
            title_elem = item.select_one(".api_txt_lines.total_tit")
            if title_elem:
                title = title_elem.get_text(strip=True)
                link = title_elem.get("href", "")

                desc_elem = item.select_one(".api_txt_lines.dsc_txt_wrap")
                description = desc_elem.get_text(strip=True) if desc_elem else ""

                results.append({
                    "title": title,
                    "link": link,
                    "description": description,
                    "source": "네이버 블로그"
                })

        print(f"검색 결과: {len(results)}건")
        for i, result in enumerate(results, 1):
            print(f"\n[{i}] {result['title']}")
            print(f"    링크: {result['link'][:80]}...")
            print(f"    설명: {result['description'][:100]}...")

        return results

    except Exception as e:
        print(f"오류: {e}")
        return []


def search_tistory_via_google(keyword: str, max_results: int = 3):
    """구글 검색으로 티스토리 블로그 찾기"""
    print(f"\n{'=' * 80}")
    print(f"티스토리 블로그 검색 (Google 경유): {keyword}")
    print(f"{'=' * 80}")

    try:
        # Google 검색 (site: 연산자 사용)
        search_query = f"{keyword} site:tistory.com"
        encoded_query = urllib.parse.quote(search_query)
        search_url = f"https://www.google.com/search?q={encoded_query}&tbs=qdr:d"  # 최근 1일

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

        response = requests.get(search_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, "html.parser")

        # 검색 결과 파싱
        results = []
        search_results = soup.select(".g")[:max_results]

        for item in search_results:
            title_elem = item.select_one("h3")
            link_elem = item.select_one("a")

            if title_elem and link_elem:
                title = title_elem.get_text(strip=True)
                link = link_elem.get("href", "")

                # 실제 티스토리 링크인지 확인
                if "tistory.com" in link:
                    desc_elem = item.select_one(".VwiC3b")
                    description = desc_elem.get_text(strip=True) if desc_elem else ""

                    results.append({
                        "title": title,
                        "link": link,
                        "description": description,
                        "source": "티스토리"
                    })

        print(f"검색 결과: {len(results)}건")
        for i, result in enumerate(results, 1):
            print(f"\n[{i}] {result['title']}")
            print(f"    링크: {result['link'][:80]}...")
            print(f"    설명: {result['description'][:100]}...")

        return results

    except Exception as e:
        print(f"오류: {e}")
        return []


def search_via_duckduckgo(keyword: str, site: str = "", max_results: int = 3):
    """DuckDuckGo를 통한 블로그 검색"""
    print(f"\n{'=' * 80}")
    print(f"DuckDuckGo 검색: {keyword} (site: {site})")
    print(f"{'=' * 80}")

    try:
        search_query = f"{keyword} {f'site:{site}' if site else ''}"
        params = {
            "q": search_query,
            "df": "d",  # 최근 1일
            "ia": "web"
        }

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

        response = requests.get("https://html.duckduckgo.com/html/", params=params, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, "html.parser")

        # 검색 결과 파싱
        results = []
        search_results = soup.select(".result")[:max_results]

        for item in search_results:
            title_elem = item.select_one(".result__title")
            link_elem = item.select_one(".result__url")

            if title_elem and link_elem:
                title = title_elem.get_text(strip=True)
                link = link_elem.get("href", "")

                desc_elem = item.select_one(".result__snippet")
                description = desc_elem.get_text(strip=True) if desc_elem else ""

                results.append({
                    "title": title,
                    "link": link,
                    "description": description,
                    "source": f"DuckDuckGo ({site if site else 'all'})"
                })

        print(f"검색 결과: {len(results)}건")
        for i, result in enumerate(results, 1):
            print(f"\n[{i}] {result['title']}")
            print(f"    링크: {result['link'][:80]}...")
            print(f"    설명: {result['description'][:100]}...")

        return results

    except Exception as e:
        print(f"오류: {e}")
        return []


# 테스트
keyword = "파이썬"

print("=" * 80)
print("블로그 플랫폼별 직접 검색 테스트")
print("=" * 80)

# 1. 네이버 블로그 검색
naver_results = search_naver_blog(keyword, max_results=3)

# 2. 티스토리 검색 (Google 경유)
tistory_results = search_tistory_via_google(keyword, max_results=3)

# 3. DuckDuckGo 검색
ddg_results = search_via_duckduckgo(keyword, site="tistory.com", max_results=3)

print("\n" + "=" * 80)
print("테스트 완료!")
print("=" * 80)
