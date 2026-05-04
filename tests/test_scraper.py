import pytest
from unittest.mock import MagicMock
from src.exporter.scraper import IMDbScraper

def test_get_imdb_id_padding():
    # Mock session
    mock_session = MagicMock()
    mock_response = MagicMock()
    # Sample HTML with short IMDb ID link
    mock_response.status_code = 200
    mock_response.text = '<html><body><a href="https://www.imdb.com/title/tt123/">IMDb</a></body></html>'
    mock_session.get.return_value = mock_response

    scraper = IMDbScraper(mock_session)
    imdb_id = scraper.get_imdb_id(123)

    # Should be padded to tt0000123
    assert imdb_id == "tt0000123"

def test_get_imdb_id_already_long():
    mock_session = MagicMock()
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = '<html><body><a href="https://www.imdb.com/title/tt0439100/">IMDb</a></body></html>'
    mock_session.get.return_value = mock_response

    scraper = IMDbScraper(mock_session)
    imdb_id = scraper.get_imdb_id(123)

    assert imdb_id == "tt0439100"

def test_get_imdb_id_not_found():
    mock_session = MagicMock()
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = '<html><body>No links here</body></html>'
    mock_session.get.return_value = mock_response

    scraper = IMDbScraper(mock_session)
    imdb_id = scraper.get_imdb_id(123)

    assert imdb_id is None
