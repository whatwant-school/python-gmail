"""
Network utility functions for getting IP information
"""

import socket

import requests


def get_local_ip() -> str:
    """
    로컬 네트워크에서의 IP 주소를 반환합니다.

    Returns:
        str: 로컬 IP 주소
    """
    try:
        # 외부 서버에 연결을 시도하여 로컬 IP를 얻음
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            # Google DNS 서버에 연결 (실제로 데이터를 전송하지는 않음)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
        return local_ip
    except Exception as e:
        return f"로컬 IP 조회 실패: {str(e)}"


def get_public_ip() -> str:
    """
    공용(외부) IP 주소를 반환합니다.

    Returns:
        str: 공용 IP 주소 또는 오류 메시지
    """
    try:
        # 여러 서비스를 시도하여 신뢰성 향상
        services = [
            "https://api.ipify.org",
            "https://httpbin.org/ip",
            "https://ipecho.net/plain",
        ]

        for service in services:
            try:
                response = requests.get(service, timeout=5)
                if response.status_code == 200:
                    if "ipify" in service:
                        return response.text.strip()
                    elif "httpbin" in service:
                        import json

                        return json.loads(response.text)["origin"]
                    elif "ipecho" in service:
                        return response.text.strip()
            except Exception as e:
                import logging

                logging.warning(f"get_public_ip 예외: {e}")
                continue

        return "공용 IP 조회 실패: 모든 서비스에 접근할 수 없습니다"

    except Exception as e:
        return f"공용 IP 조회 실패: {str(e)}"


def get_ip_info() -> dict:
    """
    로컬 IP와 공용 IP 정보를 모두 반환합니다.

    Returns:
        dict: 로컬 IP와 공용 IP 정보
    """
    return {"local_ip": get_local_ip(), "public_ip": get_public_ip()}


def format_ip_info_text(ip_info: dict) -> str:
    """
    IP 정보를 텍스트 형식으로 포맷팅합니다.

    Args:
        ip_info (dict): get_ip_info()에서 반환된 IP 정보

    Returns:
        str: 포맷팅된 IP 정보 텍스트
    """
    return f"""
현재 네트워크 정보:
- 로컬 IP: {ip_info["local_ip"]}
- 공용 IP: {ip_info["public_ip"]}
"""


def format_ip_info_html(ip_info: dict) -> str:
    """
    IP 정보를 HTML 형식으로 포맷팅합니다.

    Args:
        ip_info (dict): get_ip_info()에서 반환된 IP 정보

    Returns:
        str: 포맷팅된 IP 정보 HTML
    """
    return f"""
<h3>현재 네트워크 정보</h3>
<ul>
    <li><strong>로컬 IP:</strong> {ip_info["local_ip"]}</li>
    <li><strong>공용 IP:</strong> {ip_info["public_ip"]}</li>
</ul>
"""
