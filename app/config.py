from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


APP_DIR = Path(__file__).resolve().parent


class Settings(BaseSettings):
    """Centralized settings for Tiny-Local-Multi-Agent-System."""

    model_config = SettingsConfigDict(env_file=".env", env_prefix="TLMA_", extra="ignore")

    MODEL_FILENAME: str = "qwen2.5-1.5b-instruct-q8_0.gguf"
    MODEL_CONTEXT: int = 8192
    MODEL_THREADS: int = 8
    MODEL_GPU_LAYERS: int = -1
    MODEL_CHAT_FORMAT: str = "chatml"
    MODEL_VERBOSE: bool = False

    SYNTHESIZER_ID: str = "system_synthesizer"
    AGENTS_FILENAME: str = "agents.json"

    TOP_P: float = 0.9

    PHASE1_MAX_TOKENS: int = 2000
    PHASE1_TEMPERATURE: float = 0.1
    PHASE1_PREVIEW_CHARS: int = 500

    PHASE2_MAX_TOKENS: int = 500
    PHASE2_TEMPERATURE: float = 0.3

    PHASE3_TOKEN_BUDGET: int = 2048
    PHASE3_TEMPERATURE: float = 0.0
    PHASE3_RESERVE_TOKENS: int = 500
    PHASE3_MIN_OUTPUT_TOKENS: int = 128
    OPINION_TRUNCATE_CHARS: int = 2000

    TOKEN_BUDGET_WARN: int = 8192
    TOKEN_ESTIMATE_CHARS_PER_TOKEN: int = 4

    @property
    def MODEL_PATH(self) -> Path:
        return APP_DIR / "models" / self.MODEL_FILENAME

    @property
    def AGENTS_PATH(self) -> Path:
        return APP_DIR / "llm" / "agent_manager" / self.AGENTS_FILENAME


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
