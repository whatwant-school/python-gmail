"""
News utility functions for searching latest news by keyword
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import requests
from bs4 import BeautifulSoup


def search_news_by_keyword(
    keyword: str, max_results: int = 5, hours_back: int = 24
) -> List[Dict[str, Any]]:
    """
    키워드를 기반으로 최근 뉴스를 검색합니다.

    Args:
        keyword (str): 검색할 키워드
        max_results (int): 최대 결과 수 (3-5개 권장)
        hours_back (int): 검색할 시간 범위 (시간 단위, 기본 24시간)

    Returns:
        List[Dict[str, Any]]: 뉴스 기사 목록
    """
    try:
        # Google News RSS API를 사용한 뉴스 검색
        # RSS를 JSON으로 변환해주는 무료 서비스 활용
        import urllib.parse

        search_query = f"{keyword} -광고 -홍보"  # 광고, 홍보 제외
        encoded_query = urllib.parse.quote(search_query)

        # RSS2JSON API 사용 (무료 서비스)
        rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=ko&gl=KR&ceid=KR:ko"
        encoded_rss_url = urllib.parse.quote(rss_url, safe="")
        api_url = f"https://api.rss2json.com/v1/api.json?rss_url={encoded_rss_url}"

        response = requests.get(api_url, timeout=10)

        if response.status_code != 200:
            return _fallback_news_search(keyword, max_results)

        data = response.json()

        if data.get("status") != "ok":
            return _fallback_news_search(keyword, max_results)

        articles = data.get("items", [])

        # 시간 필터링 및 중복 제거
        cutoff_time = datetime.now() - timedelta(hours=hours_back)
        filtered_articles = []
        seen_titles = set()

        for article in articles:
            # 제목 중복 체크 (유사한 기사 제외)
            title = article.get("title", "")
            if not title or _is_similar_title(title, seen_titles):
                continue

            # 광고/홍보 기사 필터링
            if _is_ad_or_promotional(title, article.get("description", "")):
                continue

            # 발행 시간 파싱
            pub_date = _parse_pub_date(article.get("pubDate", ""))
            if pub_date and pub_date < cutoff_time:
                continue

            # 뉴스 정보 구성
            description = article.get("description", "")
            link = article.get("link", "")

            # 개선된 출처 추출
            source = _extract_source(article.get("source", {}))
            if source == "알 수 없는 출처":
                source = _extract_source_from_title_and_description(
                    title, description, link
                )

            # 기사 본문을 가져와서 개선된 요약 생성
            try:
                article_content = _fetch_article_content(link) if link else ""
                summary = _generate_summary(title, article_content, description)
            except Exception:
                summary = _clean_description(description)

            news_item = {
                "title": title,
                "summary": summary,
                "source": source,
                "link": link,
                "pub_date": pub_date.strftime("%Y-%m-%d %H:%M")
                if pub_date
                else "시간 정보 없음",
                "pub_date_raw": pub_date,
            }

            filtered_articles.append(news_item)
            seen_titles.add(_normalize_title(title))

            if len(filtered_articles) >= max_results:
                break

        # 발행 시간 순으로 정렬 (최신순)
        filtered_articles.sort(
            key=lambda x: x.get("pub_date_raw") or datetime.min, reverse=True
        )

        # 최종 결과에서 raw 시간 정보 제거
        for article in filtered_articles:
            article.pop("pub_date_raw", None)

        return filtered_articles[:max_results]

    except Exception as e:
        print(f"뉴스 검색 중 오류 발생: {e}")
        return _fallback_news_search(keyword, max_results)


def _fallback_news_search(keyword: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """
    주 API가 실패했을 때 사용할 대체 뉴스 검색 방법

    Args:
        keyword (str): 검색할 키워드
        max_results (int): 최대 결과 수

    Returns:
        List[Dict[str, Any]]: 뉴스 기사 목록
    """
    try:
        # 네이버 뉴스 RSS를 대체로 사용
        naver_rss_url = "https://rss.donga.com/total.xml"

        response = requests.get(naver_rss_url, timeout=10)
        if response.status_code == 200:
            # 간단한 XML 파싱으로 제목과 링크 추출 (향후 구현 예정)
            # 임시 결과 반환
            return [
                {
                    "title": f"{keyword} 관련 뉴스 검색 결과를 가져올 수 없습니다",
                    "summary": "뉴스 API 서비스에 일시적인 문제가 발생했습니다.",
                    "source": "시스템 알림",
                    "link": "",
                    "pub_date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                }
            ]

    except Exception:
        pass

    # 모든 방법이 실패한 경우
    return [
        {
            "title": f"{keyword} 뉴스 검색 실패",
            "summary": "네트워크 문제나 API 서비스 장애로 뉴스를 가져올 수 없습니다.",
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
    광고나 홍보성 기사인지 확인

    Args:
        title (str): 기사 제목
        description (str): 기사 설명

    Returns:
        bool: 광고/홍보 기사면 True
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
    기사 설명에서 HTML 태그나 불필요한 내용 제거하고 실제 본문 요약 생성

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

    # 출처 정보나 불필요한 메타 정보 제거
    # 예: "- 뉴스핌", "- 화성저널" 등의 패턴 제거
    clean_desc = re.sub(
        r"\s*-\s*[가-힣A-Za-z]+(?:저널|뉴스|신문|일보|방송|미디어|닷컴|\.com|\.net|\.co\.kr)?\s*$",
        "",
        clean_desc,
    )

    # URL이나 도메인 정보 제거
    clean_desc = re.sub(r"https?://[^\s]+", "", clean_desc)
    clean_desc = re.sub(r"www\.[^\s]+", "", clean_desc)
    clean_desc = re.sub(r"[a-zA-Z0-9.-]+\.(com|net|co\.kr|org)\b", "", clean_desc)

    # v.daum.net 같은 패턴 제거
    clean_desc = re.sub(r"v\.[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", "", clean_desc)

    # 기사 제목과 동일한 부분 제거 (중복 방지)
    # 만약 설명이 제목과 거의 동일하다면 더 의미있는 요약 생성
    if len(clean_desc.strip()) < 20:
        return "기사 본문에서 상세 내용을 확인하세요"

    # 연속된 공백 다시 정리
    clean_desc = re.sub(r"\s+", " ", clean_desc).strip()

    # 너무 긴 설명은 잘라내기 (150자 제한으로 축소)
    if len(clean_desc) > 150:
        # 문장 단위로 자르기 시도
        sentences = clean_desc.split(". ")
        if len(sentences) > 1:
            clean_desc = sentences[0] + "."
            if len(clean_desc) > 150:
                clean_desc = clean_desc[:147] + "..."
        else:
            clean_desc = clean_desc[:147] + "..."

    return clean_desc if clean_desc.strip() else "기사 본문에서 상세 내용을 확인하세요"


def _extract_source(source_info: Any) -> str:
    """
    뉴스 출처 정보 추출

    Args:
        source_info: 출처 정보 (dict 또는 str)

    Returns:
        str: 출처 이름
    """
    if isinstance(source_info, dict):
        return source_info.get("title", source_info.get("name", "알 수 없는 출처"))
    elif isinstance(source_info, str):
        return source_info
    else:
        return "알 수 없는 출처"


def _extract_source_from_title_and_description(
    title: str, description: str, link: str = ""
) -> str:
    """
    제목, 설명, 링크에서 뉴스 출처를 추출

    Args:
        title (str): 기사 제목
        description (str): 기사 설명
        link (str): 기사 링크

    Returns:
        str: 출처 이름
    """
    import re

    # 1. 제목에서 출처 추출 (제목 끝에 "- 출처명" 패턴)
    title_source_match = re.search(
        r"\s*-\s*([가-힣A-Za-z0-9]+(?:저널|뉴스|신문|일보|방송|미디어|타임즈|헤럴드|포스트|투데이|데일리|위클리))\s*$",
        title,
    )
    if title_source_match:
        return title_source_match.group(1)

    # 2. 설명에서 출처 추출
    desc_source_match = re.search(
        r"\s*-?\s*([가-힣A-Za-z0-9]+(?:저널|뉴스|신문|일보|방송|미디어|타임즈|헤럴드|포스트|투데이|데일리|위클리))\s*$",
        description,
    )
    if desc_source_match:
        return desc_source_match.group(1)

    # 3. 링크에서 도메인 기반 출처 추출
    if link:
        try:
            from urllib.parse import urlparse

            parsed_url = urlparse(link)
            domain = parsed_url.netloc.lower()

            # 주요 언론사 도메인 매핑
            domain_mapping = {
                "news.naver.com": "네이버뉴스",
                "news.daum.net": "다음뉴스",
                "v.daum.net": "다음뉴스",
                "news.google.com": "구글뉴스",
                "yna.co.kr": "연합뉴스",
                "yonhapnews.co.kr": "연합뉴스",
                "chosun.com": "조선일보",
                "donga.com": "동아일보",
                "joongang.co.kr": "중앙일보",
                "hani.co.kr": "한겨레",
                "khan.co.kr": "경향신문",
                "mt.co.kr": "머니투데이",
                "mk.co.kr": "매일경제",
                "hankyung.com": "한국경제",
                "sbs.co.kr": "SBS",
                "kbs.co.kr": "KBS",
                "mbc.co.kr": "MBC",
                "newspim.com": "뉴스핌",
                "news1.kr": "뉴스1",
                "pressian.com": "프레시안",
                "ohmynews.com": "오마이뉴스",
                "sisain.co.kr": "시사IN",
                "hankookilbo.com": "한국일보",
                "seoul.co.kr": "서울신문",
                "munhwa.com": "문화일보",
                "dt.co.kr": "디지털타임스",
                "etnews.com": "전자신문",
                "zdnet.co.kr": "ZDNet Korea",
            }

            # 정확한 도메인 매칭
            if domain in domain_mapping:
                return domain_mapping[domain]

            # 부분 도메인 매칭
            for known_domain, source_name in domain_mapping.items():
                if known_domain in domain or domain in known_domain:
                    return source_name

            # 도메인에서 언론사명 추출 시도
            domain_parts = domain.replace("www.", "").split(".")
            if len(domain_parts) >= 2:
                main_domain = domain_parts[0]
                # 언론사 키워드가 포함된 경우
                if any(
                    keyword in main_domain
                    for keyword in [
                        "news",
                        "journal",
                        "daily",
                        "times",
                        "post",
                        "herald",
                    ]
                ):
                    return main_domain.title()
                # 한국 언론사 도메인 패턴
                if main_domain.endswith(("news", "journal")):
                    return (
                        main_domain.replace("news", "뉴스")
                        .replace("journal", "저널")
                        .title()
                    )

        except Exception:
            pass

    # 4. 기타 패턴으로 출처 추출
    combined_text = f"{title} {description}"

    # 괄호 안의 출처 정보
    bracket_source = re.search(
        r"\(([가-힣A-Za-z0-9]+(?:저널|뉴스|신문|일보|방송|미디어))\)", combined_text
    )
    if bracket_source:
        return bracket_source.group(1)

    # 대괄호 안의 출처 정보
    square_bracket_source = re.search(
        r"\[([가-힣A-Za-z0-9]+(?:저널|뉴스|신문|일보|방송|미디어))\]", combined_text
    )
    if square_bracket_source:
        return square_bracket_source.group(1)

    return "알 수 없는 출처"


def _get_real_url_from_google_news(google_news_url: str) -> str:
    """
    Google News URL에서 실제 원본 기사 URL을 추출합니다.

    Args:
        google_news_url (str): Google News RSS URL

    Returns:
        str: 실제 기사 URL 또는 원본 URL
    """
    try:
        if not google_news_url or "news.google.com" not in google_news_url:
            return google_news_url

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        # Google News 링크를 따라가서 실제 URL 얻기
        response = requests.get(
            google_news_url, headers=headers, timeout=10, allow_redirects=True
        )

        # 최종 리다이렉트된 URL 반환
        final_url = response.url

        # Google News 내부 URL이면 포기
        if "news.google.com" in final_url:
            return google_news_url

        return final_url

    except Exception:
        return google_news_url


def _fetch_article_content(url: str) -> str:
    """
    기사 URL에서 본문 내용을 추출합니다.

    Args:
        url (str): 기사 URL

    Returns:
        str: 추출된 본문 내용
    """
    try:
        # Google News URL인 경우 실제 URL로 변환 시도
        real_url = _get_real_url_from_google_news(url)

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

        # 다양한 언론사의 본문 선택자 시도
        content_selectors = [
            # 네이버 뉴스
            "#dic_area",
            ".go_trans._article_content",
            # 다음 뉴스
            ".news_view .article_view",
            ".news_view .view_content",
            # 일반적인 선택자
            "article",
            ".article-content",
            ".article_content",
            ".news-content",
            ".content",
            ".view_content",
            ".article-body",
            ".entry-content",
            'div[class*="content"]',
            'div[class*="article"]',
            # 지역 언론사 선택자 추가
            ".article_txt",
            ".news_article",
            ".view_text",
            # 마지막 시도: p 태그들
            "p",
        ]

        content = ""
        for selector in content_selectors:
            elements = soup.select(selector)
            if elements:
                if selector == "p":
                    # p 태그의 경우 여러 개를 합침 (더 많은 문단 포함)
                    paragraphs = []
                    for elem in elements[:10]:  # 처음 10개 문단까지
                        text = elem.get_text().strip()
                        if (
                            len(text) > 20  # 의미있는 길이
                            and not text.startswith(
                                (
                                    "기자",
                                    "사진",
                                    "영상",
                                    "출처",
                                    "저작권",
                                    "▲",
                                    "■",
                                    "※",
                                )
                            )
                            and not text.endswith(("기자", "제공"))
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
            # 불필요한 텍스트 제거
            content = re.sub(r"(기자\s*=?\s*[가-힣]+|[가-힣]+\s*기자)", "", content)
            content = re.sub(r"(사진\s*=?\s*[^.]*|영상\s*=?\s*[^.]*)", "", content)
            content = re.sub(r"(▲|■|※)[^.]*", "", content)

            # 너무 긴 내용은 처음 500자만 사용
            if len(content) > 500:
                content = content[:500]

        return content

    except Exception:
        return ""


def _generate_summary(title: str, content: str, description: str = "") -> str:
    """
    기사 제목, 본문, 설명을 바탕으로 요약을 생성합니다.

    Args:
        title (str): 기사 제목
        content (str): 기사 본문
        description (str): 기사 설명

    Returns:
        str: 생성된 요약
    """
    import re

    # 본문이 있으면 본문 기반 요약 생성
    if content and len(content.strip()) > 50:
        # 본문에서 핵심 문장 추출
        sentences = re.split(r"[.!?]", content)
        meaningful_sentences = []

        # 제목에서 주요 키워드 추출 (요약 품질 향상용)
        title_keywords = set(re.findall(r"[가-힣]{2,}", title))

        for sentence in sentences:
            sentence = sentence.strip()

            # 의미있는 문장 필터링
            if (
                len(sentence) > 20
                and len(sentence) < 200  # 적절한 길이
                and not sentence.startswith(
                    ("기자", "사진", "영상", "출처", "저작권", "▲", "■", "※", "이메일")
                )
                and not sentence.endswith(("기자", "제공", "=연합뉴스"))
                and not re.match(r"^[\d\s\-()]+$", sentence)  # 숫자만 있는 문장 제외
                and "광고" not in sentence
                and "홍보" not in sentence
                and "copyright" not in sentence.lower()
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
        # 설명에서 제목과 다른 부분 찾기
        cleaned_desc = _clean_description(description)
        if (
            cleaned_desc
            and cleaned_desc
            not in ["요약 정보 없음", "기사 본문에서 상세 내용을 확인하세요"]
            and _calculate_similarity(
                _normalize_title(title), _normalize_title(cleaned_desc)
            )
            < 0.8
        ):
            return cleaned_desc

    # 제목에서 핵심 정보 추출해서 기본 요약 생성
    import re

    # 날짜, 장소, 행사명 등 추출
    title_without_source = re.sub(
        r"\s*-\s*[가-힣A-Za-z0-9]+(?:저널|뉴스|신문|일보|방송|미디어)?\s*$", "", title
    )

    if "개최" in title_without_source or "진행" in title_without_source:
        return f"{title_without_source.strip()}에 대한 상세 내용을 기사에서 확인할 수 있습니다."
    elif "발표" in title_without_source or "계획" in title_without_source:
        return (
            f"{title_without_source.strip()}에 관한 구체적인 내용이 포함되어 있습니다."
        )
    else:
        return "기사 본문에서 상세 내용을 확인하세요."


def format_news_info_text(news_list: List[Dict[str, Any]], keyword: str) -> str:
    """
    뉴스 정보를 텍스트 형식으로 포맷팅합니다.

    Args:
        news_list (List[Dict[str, Any]]): 뉴스 기사 목록
        keyword (str): 검색 키워드

    Returns:
        str: 포맷팅된 뉴스 정보 텍스트
    """
    if not news_list:
        return f"""
