#!/usr/bin/env python3
"""
RSS 피드 내용 직접 확인
"""

import requests
import urllib.parse


def check_rss_feed():
    """RSS 피드 내용 확인"""
    keyword = "파이썬"
    search_query = f"{keyword} -광고 -홍보"
    encoded_query = urllib.parse.quote(search_query)

    # Google Blogs RSS 검색
    rss_url = f"https://news.google.com/rss/search?q={encoded_query}+when:1d+site:tistory.com+OR+site:blog.naver.com+OR+site:brunch.co.kr&hl=ko&gl=KR&ceid=KR:ko"

    print("RSS URL:")
    print(rss_url)
    print("\n" + "=" * 80)

    # RSS2JSON API 사용
    encoded_rss_url = urllib.parse.quote(rss_url, safe="")
    api_url = f"https://api.rss2json.com/v1/api.json?rss_url={encoded_rss_url}"

    print("\nAPI URL:")
    print(api_url[:200] + "...")
    print("\n" + "=" * 80)

    response = requests.get(api_url, timeout=10)
    data = response.json()

    print(f"\nStatus: {data.get('status')}")
    print(f"Feed Title: {data.get('feed', {}).get('title')}")
    print(f"Items Count: {len(data.get('items', []))}")

    print("\n" + "=" * 80)
    print("첫 번째 아이템 상세:")
    print("=" * 80)

    if data.get('items'):
        item = data['items'][0]
        print(f"\nTitle: {item.get('title')}")
        print(f"\nLink: {item.get('link')}")
        print(f"\nPubDate: {item.get('pubDate')}")
        print(f"\nDescription (처음 200자):")
        print(item.get('description', '')[:200])
        print(f"\nSource: {item.get('source')}")

        # 모든 필드 출력
        print("\n모든 필드:")
        for key, value in item.items():
            if isinstance(value, str) and len(value) > 100:
                print(f"  {key}: {value[:100]}...")
            else:
                print(f"  {key}: {value}")


if __name__ == "__main__":
    check_rss_feed()
