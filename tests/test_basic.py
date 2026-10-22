import json
import os
import tempfile

import main


def test_load_state_missing_file(monkeypatch):
    monkeypatch.setattr(main, "STATE_FILE", os.path.join(tempfile.mkdtemp(), "state.json"))
    assert main.load_state() == {"installed": [], "hacks": []}


def test_save_and_load_state(monkeypatch):
    d = tempfile.mkdtemp()
    path = os.path.join(d, "state.json")
    monkeypatch.setattr(main, "STATE_FILE", path)
    main.save_state({"installed": ["gapps"], "hacks": []})
    assert main.load_state()["installed"] == ["gapps"]