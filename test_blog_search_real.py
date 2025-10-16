#!/usr/bin/env python3
"""
실제 블로그 검색 테스트 스크립트
"""

from module.blog_utils import (
    search_blogs_by_keyword,
    format_blog_info_text,
    format_blog_info_html,
)


def test_real_blog_search():
    """실제 웹에서 블로그 검색 테스트"""
    print("=" * 80)
    print("실제 블로그 검색 테스트 시작")
    print("=" * 80)

    # 테스트 키워드들
    test_keywords = [
        "파이썬",
        "개발자",
        "프로그래밍",
    ]

    for keyword in test_keywords:
        print(f"\n{'=' * 80}")
        print(f"키워드: '{keyword}' 검색 중...")
        print(f"{'=' * 80}")

        try:
            # 블로그 검색 (최대 3개, 최근 24시간)
            results = search_blogs_by_keyword(keyword, max_results=3, hours_back=24)

            print(f"\n검색 결과: {len(results)}건\n")

            if results:
                # 각 결과 출력
                for i, blog in enumerate(results, 1):
                    print(f"\n[블로그 {i}]")
                    print(f"제목: {blog.get('title', 'N/A')}")
                    print(f"요약: {blog.get('summary', 'N/A')[:100]}...")
                    print(f"출처: {blog.get('source', 'N/A')}")
                    print(f"등록: {blog.get('pub_date', 'N/A')}")
                    print(f"링크: {blog.get('link', 'N/A')[:80]}...")
                    print("-" * 80)

                # 텍스트 포맷 테스트
                print(f"\n{'=' * 80}")
                print("텍스트 포맷 결과:")
                print(f"{'=' * 80}")
                text_formatted = format_blog_info_text(results, keyword)
                print(text_formatted)

                # HTML 포맷 테스트
                print(f"\n{'=' * 80}")
                print("HTML 포맷 결과 (일부):")
                print(f"{'=' * 80}")
                html_formatted = format_blog_info_html(results, keyword)
                print(html_formatted[:500] + "..." if len(html_formatted) > 500 else html_formatted)

            else:
                print("⚠️  검색 결과가 없습니다.")

        except Exception as e:
            print(f"❌ 오류 발생: {e}")
            import traceback
            traceback.print_exc()

    print(f"\n{'=' * 80}")
    print("테스트 완료!")
    print(f"{'=' * 80}")


if __name__ == "__main__":
    test_real_blog_search()
