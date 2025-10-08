import pytest
from module import weather_utils

def test_get_coordinates_by_address_valid():
    coords = weather_utils.get_coordinates_by_address("서울")
    assert coords is None or ("lat" in coords and "lon" in coords)

def test_get_coordinates_by_address_invalid():
    coords = weather_utils.get_coordinates_by_address("!@#$%^&*")
    assert coords is None

def test_get_weather_by_coordinates_keys():
    # 위도, 경도는 서울 기준
    result = weather_utils.get_weather_by_coordinates(37.5665, 126.9780)
    assert "temperature" in result
    assert "humidity" in result
    assert "wind_speed" in result
    assert "condition" in result
    assert "status" in result
    assert "time_range" in result
    assert result["time_range"] == "19:00~21:00"

def test_get_weather_description():
    desc = weather_utils.get_weather_description(0)
    assert desc == "맑음"
    desc = weather_utils.get_weather_description(9999)
    assert desc == "알 수 없음"

def test_get_weather_by_address_keys():
    result = weather_utils.get_weather_by_address("서울")
    assert "temperature" in result
    assert "humidity" in result
    assert "wind_speed" in result
    assert "condition" in result
    assert "status" in result
    assert "address" in result
    assert "time_range" in result

def test_format_weather_info_text():
    info = {"address": "서울", "temperature": "20°C", "humidity": "50%", "wind_speed": "5 km/h", "condition": "맑음", "status": "success", "time_range": "19:00~21:00"}
    text = weather_utils.format_weather_info_text(info)
    assert "서울" in text
    assert "20°C" in text
    assert "맑음" in text
    assert "19:00~21:00" in text

def test_format_weather_info_html():
    info = {"address": "서울", "temperature": "20°C", "humidity": "50%", "wind_speed": "5 km/h", "condition": "맑음", "status": "success", "time_range": "19:00~21:00"}
    html = weather_utils.format_weather_info_html(info)
    assert "<ul>" in html
    assert "서울" in html
    assert "20°C" in html
    assert "맑음" in html
    assert "19:00~21:00" in html
