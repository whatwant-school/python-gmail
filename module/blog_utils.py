"""
Blog utility functions for searching latest blog posts by keyword
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import requests
from bs4 import BeautifulSoup


def search_blogs_by_keyword(
    keyword: str, max_results: int = 5, hours_back: int = 24
) -> List[Dict[str, Any]]:
    """
    키워드를 기반으로 최근 블로그 글을 검색합니다.

    Args:
        keyword (str): 검색할 키워드
        max_results (int): 최대 결과 수 (3-5개 권장)
        hours_back (int): 검색할 시간 범위 (시간 단위, 기본 24시간)

    Returns:
        List[Dict[str, Any]]: 블로그 글 목록
    """
    try:
        # Google Blog Search RSS를 사용한 블로그 검색
        import urllib.parse

        search_query = f"{keyword} -광고 -홍보"  # 광고, 홍보 제외
        encoded_query = urllib.parse.quote(search_query)

        # Google Blogs RSS 검색 (티스토리, 네이버 블로그, 브런치)
        rss_url = f"https://news.google.com/rss/search?q={encoded_query}+when:1d+site:tistory.com+OR+site:blog.naver.com+OR+site:brunch.co.kr&hl=ko&gl=KR&ceid=KR:ko"

        # RSS2JSON API 사용 (무료 서비스)
        encoded_rss_url = urllib.parse.quote(rss_url, safe="")
        api_url = f"https://api.rss2json.com/v1/api.json?rss_url={encoded_rss_url}"

        response = requests.get(api_url, timeout=10)

        if response.status_code != 200:
            return _fallback_blog_search(keyword, max_results)

        data = response.json()

        if data.get("status") != "ok":
            return _fallback_blog_search(keyword, max_results)

        articles = data.get("items", [])

        # 시간 필터링 및 중복 제거
        cutoff_time = datetime.now() - timedelta(hours=hours_back)
        filtered_blogs = []
        seen_titles = set()

        for article in articles:
            # 제목 중복 체크 (유사한 글 제외)
            title = article.get("title", "")
            if not title or _is_similar_title(title, seen_titles):
                continue

            # 광고/홍보 글 필터링
            if _is_ad_or_promotional(title, article.get("description", "")):
                continue

            # 발행 시간 파싱
            pub_date = _parse_pub_date(article.get("pubDate", ""))
            if pub_date and pub_date < cutoff_time:
                continue

            # 블로그 정보 구성
            description = article.get("description", "")
            link = article.get("link", "")

            # 블로그 출처 추출
            source = _extract_blog_source(link, title, description)

            # 블로그 본문을 가져와서 개선된 요약 생성
            try:
                blog_content = _fetch_blog_content(link) if link else ""
                summary = _generate_summary(title, blog_content, description)
            except Exception:
                summary = _clean_description(description)

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
        date_str (str): 날짜 문자열

    Returns:
        Optional[datetime]: 파싱된 datetime 객체 또는 None
    """
    if not date_str:
        return None

    # 다양한 날짜 형식 지원
    formats = [
        "%a, %d %b %Y %H:%M:%S %Z",  # RSS 표준 형식
        "%a, %d %b %Y %H:%M:%S %z",  # RFC 2822
        "%Y-%m-%dT%H:%M:%S%z",  # ISO 8601
        "%Y-%m-%d %H:%M:%S",  # 일반적인 형식
        "%Y-%m-%d",  # 날짜만
    ]

    for fmt in formats:
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except ValueError:
            continue

    # 한국어 날짜 형식도 시도
    try:
        # "2024년 1월 15일" 형식 처리
        import re

        korean_date = re.search(r"(\d{4})년\s*(\d{1,2})월\s*(\d{1,2})일", date_str)
        if korean_date:
            year, month, day = korean_date.groups()
            return datetime(int(year), int(month), int(day))
    except Exception:
        pass

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
    content = (title + " " + description).lower()

    # 광고/홍보 관련 키워드
    ad_keywords = [
        "광고",
        "홍보",
        "협찬",
        "제휴",
        "할인",
        "이벤트",
        "프로모션",
        "마케팅",
        "브랜드",
        "론칭",
        "오픈",
        "신제품",
        "출시",
        "특가",
        "세일",
        "쿠폰",
        "포인트",
        "혜택",
        "무료체험",
        "[광고]",
        "(광고)",
        "[pr]",
        "(pr)",
        "[홍보]",
        "(홍보)",
    ]

    return any(keyword in content for keyword in ad_keywords)


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


