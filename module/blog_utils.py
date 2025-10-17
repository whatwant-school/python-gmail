"""
Blog utility functions for searching latest blog posts by keyword
"""

import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import requests


def search_blogs_by_keyword(
    keyword: str, max_results: int = 5, hours_back: int = 24
) -> List[Dict[str, Any]]:
    """
    키워드를 기반으로 최근 블로그 글을 검색합니다. (Naver API 사용)

    Args:
        keyword (str): 검색할 키워드
        max_results (int): 최대 결과 수 (3-5개 권장, 최대 100)
        hours_back (int): 검색할 시간 범위 (시간 단위, 기본 24시간)

    Returns:
        List[Dict[str, Any]]: 블로그 글 목록

    Environment Variables:
        NAVER_CLIENT_ID: Naver API Client ID
        NAVER_CLIENT_SECRET: Naver API Client Secret
    """
    try:
        # 환경변수에서 Naver API 인증 정보 가져오기
        client_id = os.getenv("NAVER_CLIENT_ID")
        client_secret = os.getenv("NAVER_CLIENT_SECRET")

        if not client_id or not client_secret:
            print(
                "경고: NAVER_CLIENT_ID 또는 NAVER_CLIENT_SECRET 환경변수가 설정되지 않았습니다."
            )
            return _fallback_blog_search(keyword, max_results)

        # Naver 블로그 검색 API 호출
        import urllib.parse

        # 키워드를 공백으로 분리
        keywords = keyword.strip().split()
        all_articles = []

        if len(keywords) > 1:
            # 여러 키워드인 경우 각각 개별 검색 후 합치기
            for kw in keywords:
                search_query = f"{kw} -광고 -홍보"
                encoded_query = urllib.parse.quote(search_query)
                api_url = f"https://openapi.naver.com/v1/search/blog.json?query={encoded_query}&display={min(max_results * 3, 100)}&sort=date"

                headers = {
                    "X-Naver-Client-Id": client_id,
                    "X-Naver-Client-Secret": client_secret,
                }

                response = requests.get(api_url, headers=headers, timeout=10)

                if response.status_code == 200:
                    data = response.json()
                    all_articles.extend(data.get("items", []))
        else:
            # 단일 키워드인 경우 그대로 사용
            search_query = f"{keyword} -광고 -홍보"
            encoded_query = urllib.parse.quote(search_query)
            api_url = f"https://openapi.naver.com/v1/search/blog.json?query={encoded_query}&display={min(max_results * 2, 100)}&sort=date"

            headers = {
                "X-Naver-Client-Id": client_id,
                "X-Naver-Client-Secret": client_secret,
            }

            response = requests.get(api_url, headers=headers, timeout=10)

            if response.status_code != 200:
                print(f"Naver API 오류: {response.status_code}")
                print(f"응답 내용: {response.text[:200]}")
                return _fallback_blog_search(keyword, max_results)

            data = response.json()
            all_articles = data.get("items", [])

        articles = all_articles

        if not articles:
            return _fallback_blog_search(keyword, max_results)

        if not articles:
            return _fallback_blog_search(keyword, max_results)

        # 시간 필터링 및 중복 제거
        # timezone aware로 변경 (한국 시간 기준)
        from datetime import timezone

        # KST (UTC+9) 기준으로 현재 시간 계산
        kst = timezone(timedelta(hours=9))
        cutoff_time = datetime.now(kst) - timedelta(hours=hours_back)
        filtered_blogs = []
        seen_titles = set()

        for article in articles:
            # 제목 중복 체크 (유사한 글 제외)
            title = article.get("title", "")
            # HTML 태그 제거
            title = _remove_html_tags(title)

            if not title or _is_similar_title(title, seen_titles):
                continue

            # 광고/홍보 글 필터링
            description = article.get("description", "")
            description = _remove_html_tags(description)

            if _is_ad_or_promotional(title, description):
                continue

            # 발행 시간 파싱 (Naver API는 "YYYYMMDD" 형식)
            pub_date = _parse_pub_date(article.get("postdate", ""))
            if pub_date and pub_date < cutoff_time:
                continue

            # 블로그 정보 구성
            link = article.get("link", "")

            # 블로그 출처 추출
            source = _extract_blog_source(
                link, article.get("bloggername", ""), article.get("bloggerlink", "")
            )

            # 요약 생성
            summary = (
                _clean_description(description) if description else "요약 정보 없음"
            )

            blog_item = {
                "title": title,
                "summary": summary,
                "source": source,
                "link": link,
                "pub_date": pub_date.strftime("%Y-%m-%d %H:%M")
                if pub_date
                else "시간 정보 없음",
                "pub_date_raw": pub_date,
            }

            filtered_blogs.append(blog_item)
            seen_titles.add(_normalize_title(title))

            if len(filtered_blogs) >= max_results:
                break

        # 발행 시간 순으로 정렬 (최신순)
        filtered_blogs.sort(
            key=lambda x: x.get("pub_date_raw") or datetime.min, reverse=True
        )

        # 최종 결과에서 raw 시간 정보 제거
        for blog in filtered_blogs:
            blog.pop("pub_date_raw", None)

        return filtered_blogs[:max_results]

    except Exception as e:
        print(f"블로그 검색 중 오류 발생: {e}")
        return _fallback_blog_search(keyword, max_results)


