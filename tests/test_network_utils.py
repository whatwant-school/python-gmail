from module import network_utils


def test_get_local_ip_format():
    ip = network_utils.get_local_ip()
    assert isinstance(ip, str)
    assert ip != ""


def test_get_public_ip_format():
    ip = network_utils.get_public_ip()
    assert isinstance(ip, str)
    assert ip != ""


def test_get_ip_info_keys():
    info = network_utils.get_ip_info()
    assert "local_ip" in info
    assert "public_ip" in info


def test_format_ip_info_text():
    info = {"local_ip": "127.0.0.1", "public_ip": "8.8.8.8"}
    text = network_utils.format_ip_info_text(info)
    assert "127.0.0.1" in text
    assert "8.8.8.8" in text


def test_format_ip_info_html():
    info = {"local_ip": "127.0.0.1", "public_ip": "8.8.8.8"}
    html = network_utils.format_ip_info_html(info)
    assert "<ul>" in html
    assert "127.0.0.1" in html
    assert "8.8.8.8" in html