def _extract_blog_source(link: str, title: str = "", description: str = "") -> str:
    """
    블로그 출처 정보 추출

    Args:
        link (str): 블로그 링크
        title (str): 글 제목
        description (str): 글 설명

    Returns:
        str: 출처 이름
    """
    import re
    from urllib.parse import urlparse

    # 1. 제목에서 블로그 플랫폼 정보 추출 (Google News RSS는 제목에 출처 포함)
    if title:
        # "제목 : 네이버 블로그" 또는 "제목 - 네이버" 패턴
        if "네이버 블로그" in title or ": 네이버 블로그" in title:
            # "제목 : 네이버 블로그 - NAVER" 형태에서 제목 부분만 추출
            title_parts = re.split(r'\s*[:：]\s*네이버\s*블로그', title)
            if title_parts and len(title_parts[0]) > 0:
                clean_title = title_parts[0].strip()
                return f"{clean_title[:30]}... (네이버 블로그)"
            return "네이버 블로그"

        # "제목 - 티스토리" 패턴
        if "티스토리" in title or "- 티스토리" in title:
            title_parts = re.split(r'\s*-\s*티스토리', title)
            if title_parts and len(title_parts[0]) > 0:
                clean_title = title_parts[0].strip()
                return f"{clean_title[:30]}... (티스토리)"
            return "티스토리"

        # "제목 - 브런치" 패턴
        if "브런치" in title or "brunch" in title.lower():
            return "브런치"

        # "NAVER" 키워드가 있으면 네이버 블로그로 추정
        if "NAVER" in title or "naver" in title.lower():
            return "네이버 블로그"

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

        except Exception:
            pass

    # 3. 제목이나 설명에서 블로그명 추출 시도
    combined_text = f"{title} {description}"

    # 괄호 안의 블로그명
    bracket_source = re.search(r"\(([가-힣A-Za-z0-9]+\s*블로그)\)", combined_text)
    if bracket_source:
        return bracket_source.group(1)

    return "블로그"


def _get_real_url_from_google(google_url: str) -> str:
    """
    Google 검색 URL에서 실제 원본 블로그 URL을 추출합니다.

    Args:
        google_url (str): Google 검색 URL

    Returns:
        str: 실제 블로그 URL 또는 원본 URL
    """
    try:
        if not google_url or "google.com" not in google_url:
            return google_url

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        # Google 링크를 따라가서 실제 URL 얻기
        response = requests.get(
            google_url, headers=headers, timeout=10, allow_redirects=True
        )

        # 최종 리다이렉트된 URL 반환
        final_url = response.url

        # Google 내부 URL이면 포기
        if "google.com" in final_url:
            return google_url

        return final_url

    except Exception:
        return google_url


