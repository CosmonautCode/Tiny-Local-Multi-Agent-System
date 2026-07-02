import json

from app.config import get_settings
from app.llm.engine.service import load_llm


class AgentManager:
    """Owns the agent catalog and the shared Llama instance."""

    def __init__(self):
        self.agents: list[dict] = []
        self.llm = None

    def load(self):
        """Read agent catalog from disk and initialize a single LLM instance."""
        path = get_settings().AGENTS_PATH
        try:
            with open(path, "r", encoding="utf-8") as f:
                config = json.load(f)
        except (OSError, json.JSONDecodeError) as e:
            raise RuntimeError(f"Cannot load agents file {path}: {e}") from e
        if "user_agents" not in config:
            raise ValueError(f"Agents file missing 'user_agents' key: {path}")
        self.agents = config["user_agents"]
        if not self.agents:
            raise ValueError(f"Agents file has no agents: {path}")
        self.llm = load_llm()

    def find_synthesizer(self) -> dict:
        """Return the synthesizer agent config or raise if missing."""
        sid = get_settings().SYNTHESIZER_ID
        for agent in self.agents:
            if agent.get("id") == sid:
                return agent
        raise ValueError(f"Synthesizer agent id '{sid}' not found in agents catalog")

    def specialists(self) -> list[dict]:
        """Return every agent except the synthesizer."""
        sid = get_settings().SYNTHESIZER_ID
        return [a for a in self.agents if a.get("id") != sid]