def _remove_html_tags(text: str) -> str:
    """
    HTML 태그와 엔티티를 제거합니다.

    Args:
        text (str): HTML이 포함된 텍스트

    Returns:
        str: HTML 태그가 제거된 텍스트
    """
    import html
    import re

    if not text:
        return ""

    # HTML 엔티티 디코드 (&lt;, &gt;, &quot; 등)
    text = html.unescape(text)

    # HTML 태그 제거
    text = re.sub(r"<[^>]+>", "", text)

    # 연속된 공백 정리
    text = re.sub(r"\s+", " ", text).strip()

    return text


def _fallback_blog_search(keyword: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """
    주 API가 실패했을 때 사용할 대체 블로그 검색 방법

    Args:
        keyword (str): 검색할 키워드
        max_results (int): 최대 결과 수

    Returns:
        List[Dict[str, Any]]: 블로그 글 목록
    """
    # 모든 방법이 실패한 경우
    return [
        {
            "title": f"{keyword} 블로그 검색 실패",
            "summary": "네트워크 문제나 API 서비스 장애로 블로그 글을 가져올 수 없습니다.",
            "source": "시스템 오류",
            "link": "",
            "pub_date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }
    ]


def _parse_pub_date(date_str: str) -> Optional[datetime]:
    """
    다양한 형식의 날짜 문자열을 datetime 객체로 변환

    Args:
        date_str (str): 날짜 문자열 (Naver API는 "YYYYMMDD" 형식)

    Returns:
        Optional[datetime]: 파싱된 datetime 객체 또는 None
    """
    if not date_str:
        return None

    # 다양한 날짜 형식 지원
    formats = [
        "%Y%m%d",  # Naver API 형식 (YYYYMMDD)
        "%a, %d %b %Y %H:%M:%S %Z",  # RSS 표준 형식
        "%a, %d %b %Y %H:%M:%S %z",  # RFC 2822
        "%Y-%m-%dT%H:%M:%S%z",  # ISO 8601
        "%Y-%m-%d %H:%M:%S",  # 일반적인 형식
        "%Y-%m-%d",  # 날짜만
    ]

    for fmt in formats:
        try:
            parsed_date = datetime.strptime(date_str.strip(), fmt)
            # timezone이 없으면 KST 추가
            if parsed_date.tzinfo is None:
                from datetime import timezone

                kst = timezone(timedelta(hours=9))
                parsed_date = parsed_date.replace(tzinfo=kst)
            return parsed_date
        except ValueError:
            continue

    # 한국어 날짜 형식도 시도
    try:
        # "2024년 1월 15일" 형식 처리
        import re

        korean_date = re.search(r"(\d{4})년\s*(\d{1,2})월\s*(\d{1,2})일", date_str)
        if korean_date:
            year, month, day = korean_date.groups()
            from datetime import timezone

            kst = timezone(timedelta(hours=9))
            return datetime(int(year), int(month), int(day), tzinfo=kst)
    except Exception as e:
        import logging

        logging.warning(f"_parse_pub_date 예외: {e}")

    return None


def _is_similar_title(title: str, seen_titles: set) -> bool:
    """
    제목이 이미 본 제목들과 유사한지 확인

    Args:
        title (str): 확인할 제목
        seen_titles (set): 이미 본 제목들의 집합

    Returns:
        bool: 유사한 제목이 있으면 True
    """
    normalized_title = _normalize_title(title)

    for seen_title in seen_titles:
        # 50% 이상 겹치면 유사한 것으로 판단
        if _calculate_similarity(normalized_title, seen_title) > 0.5:
            return True

    return False


def _normalize_title(title: str) -> str:
    """
    제목을 정규화 (공백, 특수문자 제거)

    Args:
        title (str): 원본 제목

    Returns:
        str: 정규화된 제목
    """
    import re

    # 특수문자, 공백 제거하고 소문자로 변환
    normalized = re.sub(r"[^\w\s가-힣]", "", title)
    normalized = re.sub(r"\s+", " ", normalized).strip().lower()
    return normalized


def _calculate_similarity(str1: str, str2: str) -> float:
    """
    두 문자열의 유사도 계산 (Jaccard 유사도)

    Args:
        str1 (str): 첫 번째 문자열
        str2 (str): 두 번째 문자열

    Returns:
        float: 유사도 (0.0 ~ 1.0)
    """
    words1 = set(str1.split())
    words2 = set(str2.split())

    if not words1 and not words2:
        return 1.0

    intersection = words1.intersection(words2)
    union = words1.union(words2)

    return len(intersection) / len(union) if union else 0.0


def _is_ad_or_promotional(title: str, description: str) -> bool:
    """
    광고나 홍보성 글인지 확인

    Args:
        title (str): 글 제목
        description (str): 글 설명

    Returns:
        bool: 광고/홍보 글이면 True
    """
    # 제목과 설명을 합친 텍스트 (대소문자 구분 없이)
    combined = (title + " " + description).lower()

    # 명확한 광고성 표시만 체크 (제목이나 설명 앞부분에 표시된 경우)
    ad_keywords = [
        "[광고]",
        "(광고)",
        "[pr]",
        "(pr)",
        "[홍보]",
        "(홍보)",
        "제휴광고",
        "협찬광고",
    ]

    # 제목이나 설명의 시작 100자 이내에 광고 표시가 있는지 확인
    prefix = combined[:100]

    return any(keyword in prefix for keyword in ad_keywords)


def _clean_description(description: str) -> str:
    """
    글 설명에서 HTML 태그나 불필요한 내용 제거하고 실제 본문 요약 생성

    Args:
        description (str): 원본 설명

    Returns:
        str: 정제된 설명
    """
    import re

    if not description:
        return "요약 정보 없음"

    # HTML 태그 제거
    clean_desc = re.sub(r"<[^>]+>", "", description)

    # 연속된 공백 정리
    clean_desc = re.sub(r"\s+", " ", clean_desc).strip()

    # 블로그 출처 정보나 불필요한 메타 정보 제거
    clean_desc = re.sub(
        r"\s*-\s*[가-힣A-Za-z0-9]+(?:블로그|BLOG|Blog)?\s*$", "", clean_desc
    )

    # URL이나 도메인 정보 제거
    clean_desc = re.sub(r"https?://[^\s]+", "", clean_desc)
    clean_desc = re.sub(r"www\.[^\s]+", "", clean_desc)
    clean_desc = re.sub(
        r"[a-zA-Z0-9.-]+\.(com|net|co\.kr|org|tistory\.com|naver\.com)\b",
        "",
        clean_desc,
    )

    # 너무 짧은 설명
    if len(clean_desc.strip()) < 20:
        return "블로그 본문에서 상세 내용을 확인하세요"

    # 연속된 공백 다시 정리
    clean_desc = re.sub(r"\s+", " ", clean_desc).strip()

    # 너무 긴 설명은 잘라내기 (150자 제한)
    if len(clean_desc) > 150:
        sentences = clean_desc.split(". ")
        if len(sentences) > 1:
            clean_desc = sentences[0] + "."
            if len(clean_desc) > 150:
                clean_desc = clean_desc[:147] + "..."
        else:
            clean_desc = clean_desc[:147] + "..."

    return (
        clean_desc if clean_desc.strip() else "블로그 본문에서 상세 내용을 확인하세요"
    )


def _extract_blog_source(
    link: str, blogger_name: str = "", blogger_link: str = ""
) -> str:
    """
    블로그 출처 정보 추출

    Args:
        link (str): 블로그 링크
        blogger_name (str): 블로거 이름 (Naver API 제공)
        blogger_link (str): 블로거 링크 (Naver API 제공)

    Returns:
        str: 출처 이름
    """
    from urllib.parse import urlparse

    # 1. Naver API에서 제공하는 블로거 이름 사용
    if blogger_name:
        # 블로그 플랫폼 판별
        platform = ""
        if link:
            if "blog.naver.com" in link:
                platform = " (네이버 블로그)"
            elif "tistory.com" in link:
                platform = " (티스토리)"
            elif "brunch.co.kr" in link:
                platform = " (브런치)"

        return f"{blogger_name}{platform}"

    # 2. 링크에서 블로그 플랫폼 및 사용자 추출
    if link:
        try:
            parsed_url = urlparse(link)
            domain = parsed_url.netloc.lower()

            # 티스토리 블로그
            if "tistory.com" in domain:
                blog_name = domain.replace(".tistory.com", "").replace("www.", "")
                return f"{blog_name} (티스토리)"

            # 네이버 블로그
            if "blog.naver.com" in domain:
                path_parts = parsed_url.path.split("/")
                if len(path_parts) > 1:
                    blog_id = path_parts[1]
                    return f"{blog_id} (네이버 블로그)"
                return "네이버 블로그"

            # 브런치
            if "brunch.co.kr" in domain:
                path_parts = parsed_url.path.split("/")
                if len(path_parts) > 1 and path_parts[0] == "":
                    blog_id = path_parts[1].replace("@", "")
                    return f"@{blog_id} (브런치)"
                return "브런치"

            # 미디엄
            if "medium.com" in domain:
                path_parts = parsed_url.path.split("/")
                if len(path_parts) > 1 and path_parts[1].startswith("@"):
                    blog_id = path_parts[1]
                    return f"{blog_id} (미디엄)"
                return "미디엄"

            # 기타 블로그
            if any(
                keyword in domain
                for keyword in ["blog", "diary", "note", "post", "story"]
            ):
                return f"{domain.replace('www.', '')} (블로그)"

        except Exception as e:
            import logging

            logging.warning(f"_extract_blog_source 예외: {e}")

    return "블로그"


def format_blog_info_text(blog_list: List[Dict[str, Any]], keyword: str) -> str:
    """
    블로그 정보를 텍스트 형식으로 포맷팅합니다.

    Args:
        blog_list (List[Dict[str, Any]]): 블로그 글 목록
        keyword (str): 검색 키워드

    Returns:
        str: 포맷팅된 블로그 정보 텍스트
    """
    if not blog_list:
        return f"""
"{keyword}" 관련 최신 블로그:
- 검색 결과가 없습니다.
"""

    result = f"""
"{keyword}" 관련 최신 블로그 ({len(blog_list)}건):

"""

    for i, blog in enumerate(blog_list, 1):
        result += f"{i}. {blog.get('title', '제목 없음')}\n"
        result += f"   요약: {blog.get('summary', '요약 없음')}\n"
        result += f"   출처: {blog.get('source', '알 수 없음')}\n"
        result += f"   등록: {blog.get('pub_date', '시간 정보 없음')}\n"

        if blog.get("link"):
            result += f"   링크: {blog['link']}\n"

        result += "\n"

    return result


def format_blog_info_html(blog_list: List[Dict[str, Any]], keyword: str) -> str:
    """
    블로그 정보를 HTML 형식으로 포맷팅합니다.

    Args:
        blog_list (List[Dict[str, Any]]): 블로그 글 목록
        keyword (str): 검색 키워드

    Returns:
        str: 포맷팅된 블로그 정보 HTML
    """
    if not blog_list:
        return f"""
<h3>✍️ "{keyword}" 관련 최신 블로그</h3>
<p><em>검색 결과가 없습니다.</em></p>
"""

    result = f"""
<h3>✍️ "{keyword}" 관련 최신 블로그 ({len(blog_list)}건)</h3>
<div style="margin-left: 10px;">
"""

    for i, blog in enumerate(blog_list, 1):
        title = blog.get("title", "제목 없음")
        summary = blog.get("summary", "요약 없음")
        source = blog.get("source", "알 수 없음")
        pub_date = blog.get("pub_date", "시간 정보 없음")
        link = blog.get("link", "")

        result += f"""
<div style="margin-bottom: 15px; padding: 10px; border-left: 3px solid #28a745;">
    <h4 style="margin: 0 0 5px 0; color: #28a745;">
        {i}. {title}
    </h4>
    <p style="margin: 5px 0; color: #555; font-size: 14px;">
        📝 <strong>요약:</strong> {summary}
    </p>
    <p style="margin: 5px 0; color: #777; font-size: 12px;">
        ✍️ <strong>출처:</strong> {source} |
        🕒 <strong>등록:</strong> {pub_date}
    </p>
"""

        if link:
            result += f"""
    <p style="margin: 5px 0; font-size: 12px;">
        🔗 <a href="{link}" style="color: #28a745;">블로그 링크</a>
    </p>
"""

        result += "</div>\n"

    result += "</div>\n"

    return result
