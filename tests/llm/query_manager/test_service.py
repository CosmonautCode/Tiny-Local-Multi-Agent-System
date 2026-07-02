from app.llm.agent_manager.service import AgentManager
from app.llm.query_manager.service import QueryManager


class FakeLLM:
    def __init__(self):
        self.calls = []

    def create_chat_completion(self, **kwargs):
        self.calls.append(kwargs)
        return {
            "choices": [{"message": {"content": '"key": "value"}'}}],
            "usage": {"completion_tokens": 3},
        }


def _agent_manager():
    am = AgentManager()
    am.agents = [
        {"id": "system_synthesizer", "name": "Synth", "system_prompt": "sp", "phase1_prompt": "extract", "phase2_prompt": "merge"},
        {"id": "a", "name": "Alpha", "system_prompt": "sp-a", "specialty": "test"},
        {"id": "b", "name": "Beta", "system_prompt": "sp-b", "specialty": "test"},
    ]
    am.llm = FakeLLM()
    return am


def test_process_query_runs_all_three_phases():
    am = _agent_manager()
    qm = QueryManager(am)
    qm.process_query("How do I build X?")
    assert len(am.llm.calls) == 1 + 2 + 1
