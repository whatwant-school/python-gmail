#!/usr/bin/env python3
"""
Send email via Gmail SMTP
"""

__author__ = "whatwant"
__version__ = "0.4.0"
__license__ = "BEER-WARE"

import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from module.blog_utils import (
    format_blog_info_html,
    format_blog_info_text,
    search_blogs_by_keyword,
)
from module.network_utils import format_ip_info_html, format_ip_info_text, get_ip_info
from module.news_utils import (
    format_news_info_html,
    format_news_info_text,
    search_news_by_keyword,
)
from module.weather_utils import (
    format_weather_info_html,
    format_weather_info_text,
    get_weather_by_address,
)

# .env 파일이 있으면 로드 (python-dotenv가 설치된 경우)
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass  # python-dotenv가 없어도 환경 변수는 직접 설정할 수 있음


def send_email(sender_email, receiver_email, app_password, subject, text, html):
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = sender_email
    message["To"] = receiver_email

    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")

    message.attach(part1)
    message.attach(part2)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender_email, app_password)
        server.sendmail(sender_email, receiver_email, message.as_string())


if __name__ == "__main__":
    # 환경 변수에서 Gmail 설정 읽기
    sender_email = os.getenv("GMAIL_SENDER_EMAIL")
    receiver_email = os.getenv("GMAIL_RECEIVER_EMAIL")
    app_password = os.getenv("GMAIL_APP_PASSWORD")

    # 필수 환경 변수 체크
    if not all([sender_email, receiver_email, app_password]):
        raise ValueError(
            "다음 환경 변수들을 설정해주세요: GMAIL_SENDER_EMAIL, GMAIL_RECEIVER_EMAIL, GMAIL_APP_PASSWORD"
        )

    # IP 정보 가져오기
    ip_info = get_ip_info()

    # 날씨 정보 가져오기 (환경 변수에서 주소를 읽고, 없으면 기본값 사용)
    weather_address = os.getenv("WEATHER_ADDRESS", "화성시 동탄")
    weather_info = get_weather_by_address(weather_address)

    # 뉴스 정보 가져오기 (WEATHER_ADDRESS를 키워드로 사용)
    news_info = search_news_by_keyword(weather_address, max_results=4, hours_back=24)

    # 블로그 정보 가져오기 (WEATHER_ADDRESS를 키워드로 사용)
    blog_info = search_blogs_by_keyword(weather_address, max_results=4, hours_back=24)

    subject = "This is a lucky email with IP, Weather, News & Blog Info"
    base_text = "whatwant is a good man."
    ip_text = format_ip_info_text(ip_info)
    weather_text = format_weather_info_text(weather_info)
    news_text = format_news_info_text(news_info, weather_address)
    blog_text = format_blog_info_text(blog_info, weather_address)
    text = (
        base_text
        + "\n"
        + ip_text
        + "\n"
        + weather_text
        + "\n"
        + news_text
        + "\n"
        + blog_text
    )

    base_html = f"<p>{base_text}</p>"
    ip_html = format_ip_info_html(ip_info)
    weather_html = format_weather_info_html(weather_info)
    news_html = format_news_info_html(news_info, weather_address)
    blog_html = format_blog_info_html(blog_info, weather_address)
    html = f"<html><body>{base_html}{ip_html}{weather_html}{news_html}{blog_html}</body></html>"

    send_email(sender_email, receiver_email, app_password, subject, text, html)
