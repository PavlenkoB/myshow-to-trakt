import pytest
from unittest.mock import MagicMock, patch
from src.exporter.processor import DataProcessor

@pytest.fixture
def mock_deps():
    return {
        'session': MagicMock(),
        'scraper': MagicMock(),
        'cache': MagicMock(),
        'state_cache': MagicMock(),
        'episode_cache': MagicMock(),
        'ep_imdb_cache': MagicMock(),  # BUG-001: was missing, caused TypeError on every test
    }

def test_imdb_id_padding_in_metadata(mock_deps):
    processor = DataProcessor(**mock_deps)
    
    # Mock MyShows API response with short IMDb ID
    mock_meta = {
        'title': 'Test Show',
        'imdbId': '1234',
        'episodes': {}
    }
    
    # We'll test the logic inside process_all indirectly or test the internal processing
    # But let's check how processor handles padding
    
    # Manually trigger the padding logic check if possible or mock the fetch
    with patch.object(processor, 'fetch_metadata', return_value=mock_meta):
        with patch.object(processor, 'fetch_show_list', return_value={'1': {'watchStatus': 'watching'}}):
            # We just want to see if it saves correctly
            processor.state_cache.load.return_value = {}
            processor.episode_cache.load.return_value = {}
            
            # Run Stage 1 logic (Metadata)
            processor.process_all('tmp/test.csv', limit=1)
            
            # Check what was saved to state_cache
            args, _ = processor.state_cache.save.call_args
            saved_data = args[0]
            assert saved_data['1']['imdb_id'] == "tt0001234"

def test_rating_scaling_in_export(mock_deps, tmp_path):
    csv_file = tmp_path / "export.csv"
    processor = DataProcessor(**mock_deps)
    
    # Setup data in caches
    shows_data = {
        '1': {
            'title': 'Test Show',
            'imdb_id': 'tt1234567',
            'watchStatus': 'watching',
            'rating': 5, # MyShows scale 1-5
            'ep_map': {'101': {'s': 1, 'e': 1}}
        }
    }
    episodes_data = {
        '1': [{'s': 1, 'e': 1, 'date': '01.01.2024', 'rating': 4}] # Episode specific rating
    }
    
    processor.state_cache.load.return_value = shows_data
    processor.episode_cache.load.return_value = episodes_data
    processor.cache.get.return_value = None
    
    with patch.object(processor, 'fetch_show_list', return_value={'1': {'watchStatus': 'watching'}}):
        processor.process_all(str(csv_file))
        
        # Read the CSV to verify
        import csv
        with open(csv_file, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            
            assert len(rows) == 1
            assert rows[0]['type'] == 'episode'
            # Episode rating 4 * 2 = 8
            assert rows[0]['rating'] == '8'
            assert rows[0]['rated_at'] == '2024-01-01T12:00:00Z'
            # BUG-011: watchlisted_at must be empty for episode (history) rows
            assert rows[0]['watchlisted_at'] == ''

def test_watchlist_export(mock_deps, tmp_path):
    csv_file = tmp_path / "watchlist.csv"
    processor = DataProcessor(**mock_deps)
    
    shows_data = {
        '1': {
            'title': 'Later Show',
            'imdb_id': 'tt1234567',
            'watchStatus': 'later',
            'rating': 5,
            'ep_map': {}
        }
    }
    episodes_data = {'1': []} # No episodes watched
    
    processor.state_cache.load.return_value = shows_data
    processor.episode_cache.load.return_value = episodes_data
    
    with patch.object(processor, 'fetch_show_list', return_value={'1': {'watchStatus': 'later'}}):
        processor.process_all(str(csv_file))
        
        import csv
        with open(csv_file, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            
            assert len(rows) == 1
            assert rows[0]['type'] == 'show'
            assert rows[0]['watched_at'] == ''
            assert rows[0]['watchlisted_at'] != ''
            # For watchlist shows, we use show rating
            assert rows[0]['rating'] == '10'
