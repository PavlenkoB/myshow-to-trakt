import os
import json
import pytest
from src.exporter.cache import IMDbCache, StateCache

def test_imdb_cache_load_save(tmp_path):
    cache_file = tmp_path / "imdb.json"
    # Initial load of non-existent file
    cache = IMDbCache(str(cache_file))
    assert cache.data == {}
    
    cache.set("123", "tt0000123")
    assert cache.get("123") == "tt0000123"
    
    # Reload
    cache2 = IMDbCache(str(cache_file))
    assert cache2.get("123") == "tt0000123"

def test_state_cache_load_save(tmp_path):
    cache_file = tmp_path / "state.json"
    cache = StateCache(str(cache_file))
    
    # Load non-existent
    assert cache.load() is None
    
    data = {"1": {"title": "Test"}}
    cache.save(data)
    
    assert cache.load() == data

def test_cache_invalid_json(tmp_path):
    cache_file = tmp_path / "invalid.json"
    with open(cache_file, 'w') as f:
        f.write("invalid json")
        
    cache = IMDbCache(str(cache_file))
    assert cache.data == {}
    
    state_cache = StateCache(str(cache_file))
    assert state_cache.load() is None
