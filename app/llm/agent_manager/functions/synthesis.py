from app.config import get_settings
from app.llm.agent_manager.functions.llm_call import call_llm


def synthesize_report(
    llm,
    synthesizer_prompt: str,
    agent_opinions: list[dict],
    token_budget: int | None = None,
) -> tuple[str, int]:
    """Merge agent opinions into a single technical spec via one LLM call."""
    settings = get_settings()
    budget = token_budget if token_budget is not None else settings.PHASE3_TOKEN_BUDGET
    summed_agent_tokens = sum(int(op.get("est_tokens", 0)) for op in agent_opinions)
    max_output = max(
        settings.PHASE3_MIN_OUTPUT_TOKENS,
        budget - summed_agent_tokens - settings.PHASE3_RESERVE_TOKENS,
    )
    lines = [
        f"[{op['name']}] {op['response'][: settings.OPINION_TRUNCATE_CHARS]}"
        for op in agent_opinions
    ]
    user_msg = "Synthesize expert opinions into technical spec:\n\n" + "\n\n".join(lines)
    report, output_tokens = call_llm(
        llm,
        synthesizer_prompt,
        user_msg,
        max_tokens=max_output,
        temperature=settings.PHASE3_TEMPERATURE,
    )
    return report, summed_agent_tokens + output_tokens
