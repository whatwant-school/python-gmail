"""
Weather utility functions for getting weather information
"""

from typing import Dict, Optional

import requests


def get_coordinates_by_address(address: str) -> Optional[Dict[str, float]]:
    """
    주소를 기반으로 좌표(위도, 경도)를 조회합니다.

    Args:
        address (str): 조회할 주소

    Returns:
        Optional[Dict[str, float]]: 위도, 경도 정보 또는 None
    """
    try:
        # Nominatim API (OpenStreetMap)를 사용하여 좌표 조회
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            "q": address,
            "format": "json",
            "limit": 1,
            "accept-language": "ko",
        }

        headers = {"User-Agent": "python-gmail/0.2.1"}

        response = requests.get(url, params=params, headers=headers, timeout=10)

        if response.status_code == 200:
            data = response.json()
            if data:
                return {"lat": float(data[0]["lat"]), "lon": float(data[0]["lon"])}
        return None
    except Exception:
        return None


def get_weather_by_coordinates(lat: float, lon: float) -> Dict[str, str]:
    """
    좌표를 기반으로 날씨 정보를 조회합니다.

    Args:
        lat (float): 위도
        lon (float): 경도

    Returns:
        Dict[str, str]: 날씨 정보
    """
    try:
        # Open-Meteo API (무료, API 키 불필요)
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m",
            "timezone": "Asia/Seoul",
            "forecast_days": 1,
        }

        response = requests.get(url, params=params, timeout=10)

        if response.status_code == 200:
            data = response.json()
            current = data.get("current", {})

            # Weather code를 한국어 설명으로 변환
            weather_code = current.get("weather_code", 0)
            weather_desc = get_weather_description(weather_code)

            return {
                "temperature": f"{current.get('temperature_2m', 'N/A')}°C",
                "humidity": f"{current.get('relative_humidity_2m', 'N/A')}%",
                "wind_speed": f"{current.get('wind_speed_10m', 'N/A')} km/h",
                "condition": weather_desc,
                "status": "success",
            }
        else:
            return {
                "temperature": "조회 실패",
                "humidity": "조회 실패",
                "wind_speed": "조회 실패",
                "condition": "조회 실패",
                "status": "error",
            }
    except Exception as e:
        return {
            "temperature": "조회 실패",
            "humidity": "조회 실패",
            "wind_speed": "조회 실패",
            "condition": f"오류: {str(e)}",
            "status": "error",
        }


def get_weather_description(weather_code: int) -> str:
    """
    날씨 코드를 한국어 설명으로 변환합니다.

    Args:
        weather_code (int): WMO 날씨 코드

    Returns:
        str: 날씨 설명
    """
    weather_codes = {
        0: "맑음",
        1: "대체로 맑음",
        2: "부분적으로 흐림",
        3: "흐림",
        45: "안개",
        48: "서리 안개",
        51: "가벼운 이슬비",
        53: "보통 이슬비",
        55: "강한 이슬비",
        56: "가벼운 얼음 이슬비",
        57: "강한 얼음 이슬비",
        61: "약한 비",
        63: "보통 비",
        65: "강한 비",
        66: "가벼운 얼음비",
        67: "강한 얼음비",
        71: "약한 눈",
        73: "보통 눈",
        75: "강한 눈",
        77: "진눈깨비",
        80: "약한 소나기",
        81: "보통 소나기",
        82: "강한 소나기",
        85: "약한 눈 소나기",
        86: "강한 눈 소나기",
        95: "뇌우",
        96: "약한 우박을 동반한 뇌우",
        99: "강한 우박을 동반한 뇌우",
    }
    return weather_codes.get(weather_code, "알 수 없음")


def get_weather_by_address(address: str) -> Dict[str, str]:
    """
    주소를 기반으로 날씨 정보를 조회합니다.

    Args:
        address (str): 조회할 주소

    Returns:
        Dict[str, str]: 날씨 정보
    """
    coordinates = get_coordinates_by_address(address)

    if coordinates is None:
        return {
            "temperature": "주소 조회 실패",
            "humidity": "주소 조회 실패",
            "wind_speed": "주소 조회 실패",
            "condition": "주소를 찾을 수 없습니다",
            "status": "address_error",
            "address": address,
        }

    weather = get_weather_by_coordinates(coordinates["lat"], coordinates["lon"])
    weather["address"] = address
    return weather


def format_weather_info_text(weather_info: Dict[str, str]) -> str:
    """
    날씨 정보를 텍스트 형식으로 포맷팅합니다.

    Args:
        weather_info (Dict[str, str]): get_weather_by_address()에서 반환된 날씨 정보

    Returns:
        str: 포맷팅된 날씨 정보 텍스트
    """
    address = weather_info.get("address", "알 수 없는 위치")

    if weather_info.get("status") == "address_error":
        return f"""
{address} 날씨 정보:
- 주소를 찾을 수 없습니다.
"""

    return f"""
{address} 날씨 정보:
- 기온: {weather_info.get("temperature", "N/A")}
- 습도: {weather_info.get("humidity", "N/A")}
- 풍속: {weather_info.get("wind_speed", "N/A")}
- 날씨: {weather_info.get("condition", "N/A")}
"""


def format_weather_info_html(weather_info: Dict[str, str]) -> str:
    """
    날씨 정보를 HTML 형식으로 포맷팅합니다.

    Args:
        weather_info (Dict[str, str]): get_weather_by_address()에서 반환된 날씨 정보

    Returns:
        str: 포맷팅된 날씨 정보 HTML
    """
    address = weather_info.get("address", "알 수 없는 위치")

    if weather_info.get("status") == "address_error":
        return f"""
<h3>{address} 날씨 정보</h3>
<p><strong>⚠️ 주소를 찾을 수 없습니다.</strong></p>
"""

    return f"""
<h3>{address} 날씨 정보</h3>
<ul>
    <li><strong>🌡️ 기온:</strong> {weather_info.get("temperature", "N/A")}</li>
    <li><strong>💧 습도:</strong> {weather_info.get("humidity", "N/A")}</li>
    <li><strong>💨 풍속:</strong> {weather_info.get("wind_speed", "N/A")}</li>
    <li><strong>🌤️ 날씨:</strong> {weather_info.get("condition", "N/A")}</li>
</ul>
"""
