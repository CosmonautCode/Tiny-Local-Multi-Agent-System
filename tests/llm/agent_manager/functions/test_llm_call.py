import pytest

from app.llm.agent_manager.functions.llm_call import call_llm, estimate_tokens


class FakeLLM:
    def __init__(self, content="ok", completion_tokens=None):
        self.content = content
        self.completion_tokens = completion_tokens
        self.calls = []

    def create_chat_completion(self, **kwargs):
        self.calls.append(kwargs)
        return {
            "choices": [{"message": {"content": self.content}}],
            "usage": {"completion_tokens": self.completion_tokens} if self.completion_tokens else {},
        }


def test_estimate_tokens_is_positive():
    assert estimate_tokens("") == 1
    assert estimate_tokens("a" * 400) >= 100


def test_call_llm_returns_content_and_tokens():
    llm = FakeLLM("hello", completion_tokens=42)
    response, tokens = call_llm(llm, "sys", "u", max_tokens=100, temperature=0.5)
    assert response == "hello"
    assert tokens == 42


def test_call_llm_forces_json_prefix():
    llm = FakeLLM('"k": 1}')
    response, _ = call_llm(llm, "sys", "u", max_tokens=100, temperature=0.5, force_json=True)
    assert response.startswith("{")


def test_call_llm_raises_on_empty_choices():
    class EmptyLLM:
        def create_chat_completion(self, **_):
            return {"choices": []}

    with pytest.raises(RuntimeError):
        call_llm(EmptyLLM(), "sys", "u", max_tokens=10, temperature=0.1)
