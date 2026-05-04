import pytest
from src.exporter.session import SessionManager

def test_login_with_cookie():
    manager = SessionManager("test-agent")
    cookie_str = "PHPSESSID=abc123def; other_cookie=xyz"
    
    result = manager.login(session_cookie=cookie_str)
    
    assert result is True
    assert manager.session.cookies.get("PHPSESSID") == "abc123def"
    assert manager.session.cookies.get("other_cookie") == "xyz"

def test_login_missing_creds():
    manager = SessionManager("test-agent")
    result = manager.login()
    assert result is False
