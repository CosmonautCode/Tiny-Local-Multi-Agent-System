import json

import pytest

from app.llm.agent_manager import service as am_service
from app.llm.agent_manager.service import AgentManager


def _write_agents(tmp_path, payload):
    path = tmp_path / "agents.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def _stub_settings(monkeypatch, path):
    settings = am_service.get_settings().model_copy()
    monkeypatch.setattr(type(settings), "AGENTS_PATH", property(lambda self: path))
    monkeypatch.setattr(am_service, "get_settings", lambda: settings)
    return settings


def test_load_requires_user_agents_key(monkeypatch, tmp_path):
    path = _write_agents(tmp_path, {"nope": []})
    _stub_settings(monkeypatch, path)
    monkeypatch.setattr(am_service, "load_llm", lambda: object())
    with pytest.raises(ValueError, match="user_agents"):
        AgentManager().load()


def test_load_rejects_empty_agents(monkeypatch, tmp_path):
    path = _write_agents(tmp_path, {"user_agents": []})
    _stub_settings(monkeypatch, path)
    monkeypatch.setattr(am_service, "load_llm", lambda: object())
    with pytest.raises(ValueError, match="no agents"):
        AgentManager().load()


def test_find_synthesizer_and_specialists(monkeypatch, tmp_path):
    path = _write_agents(tmp_path, {"user_agents": [
        {"id": "system_synthesizer", "name": "S", "system_prompt": "sp"},
        {"id": "a", "name": "A", "system_prompt": "sp"},
        {"id": "b", "name": "B", "system_prompt": "sp"},
    ]})
    _stub_settings(monkeypatch, path)
    monkeypatch.setattr(am_service, "load_llm", lambda: "fake-llm")
    am = AgentManager()
    am.load()
    assert am.llm == "fake-llm"
    assert am.find_synthesizer()["id"] == "system_synthesizer"
    assert [a["id"] for a in am.specialists()] == ["a", "b"]


def test_find_synthesizer_raises_when_missing(monkeypatch, tmp_path):
    path = _write_agents(tmp_path, {"user_agents": [{"id": "x", "name": "X", "system_prompt": "sp"}]})
    _stub_settings(monkeypatch, path)
    monkeypatch.setattr(am_service, "load_llm", lambda: object())
    am = AgentManager()
    am.load()
    with pytest.raises(ValueError, match="Synthesizer"):
        am.find_synthesizer()
