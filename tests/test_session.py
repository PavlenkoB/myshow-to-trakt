import pytest
from unittest.mock import MagicMock, patch
from src.exporter.session import SessionManager


def test_login_with_cookie():
    """Valid cookie: verification request succeeds → login returns True."""
    manager = SessionManager("test-agent")
    cookie_str = "PHPSESSID=abc123def; other_cookie=xyz"

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    # BUG-009: patch the internal session.get so no real HTTP call is made
    with patch.object(manager.session, 'get', return_value=mock_resp):
        result = manager.login(session_cookie=cookie_str)

    assert result is True
    assert manager.session.cookies.get("PHPSESSID") == "abc123def"
    assert manager.session.cookies.get("other_cookie") == "xyz"


def test_login_with_expired_cookie():
    """Expired cookie: verification request returns 403 → login returns False."""
    manager = SessionManager("test-agent")
    cookie_str = "PHPSESSID=expired"

    mock_resp = MagicMock()
    mock_resp.status_code = 403
    with patch.object(manager.session, 'get', return_value=mock_resp):
        result = manager.login(session_cookie=cookie_str)

    assert result is False


def test_login_missing_creds():
    manager = SessionManager("test-agent")
    result = manager.login()
    assert result is False
