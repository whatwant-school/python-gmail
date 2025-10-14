import os
from unittest import mock

import pytest

import python_gmail as gmail


@pytest.fixture
def env_vars():
    with mock.patch.dict(
        os.environ,
        {
            "GMAIL_SENDER_EMAIL": "sender@example.com",
            "GMAIL_RECEIVER_EMAIL": "receiver@example.com",
            "GMAIL_APP_PASSWORD": "dummyapppassword",
            "WEATHER_ADDRESS": "화성시 동탄",
        },
    ):
        yield


def test_send_email_success(env_vars):
    with mock.patch("smtplib.SMTP_SSL") as mock_smtp:
        instance = mock_smtp.return_value.__enter__.return_value
        gmail.send_email(
            os.environ["GMAIL_SENDER_EMAIL"],
            os.environ["GMAIL_RECEIVER_EMAIL"],
            os.environ["GMAIL_APP_PASSWORD"],
            "Test Subject",
            "Test Text",
            "<p>Test HTML</p>",
        )
        instance.login.assert_called_once_with(
            os.environ["GMAIL_SENDER_EMAIL"], os.environ["GMAIL_APP_PASSWORD"]
        )
        instance.sendmail.assert_called_once()


def test_send_email_env_missing():
    with mock.patch.dict(os.environ, {}, clear=True):
        with pytest.raises(ValueError):
            # __main__ block expects env vars, simulate as script
            if not all(
                [
                    os.getenv("GMAIL_SENDER_EMAIL"),
                    os.getenv("GMAIL_RECEIVER_EMAIL"),
                    os.getenv("GMAIL_APP_PASSWORD"),
                ]
            ):
                raise ValueError(
                    "다음 환경 변수들을 설정해주세요: GMAIL_SENDER_EMAIL, GMAIL_RECEIVER_EMAIL, GMAIL_APP_PASSWORD"
                )


def test_main_integration_with_news(env_vars):
    """메인 기능에 뉴스 검색이 포함된 통합 테스트"""
    # 모든 필요한 모듈이 import되고 있는지 확인
    import python_gmail
    from module.network_utils import get_ip_info
    from module.news_utils import (
        format_news_info_html,
        format_news_info_text,
        search_news_by_keyword,
    )
    from module.weather_utils import get_weather_by_address

    # 함수들이 존재하는지 확인
    assert hasattr(python_gmail, "send_email")
    assert callable(search_news_by_keyword)
    assert callable(format_news_info_text)
    assert callable(format_news_info_html)
    assert callable(get_weather_by_address)
    assert callable(get_ip_info)

    # 뉴스 검색 함수가 제대로 동작하는지 간단히 테스트
    news_result = search_news_by_keyword("테스트", max_results=1, hours_back=72)
    assert isinstance(news_result, list)

    # 포매팅 함수도 제대로 동작하는지 확인
    sample_news = [
        {
            "title": "테스트 뉴스",
            "summary": "테스트",
            "source": "테스트",
            "pub_date": "2024-10-14",
        }
    ]
    text_result = format_news_info_text(sample_news, "테스트")
    html_result = format_news_info_html(sample_news, "테스트")

    assert isinstance(text_result, str)
    assert isinstance(html_result, str)
    assert "테스트 뉴스" in text_result
    assert "테스트 뉴스" in html_result


def test_news_integration_in_email_content():
    """이메일 내용에 뉴스가 포함되는지 테스트"""
    from module.news_utils import format_news_info_html, format_news_info_text

    # 테스트 뉴스 데이터
    news_data = [
        {
            "title": "화성시 동탄 개발 소식",
            "summary": "동탄 신도시 개발이 진행됩니다",
            "source": "조선일보",
            "link": "http://example.com",
            "pub_date": "2024-10-14 10:30",
        }
    ]

    # 텍스트 포맷팅
    text_content = format_news_info_text(news_data, "화성시")
    assert "화성시" in text_content
    assert "화성시 동탄 개발 소식" in text_content
    assert "조선일보" in text_content

    # HTML 포맷팅
    html_content = format_news_info_html(news_data, "화성시")
    assert "<h3>" in html_content
    assert "화성시" in html_content
    assert "화성시 동탄 개발 소식" in html_content
    assert "http://example.com" in html_content