def _fetch_blog_content(url: str) -> str:
    """
    블로그 URL에서 본문 내용을 추출합니다.

    Args:
        url (str): 블로그 URL

    Returns:
        str: 추출된 본문 내용
    """
    try:
        # Google URL인 경우 실제 URL로 변환 시도
        real_url = _get_real_url_from_google(url)

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        response = requests.get(real_url, headers=headers, timeout=10)
        if response.status_code != 200:
            return ""

        soup = BeautifulSoup(response.content, "html.parser")

        # 광고, 스크립트, 스타일 태그 제거
        for script in soup(["script", "style", "nav", "header", "footer", "aside"]):
            script.decompose()

        # 다양한 블로그 플랫폼의 본문 선택자
        content_selectors = [
            # 티스토리
            ".entry-content",
            ".tt_article_useless_p_margin",
            ".article-content",
            # 네이버 블로그
            "#postViewArea",
            ".se-main-container",
            ".se_component_wrap",
            # 브런치
            ".wrap_body",
            ".wrap_view_article",
            # 미디엄
            "article",
            ".postArticle-content",
            # 일반적인 선택자
            ".post-content",
            ".blog-content",
            ".content",
            'div[class*="content"]',
            'div[class*="post"]',
            'div[class*="article"]',
            # 마지막 시도: p 태그들
            "p",
        ]

        content = ""
        for selector in content_selectors:
            elements = soup.select(selector)
            if elements:
                if selector == "p":
                    # p 태그의 경우 여러 개를 합침
                    paragraphs = []
                    for elem in elements[:10]:  # 처음 10개 문단까지
                        text = elem.get_text().strip()
                        if (
                            len(text) > 20
                            and not text.startswith(("사진", "이미지", "출처", "©"))
                            and "광고" not in text
                            and "홍보" not in text
                        ):
                            paragraphs.append(text)
                    content = " ".join(paragraphs)
                else:
                    content = elements[0].get_text().strip()

                if len(content) > 100:  # 충분한 내용이 있으면 사용
                    break

        # 텍스트 정제
        if content:
            import re

            # 연속된 공백, 줄바꿈 정리
            content = re.sub(r"\s+", " ", content).strip()

            # 너무 긴 내용은 처음 500자만 사용
            if len(content) > 500:
                content = content[:500]

        return content

    except Exception:
        return ""


def _generate_summary(title: str, content: str, description: str = "") -> str:
    """
    글 제목, 본문, 설명을 바탕으로 요약을 생성합니다.

    Args:
        title (str): 글 제목
        content (str): 글 본문
        description (str): 글 설명

    Returns:
        str: 생성된 요약
    """
    import re

    # 본문이 있으면 본문 기반 요약 생성
    if content and len(content.strip()) > 50:
        # 본문에서 핵심 문장 추출
        sentences = re.split(r"[.!?]", content)
        meaningful_sentences = []

        # 제목에서 주요 키워드 추출
        title_keywords = set(re.findall(r"[가-힣]{2,}", title))

        for sentence in sentences:
            sentence = sentence.strip()

            # 의미있는 문장 필터링
            if (
                len(sentence) > 20
                and len(sentence) < 200
                and not sentence.startswith(("사진", "이미지", "출처", "©"))
                and not re.match(r"^[\d\s\-()]+$", sentence)
                and "광고" not in sentence
                and "홍보" not in sentence
            ):
                # 제목과 관련성 높은 문장 우선 선택
                sentence_keywords = set(re.findall(r"[가-힣]{2,}", sentence))
                relevance_score = len(title_keywords.intersection(sentence_keywords))

                meaningful_sentences.append((sentence, relevance_score))

        if meaningful_sentences:
            # 관련성 점수로 정렬
            meaningful_sentences.sort(key=lambda x: x[1], reverse=True)

            # 상위 2개 문장으로 요약 구성
            selected_sentences = [sent[0] for sent in meaningful_sentences[:2]]
            summary = ". ".join(selected_sentences)

            # 요약이 제목과 너무 유사하면 다른 문장 시도
            if (
                _calculate_similarity(
                    _normalize_title(title), _normalize_title(summary)
                )
                > 0.7
            ):
                if len(meaningful_sentences) > 2:
                    selected_sentences = [sent[0] for sent in meaningful_sentences[1:3]]
                    summary = ". ".join(selected_sentences)

            if len(summary) > 150:
                summary = summary[:147] + "..."
            elif not summary.endswith("."):
                summary += "."

            return summary

    # 본문이 없거나 짧으면 설명에서 요약 추출 시도
    if description:
        cleaned_desc = _clean_description(description)
        if (
            cleaned_desc
            and cleaned_desc
            not in ["요약 정보 없음", "블로그 본문에서 상세 내용을 확인하세요"]
            and _calculate_similarity(
                _normalize_title(title), _normalize_title(cleaned_desc)
            )
            < 0.8
        ):
            return cleaned_desc

    return "블로그 본문에서 상세 내용을 확인하세요."


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
