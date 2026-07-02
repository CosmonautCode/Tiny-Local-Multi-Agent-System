from pathlib import Path

import pytest

from app.llm.engine import service as engine_service


def test_load_llm_raises_when_model_missing(monkeypatch):
    fake_settings = engine_service.get_settings().model_copy(update={"MODEL_FILENAME": "no_such.gguf"})
    monkeypatch.setattr(engine_service, "get_settings", lambda: fake_settings)
    assert isinstance(fake_settings.MODEL_PATH, Path)
    with pytest.raises(FileNotFoundError) as exc:
        engine_service.load_llm()
    assert str(fake_settings.MODEL_PATH) in str(exc.value)


def test_load_llm_forwards_settings(monkeypatch, tmp_path):
    model_file = tmp_path / "m.gguf"
    model_file.write_bytes(b"x")
    called = {}

    class FakeLlama:
        def __init__(self, **kwargs):
            called.update(kwargs)

    monkeypatch.setattr(engine_service, "Llama", FakeLlama)
    fake_settings = engine_service.get_settings().model_copy(update={
        "MODEL_CONTEXT": 999,
        "MODEL_THREADS": 4,
        "MODEL_GPU_LAYERS": 0,
        "MODEL_VERBOSE": True,
        "MODEL_CHAT_FORMAT": "chatml",
    })
    monkeypatch.setattr(type(fake_settings), "MODEL_PATH", property(lambda self: model_file))
    monkeypatch.setattr(engine_service, "get_settings", lambda: fake_settings)

    engine_service.load_llm()
    assert called["n_ctx"] == 999
    assert called["n_threads"] == 4
    assert called["n_gpu_layers"] == 0
    assert called["verbose"] is True
    assert called["chat_format"] == "chatml"
