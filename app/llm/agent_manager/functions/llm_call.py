from app.config import get_settings


def estimate_tokens(text: str) -> int:
    """Rough token estimate: text length divided by characters-per-token."""
    return max(1, len(text) // get_settings().TOKEN_ESTIMATE_CHARS_PER_TOKEN)


def call_llm(
    llm,
    system_prompt: str,
    user_input: str,
    max_tokens: int,
    temperature: float,
    force_json: bool = False,
) -> tuple[str, int]:
    """Send one system+user turn through the LLM, optionally forcing a JSON prefix."""
    settings = get_settings()
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_input},
    ]
    if force_json:
        messages.append({"role": "assistant", "content": "{"})
    output = llm.create_chat_completion(
        messages=messages,
        max_tokens=max_tokens,
        temperature=temperature,
        top_p=settings.TOP_P,
    )
    if not output.get("choices"):
        raise RuntimeError("LLM returned no choices")
    response = output["choices"][0]["message"]["content"].strip()
    if force_json:
        response = "{" + response
    usage = output.get("usage") or {}
    tokens = usage.get("completion_tokens") or estimate_tokens(response)
    return response, tokens
