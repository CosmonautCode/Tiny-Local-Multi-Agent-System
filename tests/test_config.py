from app.config import APP_DIR, get_settings


def test_settings_singleton():
    assert get_settings() is get_settings()


def test_model_path_anchored_to_app_dir():
    s = get_settings()
    assert s.MODEL_PATH.parent == APP_DIR / "models"


def test_agents_path_points_to_agent_manager():
    s = get_settings()
    assert s.AGENTS_PATH.name == s.AGENTS_FILENAME
    assert s.AGENTS_PATH.parent.name == "agent_manager"


def test_defaults_are_sensible():
    s = get_settings()
    assert s.PHASE1_MAX_TOKENS > 0
    assert s.PHASE2_MAX_TOKENS > 0
    assert s.PHASE3_TOKEN_BUDGET > s.PHASE3_RESERVE_TOKENS
    assert s.PHASE3_MIN_OUTPUT_TOKENS > 0
