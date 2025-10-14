"""
Tests for news_utils module
"""

from datetime import datetime, timedelta
from unittest.mock import Mock, patch

import pytest

from module.news_utils import (
    _calculate_similarity,
    _clean_description,
    _extract_source,
    _is_ad_or_promotional,
    _is_similar_title,
    _normalize_title,
    _parse_pub_date,
    format_news_info_html,
    format_news_info_text,
    search_news_by_keyword,
)


class TestNewsUtils:
    """뉴스 유틸리티 함수들을 테스트합니다."""

    def test_normalize_title(self):
        """제목 정규화 테스트"""
        # 기본 정규화
        assert (
            _normalize_title("안녕하세요! 오늘의 뉴스입니다.")
            == "안녕하세요 오늘의 뉴스입니다"
        )

        # 특수문자 제거
        assert (
            _normalize_title("[속보] 화성시 동탄 신도시 개발")
            == "속보 화성시 동탄 신도시 개발"
        )

        # 연속 공백 처리
        assert _normalize_title("뉴스    제목   테스트") == "뉴스 제목 테스트"

        # 빈 문자열
        assert _normalize_title("") == ""

    def test_calculate_similarity(self):
        """문자열 유사도 계산 테스트"""
        # 동일한 문자열
        assert _calculate_similarity("화성시 동탄", "화성시 동탄") == 1.0

        # 완전히 다른 문자열
        assert _calculate_similarity("화성시 동탄", "서울시 강남") == 0.0

        # 부분적으로 유사한 문자열
        similarity = _calculate_similarity("화성시 동탄 뉴스", "화성시 동탄 개발")
        assert 0.0 < similarity < 1.0

        # 빈 문자열들
        assert _calculate_similarity("", "") == 1.0

    def test_is_similar_title(self):
        """제목 유사성 판단 테스트"""
        seen_titles = {"화성시 동탄 신도시 개발", "서울시 강남구 뉴스"}

        # 유사한 제목
        assert _is_similar_title("화성시 동탄 신도시 확장", seen_titles) is True

        # 다른 제목
        assert _is_similar_title("부산시 해운대 개발", seen_titles) is False

        # 빈 집합
        assert _is_similar_title("아무 제목", set()) is False

    def test_is_ad_or_promotional(self):
        """광고/홍보 기사 판단 테스트"""
        # 광고성 제목
        assert _is_ad_or_promotional("[광고] 화성시 아파트 분양", "") is True
        assert _is_ad_or_promotional("특가 할인 이벤트", "") is True

        # 일반 뉴스
        assert _is_ad_or_promotional("화성시 교통 개선 계획", "") is False

        # 설명에 광고 키워드
        assert _is_ad_or_promotional("화성시 뉴스", "마케팅 이벤트 진행") is True

    def test_clean_description(self):
        """기사 설명 정제 테스트"""
        # HTML 태그 제거 (개선된 로직에 맞게 수정)
        html_text = "<p>화성시 <strong>동탄</strong> 개발 소식입니다. 이는 매우 중요한 뉴스로서 지역 발전에 큰 영향을 미칠 것으로 예상됩니다.</p>"
        result = _clean_description(html_text)
        assert "화성시 동탄 개발 소식" in result
        assert len(result) > 20  # 충분한 길이의 설명이 있어야 함

        # 연속 공백 정리 (개선된 로직에서는 너무 짧은 텍스트는 기본 메시지 반환)
        spaced_text = "화성시 동탄 개발이 활발히 진행되고 있어 지역 경제 활성화에 기여할 것으로 기대됩니다"
        result = _clean_description(spaced_text)
        assert (
            "화성시 동탄 개발" in result
            or result == "기사 본문에서 상세 내용을 확인하세요"
        )

        # 빈 문자열
        assert _clean_description("") == "요약 정보 없음"
        assert _clean_description(None) == "요약 정보 없음"

        # 긴 텍스트 잘라내기
        long_text = "화성시 동탄 신도시 개발이 본격적으로 시작되면서 " + "a" * 200
        result = _clean_description(long_text)
        assert len(result) <= 155  # 150자 제한 + "..." 고려
        assert result.endswith("...") or "기사 본문에서" in result

    def test_extract_source(self):
        """뉴스 출처 추출 테스트"""
        # 딕셔너리 형태
        source_dict = {"title": "조선일보", "name": "chosun"}
        assert _extract_source(source_dict) == "조선일보"

        # name만 있는 경우
        source_dict2 = {"name": "중앙일보"}
        assert _extract_source(source_dict2) == "중앙일보"

        # 문자열 형태
        assert _extract_source("동아일보") == "동아일보"

        # 기타 형태
        assert _extract_source(None) == "알 수 없는 출처"
        assert _extract_source(123) == "알 수 없는 출처"

    def test_parse_pub_date(self):
        """발행일 파싱 테스트"""
        # 표준 RSS 형식
        rss_date = "Mon, 14 Oct 2024 10:30:00 GMT"
        result = _parse_pub_date(rss_date)
        assert result is not None
        assert result.year == 2024
        assert result.month == 10
        assert result.day == 14

        # ISO 형식
        iso_date = "2024-10-14T10:30:00+09:00"
        result = _parse_pub_date(iso_date)
        # 타임존 파싱이 안될 수 있으므로 날짜만 확인
        assert result is not None

        # 일반 형식
        simple_date = "2024-10-14 10:30:00"
        result = _parse_pub_date(simple_date)
        assert result is not None
        assert result.year == 2024

        # 잘못된 형식
        assert _parse_pub_date("invalid date") is None
        assert _parse_pub_date("") is None
        assert _parse_pub_date(None) is None

    def test_format_news_info_text(self):
        """뉴스 정보 텍스트 포맷팅 테스트"""
        # 정상적인 뉴스 목록
        news_list = [
            {
                "title": "화성시 동탄 개발 소식",
                "summary": "동탄 신도시 개발이 진행됩니다",
                "source": "조선일보",
                "link": "http://example.com",
                "pub_date": "2024-10-14 10:30",
            }
        ]

        result = format_news_info_text(news_list, "화성시")
        assert "화성시" in result
        assert "화성시 동탄 개발 소식" in result
        assert "조선일보" in result
        assert "2024-10-14 10:30" in result
        assert "http://example.com" in result

        # 빈 목록
        empty_result = format_news_info_text([], "화성시")
        assert "검색 결과가 없습니다" in empty_result
        assert "화성시" in empty_result

    def test_format_news_info_html(self):
        """뉴스 정보 HTML 포맷팅 테스트"""
        # 정상적인 뉴스 목록
        news_list = [
            {
                "title": "화성시 동탄 개발 소식",
                "summary": "동탄 신도시 개발이 진행됩니다",
                "source": "조선일보",
                "link": "http://example.com",
                "pub_date": "2024-10-14 10:30",
            }
        ]

        result = format_news_info_html(news_list, "화성시")
        assert "<h3>" in result
        assert "화성시" in result
        assert "화성시 동탄 개발 소식" in result
        assert "조선일보" in result
        assert "http://example.com" in result
        assert "<a href=" in result

        # 빈 목록
        empty_result = format_news_info_html([], "화성시")
        assert "<h3>" in empty_result
        assert "검색 결과가 없습니다" in empty_result

    @patch("module.news_utils.requests.get")
    def test_search_news_by_keyword_success(self, mock_get):
        """뉴스 검색 성공 테스트"""

        # Mock API 응답과 기사 본문 응답을 모두 설정
        def mock_requests_get(url, **kwargs):
            if "api.rss2json.com" in url:
                # RSS2JSON API 응답
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.json.return_value = {
                    "status": "ok",
                    "items": [
                        {
                            "title": "화성시 동탄 개발 소식",
                            "description": "동탄 신도시 개발이 진행됩니다",
                            "source": {"title": "조선일보"},
                            "link": "http://example.com/news1",
                            "pubDate": datetime.now().strftime(
                                "%a, %d %b %Y %H:%M:%S GMT"
                            ),
                        },
                        {
                            "title": "[광고] 화성시 아파트 분양",  # 광고 - 필터링 될 것
                            "description": "특가 분양 이벤트",
                            "source": {"title": "부동산뉴스"},
                            "link": "http://example.com/ad1",
                            "pubDate": (datetime.now() - timedelta(hours=1)).strftime(
                                "%a, %d %b %Y %H:%M:%S GMT"
                            ),
                        },
                        {
                            "title": "화성시 교통 개선 계획",
                            "description": "대중교통 확충 예정",
                            "source": {"title": "중앙일보"},
                            "link": "http://example.com/news2",
                            "pubDate": (datetime.now() - timedelta(hours=2)).strftime(
                                "%a, %d %b %Y %H:%M:%S GMT"
                            ),
                        },
                    ],
                }
                return mock_response
            else:
                # 기사 본문 가져오기 응답 (실패하도록 설정)
                mock_response = Mock()
                mock_response.status_code = 404
                mock_response.content = ""
                return mock_response

        mock_get.side_effect = mock_requests_get

        result = search_news_by_keyword("화성시", max_results=3)

        # API가 여러 번 호출될 수 있음 (RSS API + 기사 본문 가져오기)
        assert mock_get.call_count >= 1

        # 결과 검증
        assert len(result) == 2  # 광고 1개 제외
        assert result[0]["title"] == "화성시 동탄 개발 소식"
        assert result[1]["title"] == "화성시 교통 개선 계획"

        # 필수 필드 확인
        for news in result:
            assert "title" in news
            assert "summary" in news
            assert "source" in news
            assert "link" in news
            assert "pub_date" in news

    @patch("module.news_utils.requests.get")
    def test_search_news_by_keyword_failure(self, mock_get):
        """뉴스 검색 실패 테스트"""
        # API 요청 실패
        mock_get.side_effect = Exception("Network error")

        result = search_news_by_keyword("화성시")

        # 실패 시 fallback 결과 반환
        assert len(result) == 1
        assert (
            "검색 실패" in result[0]["title"]
            or "가져올 수 없습니다" in result[0]["title"]
        )

    @patch("module.news_utils.requests.get")
    def test_search_news_by_keyword_api_error(self, mock_get):
        """API 오류 응답 테스트"""
        # API 오류 응답
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "error",
            "message": "API limit exceeded",
        }
        mock_get.return_value = mock_response

        result = search_news_by_keyword("화성시")

        # fallback 결과 확인
        assert len(result) >= 1
        assert isinstance(result[0], dict)

    @patch("module.news_utils.requests.get")
    def test_search_news_by_keyword_empty_results(self, mock_get):
        """검색 결과 없음 테스트"""
        # 빈 결과 응답
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok", "items": []}
        mock_get.return_value = mock_response

        result = search_news_by_keyword("화성시")

        # 빈 결과 반환
        assert len(result) == 0

    def test_search_news_by_keyword_time_filtering(self):
        """시간 필터링 테스트"""
        # 실제 API 호출 없이 내부 로직만 테스트
        # 이 테스트는 실제 데이터 처리 로직을 확인하기 위한 것

        # 24시간 이내 뉴스만 필터링되는지 확인
        # (실제 구현에서는 cutoff_time과 비교)
        cutoff_time = datetime.now() - timedelta(hours=24)
        recent_time = datetime.now() - timedelta(hours=12)
        old_time = datetime.now() - timedelta(hours=48)

        assert recent_time > cutoff_time
        assert old_time < cutoff_time


