from app.config import get_settings
from app.llm.agent_manager.functions.synthesis import synthesize_report


class FakeLLM:
    def __init__(self):
        self.calls = []

    def create_chat_completion(self, **kwargs):
        self.calls.append(kwargs)
        return {"choices": [{"message": {"content": "spec"}}], "usage": {"completion_tokens": 10}}


def test_synthesis_clamps_negative_max_tokens_to_min():
    llm = FakeLLM()
    settings = get_settings()
    huge_opinions = [{"name": "A", "response": "x", "est_tokens": settings.PHASE3_TOKEN_BUDGET * 10}]
    synthesize_report(llm, "sys", huge_opinions)
    assert llm.calls[0]["max_tokens"] == settings.PHASE3_MIN_OUTPUT_TOKENS


def test_synthesis_returns_report_and_summed_tokens():
    llm = FakeLLM()
    opinions = [{"name": "A", "response": "x", "est_tokens": 5}, {"name": "B", "response": "y", "est_tokens": 7}]
    report, tokens = synthesize_report(llm, "sys", opinions, token_budget=2048)
    assert report == "spec"
    assert tokens == 5 + 7 + 10


def test_opinion_truncation_uses_configured_width(monkeypatch):
    llm = FakeLLM()
    from app.llm.agent_manager.functions import synthesis
    fake_settings = synthesis.get_settings().model_copy(update={"OPINION_TRUNCATE_CHARS": 3})
    monkeypatch.setattr(synthesis, "get_settings", lambda: fake_settings)
    monkeypatch.setattr("app.llm.agent_manager.functions.llm_call.get_settings", lambda: fake_settings)
    opinions = [{"name": "A", "response": "abcdefgh", "est_tokens": 0}]
    synthesize_report(llm, "sys", opinions, token_budget=2048)
    user_msg = llm.calls[0]["messages"][1]["content"]
    assert "[A] abc" in user_msg
    assert "abcd" not in user_msg
