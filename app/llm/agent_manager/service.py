import json
from pathlib import Path
from app.llm.engine.service import load_multiple_instances



class AgentManager():
    """Multi-expert system orchestrator for technical specification generation."""
    def __init__(self):
        self.agents = []
        self.llms = []

    def load_agents(self):
        """Load agents from config and initialize LLM instances."""
        config_path = Path(__file__).parent / "agents.json"
        with open(config_path, "r") as f:
            config = json.load(f)
        self.agents = config["user_agents"]
        # Load only 1 LLM instance and reuse it for all agents (not one per agent)
        self.llms = load_multiple_instances(1)

    @staticmethod
    def _estimate_tokens(text):
        """Estimate tokens: ~4 chars per token (llama.cpp typical)."""
        return max(1, len(text) // 4)

    @staticmethod
    def call_llm(llm, system_prompt: str, user_input: str, max_tokens: int, temperature: int, force_json=False):
        """Unified LLM call method. Force JSON with completion prefix if needed."""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ]
        
        if force_json:
            messages.append({"role": "assistant", "content": "{"})
        
        output = llm.create_chat_completion(
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=0.9
        )
        
        response = output["choices"][0]["message"]["content"].strip()
        if force_json:
            response = "{" + response
        
        usage = output.get("usage") or {}
        est_tokens = usage.get("completion_tokens") or AgentManager._estimate_tokens(response)
        return response, est_tokens

    @staticmethod
    def synthesize_report(llm, synthesizer_prompt, agent_opinions, token_budget=8192):
        """Merge agent opinions into final technical specification."""
        
        summed_agent_tokens = sum(int(op.get('est_tokens', 0)) for op in agent_opinions)

        max_synthesis_output = token_budget - summed_agent_tokens - 500

        opinions_lines = [f"[{op['name']}] {op['response'][:200]}" for op in agent_opinions]
        user_msg = "Synthesize expert opinions into technical spec:\n\n" + "\n\n".join(opinions_lines)

        report, output_tokens = AgentManager.call_llm(
            llm, synthesizer_prompt, user_msg, 
            max_tokens=max_synthesis_output, temperature=0.0
        )
        
        return report, summed_agent_tokens + output_tokens
