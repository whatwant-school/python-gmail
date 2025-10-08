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