"{keyword}" 관련 최신 뉴스:
- 검색 결과가 없습니다.
"""

    result = f"""
"{keyword}" 관련 최신 뉴스 ({len(news_list)}건):

"""

    for i, news in enumerate(news_list, 1):
        result += f"{i}. {news.get('title', '제목 없음')}\n"
        result += f"   요약: {news.get('summary', '요약 없음')}\n"
        result += f"   출처: {news.get('source', '알 수 없음')}\n"
        result += f"   등록: {news.get('pub_date', '시간 정보 없음')}\n"

        if news.get("link"):
            result += f"   링크: {news['link']}\n"

        result += "\n"

    return result


def format_news_info_html(news_list: List[Dict[str, Any]], keyword: str) -> str:
    """
    뉴스 정보를 HTML 형식으로 포맷팅합니다.

    Args:
        news_list (List[Dict[str, Any]]): 뉴스 기사 목록
        keyword (str): 검색 키워드

    Returns:
        str: 포맷팅된 뉴스 정보 HTML
    """
    if not news_list:
        return f"""
<h3>📰 "{keyword}" 관련 최신 뉴스</h3>
<p><em>검색 결과가 없습니다.</em></p>
"""

    result = f"""
<h3>📰 "{keyword}" 관련 최신 뉴스 ({len(news_list)}건)</h3>
<div style="margin-left: 10px;">
"""

    for i, news in enumerate(news_list, 1):
        title = news.get("title", "제목 없음")
        summary = news.get("summary", "요약 없음")
        source = news.get("source", "알 수 없음")
        pub_date = news.get("pub_date", "시간 정보 없음")
        link = news.get("link", "")

        result += f"""
<div style="margin-bottom: 15px; padding: 10px; border-left: 3px solid #007acc;">
    <h4 style="margin: 0 0 5px 0; color: #007acc;">
        {i}. {title}
    </h4>
    <p style="margin: 5px 0; color: #555; font-size: 14px;">
        📝 <strong>요약:</strong> {summary}
    </p>
    <p style="margin: 5px 0; color: #777; font-size: 12px;">
        📺 <strong>출처:</strong> {source} |
        🕒 <strong>등록:</strong> {pub_date}
    </p>
"""

        if link:
            result += f"""
    <p style="margin: 5px 0; font-size: 12px;">
        🔗 <a href="{link}" style="color: #007acc;">기사 링크</a>
    </p>
"""

        result += "</div>\n"

    result += "</div>\n"

    return result
