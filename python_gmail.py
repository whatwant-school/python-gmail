#!/usr/bin/env python3
"""
Send email via Gmail SMTP
"""

__author__ = "whatwant"
__version__ = "0.1.0"
__license__ = "BEER-WARE"

import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

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
        raise ValueError("다음 환경 변수들을 설정해주세요: GMAIL_SENDER_EMAIL, GMAIL_RECEIVER_EMAIL, GMAIL_APP_PASSWORD")

    subject = "This is a lucky email from Python"
    text = "whatwant is a good man."
    html = f"<html><body><p>{text}</p></body></html>"

    send_email(sender_email, receiver_email, app_password, subject, text, html)
