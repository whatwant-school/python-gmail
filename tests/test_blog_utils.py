"""
Tests for blog_utils module
"""

from datetime import datetime

from module.blog_utils import (
    _calculate_similarity,
    _clean_description,
    _extract_blog_source,
    _generate_summary,
    _is_ad_or_promotional,
    _is_similar_title,
    _normalize_title,
    _parse_pub_date,
    format_blog_info_html,
    format_blog_info_text,
    search_blogs_by_keyword,
)


def test_search_blogs_by_keyword():
    """블로그 검색 기본 기능 테스트"""
    keyword = "파이썬"
    results = search_blogs_by_keyword(keyword, max_results=3, hours_back=24)

    # 결과가 리스트인지 확인
    assert isinstance(results, list)

    # 최대 결과 수 확인
    assert len(results) <= 3

    # 각 결과가 필요한 필드를 가지고 있는지 확인
    for result in results:
        assert "title" in result
        assert "summary" in result
        assert "source" in result
        assert "link" in result
        assert "pub_date" in result


def test_parse_pub_date():
    """날짜 파싱 테스트"""
    # RSS 표준 형식
    date_str = "Mon, 15 Jan 2024 10:30:00 GMT"
    parsed_date = _parse_pub_date(date_str)
    assert parsed_date is not None
    assert isinstance(parsed_date, datetime)

    # ISO 8601 형식
    date_str = "2024-01-15T10:30:00+0900"
    parsed_date = _parse_pub_date(date_str)
    assert parsed_date is not None

    # 잘못된 형식
    date_str = "invalid date"
    parsed_date = _parse_pub_date(date_str)
    assert parsed_date is None


def test_is_similar_title():
    """제목 유사도 테스트"""
    seen_titles = {"파이썬 프로그래밍 기초"}

    # 유사한 제목
    similar_title = "파이썬 프로그래밍 기초 강좌"
    assert _is_similar_title(similar_title, seen_titles) is True

    # 다른 제목
    different_title = "자바스크립트 기초"
    assert _is_similar_title(different_title, seen_titles) is False


def test_normalize_title():
    """제목 정규화 테스트"""
    title = "  파이썬 프로그래밍!!! 기초  "
    normalized = _normalize_title(title)

    assert "파이썬" in normalized
    assert "프로그래밍" in normalized
    assert "기초" in normalized
    assert "!" not in normalized
    assert normalized == normalized.strip()


def test_calculate_similarity():
    """문자열 유사도 계산 테스트"""
    str1 = "파이썬 프로그래밍 기초"
    str2 = "파이썬 프로그래밍 고급"

    similarity = _calculate_similarity(str1, str2)
    assert 0.0 <= similarity <= 1.0
    assert similarity >= 0.5  # 일부 단어가 겹침

    # 완전히 같은 문자열
    similarity = _calculate_similarity(str1, str1)
    assert similarity == 1.0

    # 완전히 다른 문자열
    str3 = "자바 웹 개발"
    similarity = _calculate_similarity(str1, str3)
    assert similarity < 0.3


def test_is_ad_or_promotional():
    """광고/홍보 글 필터링 테스트"""
    # 광고 글
    ad_title = "[광고] 특별 할인 이벤트"
    ad_description = "마케팅 프로모션 진행 중"
    assert _is_ad_or_promotional(ad_title, ad_description) is True

    # 일반 글
    normal_title = "파이썬 학습 방법"
    normal_description = "파이썬을 배우는 효과적인 방법"
    assert _is_ad_or_promotional(normal_title, normal_description) is False


def test_clean_description():
    """설명 정제 테스트"""
    # HTML 태그 제거 (충분한 길이의 텍스트)
    html_desc = "<p>파이썬 프로그래밍은 매우 유용한 기술입니다. 많은 사람들이 배우고 있습니다.</p> <a>링크</a>"
    cleaned = _clean_description(html_desc)
    assert "<" not in cleaned
    assert ">" not in cleaned
    assert "파이썬" in cleaned

    # 연속 공백 제거
    space_desc = (
        "파이썬 프로그래밍 기초를 배우는 것은 중요합니다. 체계적으로 학습하세요."
    )
    cleaned = _clean_description(space_desc)
    assert "    " not in cleaned

    # 빈 설명
    empty_desc = ""
    cleaned = _clean_description(empty_desc)
    assert cleaned == "요약 정보 없음"


def test_extract_blog_source():
    """블로그 출처 추출 테스트"""
    # 티스토리
    tistory_link = "https://myblog.tistory.com/123"
    source = _extract_blog_source(tistory_link)
    assert "티스토리" in source
    assert "myblog" in source

    # 네이버 블로그
    naver_link = "https://blog.naver.com/testuser/123456"
    source = _extract_blog_source(naver_link)
    assert "네이버" in source or "testuser" in source

    # 브런치
    brunch_link = "https://brunch.co.kr/@writer123/45"
    source = _extract_blog_source(brunch_link)
    assert "브런치" in source

    # 알 수 없는 블로그
    unknown_link = ""
    source = _extract_blog_source(unknown_link)
    assert source == "블로그"


def test_generate_summary():
    """요약 생성 테스트"""
    title = "파이썬 프로그래밍 기초"
    content = "파이썬은 배우기 쉬운 프로그래밍 언어입니다. 다양한 분야에서 활용됩니다. 웹 개발, 데이터 분석, 인공지능 등에 사용됩니다."
    description = "파이썬 학습 가이드"

    summary = _generate_summary(title, content, description)

    assert summary is not None
    assert len(summary) > 0
    assert len(summary) <= 200

    # 내용이 없는 경우
    empty_summary = _generate_summary("제목", "", "")
    assert "블로그 본문에서 상세 내용을 확인하세요" in empty_summary


def test_format_blog_info_text():
    """텍스트 포맷팅 테스트"""
    blog_list = [
        {
            "title": "파이썬 기초",
            "summary": "파이썬 학습 방법",
            "source": "개발자 블로그",
            "link": "https://example.com/1",
            "pub_date": "2024-01-15 10:30",
        }
    ]

    keyword = "파이썬"
    formatted = format_blog_info_text(blog_list, keyword)

    assert keyword in formatted
    assert "파이썬 기초" in formatted
    assert "파이썬 학습 방법" in formatted
    assert "개발자 블로그" in formatted

    # 빈 리스트
    empty_formatted = format_blog_info_text([], keyword)
    assert "검색 결과가 없습니다" in empty_formatted


def test_format_blog_info_html():
    """HTML 포맷팅 테스트"""
    blog_list = [
        {
            "title": "파이썬 기초",
            "summary": "파이썬 학습 방법",
            "source": "개발자 블로그",
            "link": "https://example.com/1",
            "pub_date": "2024-01-15 10:30",
        }
    ]

    keyword = "파이썬"
    formatted = format_blog_info_html(blog_list, keyword)

    assert "<h3>" in formatted
    assert keyword in formatted
    assert "파이썬 기초" in formatted
    assert "파이썬 학습 방법" in formatted
    assert "개발자 블로그" in formatted
    assert "<a href=" in formatted

    # 빈 리스트
    empty_formatted = format_blog_info_html([], keyword)
    assert "검색 결과가 없습니다" in empty_formatted
    assert "<h3>" in empty_formatted