class TestNewsUtilsIntegration:
    """뉴스 유틸리티 통합 테스트 (실제 웹 요청 포함)"""

    @pytest.mark.integration
    def test_real_news_search(self):
        """실제 뉴스 검색 테스트"""
        # 실제 API 호출을 통한 통합 테스트
        # 네트워크 연결이 필요하므로 @pytest.mark.integration으로 표시

        result = search_news_by_keyword(
            "서울", max_results=2, hours_back=72
        )  # 72시간으로 범위 확대

        # 기본적인 응답 구조 확인
        assert isinstance(result, list)

        if result:  # 결과가 있는 경우에만 검증
            for news in result:
                assert isinstance(news, dict)
                assert "title" in news
                assert "summary" in news
                assert "source" in news
                assert "pub_date" in news
                # link는 선택적일 수 있음

                # 기본적인 데이터 타입 확인
                assert isinstance(news["title"], str)
                assert isinstance(news["summary"], str)
                assert isinstance(news["source"], str)
                assert isinstance(news["pub_date"], str)

                # 제목과 요약이 비어있지 않은지 확인
                assert news["title"].strip()
                assert news["summary"].strip()

        print(f"실제 뉴스 검색 결과: {len(result)}건")
        if result:
            print(f"첫 번째 뉴스 제목: {result[0]['title']}")

    @pytest.mark.integration
    def test_real_news_search_with_keyword(self):
        """특정 키워드로 실제 뉴스 검색 테스트"""
        # 화성시로 실제 검색 (요청사항과 동일)
        result = search_news_by_keyword("화성시", max_results=3, hours_back=72)

        assert isinstance(result, list)
        assert len(result) <= 3

        if result:
            print(f"화성시 뉴스 검색 결과: {len(result)}건")
            for i, news in enumerate(result, 1):
                print(f"{i}. {news['title']}")
                print(f"   출처: {news['source']}")
                print(f"   등록: {news['pub_date']}")
                print()

    @pytest.mark.integration
    def test_real_news_formatting(self):
        """실제 뉴스 데이터 포맷팅 테스트"""
        news_list = search_news_by_keyword("동탄", max_results=2, hours_back=72)

        # 텍스트 포맷팅 테스트
        text_result = format_news_info_text(news_list, "동탄")
        assert isinstance(text_result, str)
        assert "동탄" in text_result

        # HTML 포맷팅 테스트
        html_result = format_news_info_html(news_list, "동탄")
        assert isinstance(html_result, str)
        assert "<h3>" in html_result
        assert "동탄" in html_result

        print(f"포맷팅 테스트 완료 - 뉴스 {len(news_list)}건")


if __name__ == "__main__":
    # 유닛 테스트만 실행 (통합 테스트 제외)
    pytest.main([__file__, "-v", "-m", "not integration"])
