#!/usr/bin/env python3
"""
Send email via Gmail SMTP
"""

__author__ = "whatwant"
__version__ = "0.1.0"
__license__ = "BEER-WARE"

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

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
    sender_email = "whatwant@whatwant.com"
    receiver_email = "whatwant@gmail.com"
    app_password = "xxxxxxxxxxxxxxxx"

    subject = "This is a lucky email from Python"
    text = "whatwant is a good man."
    html = f"<html><body><p>{text}</p></body></html>"

    send_email(sender_email, receiver_email, app_password, subject, text, html)