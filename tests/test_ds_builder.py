import pytest
from webapp.services.ds_builder import build_ds_from_notes
import json
from pathlib import Path
import tempfile

def test_build_ds_from_notes_basic():
    # Arrange: create dummy notes
    notes = [
        {"pitch": "C4", "duration": 1.0, "phoneme": "k"},
        {"pitch": "D4", "duration": 0.5, "phoneme": "d"},
        {"pitch": "E4", "duration": 0.75, "phoneme": "e"},
    ]
    
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "test.ds"
        
        # Act: build ds file
        build_ds_from_notes(notes, output_path)
        
        # Assert: check contents
        with open(output_path, "r", encoding="utf-8") as f:
            ds = json.load(f)
        
        assert "ph_seq" in ds
        assert "ph_num" in ds
        assert ds["ph_seq"] == "k d e"
        assert ds["ph_num"] == 3
        assert ds["note_seq"] == "C4 D4 E4"
        assert ds["input_type"] == "phoneme"
