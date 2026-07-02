from rich.console import Console
from rich.panel import Panel

from app.config import get_settings
from app.llm.agent_manager.functions.llm_call import call_llm
from app.llm.agent_manager.functions.synthesis import synthesize_report
from app.llm.agent_manager.service import AgentManager


console = Console()


class QueryManager:
    """Runs the 3-phase pipeline (spec extraction, opinions, synthesis) for one query."""

    def __init__(self, agents: AgentManager):
        self.agents = agents
        self.settings = get_settings()

    def process_query(self, user_query: str) -> None:
        synth_agent = self.agents.find_synthesizer()
        llm = self.agents.llm
        spec_json, spec_tokens = self._phase1_extract_spec(llm, synth_agent, user_query)
        opinions, opinion_tokens = self._phase2_collect_opinions(llm, user_query)
        final_report, final_tokens = self._phase3_synthesize(llm, synth_agent, opinions)
        self._render_totals(spec_tokens + opinion_tokens + final_tokens)

    def _phase1_extract_spec(self, llm, synth_agent, user_query):
        with console.status("[bold magenta]Analyzing User Request...[/bold magenta]", spinner="dots"):
            spec, tokens = call_llm(
                llm,
                synth_agent["system_prompt"],
                synth_agent.get("phase1_prompt", "") + "\nQuery: " + user_query,
                max_tokens=self.settings.PHASE1_MAX_TOKENS,
                temperature=self.settings.PHASE1_TEMPERATURE,
                force_json=True,
            )
        preview = spec[: self.settings.PHASE1_PREVIEW_CHARS]
        console.print(Panel(
            f"[bold]Extracted Spec:[/bold]\n{preview}...",
            title="[bold cyan]Phase 1: Tech Spec Extraction[/bold cyan]",
            border_style="cyan",
        ))
        return spec, tokens

    def _phase2_collect_opinions(self, llm, user_query):
        opinions = []
        total = 0
        for agent in self.agents.specialists():
            with console.status(
                f"[bold magenta]Getting {agent['name']}'s opinion...[/bold magenta]",
                spinner="dots",
            ):
                text, tokens = call_llm(
                    llm,
                    agent["system_prompt"],
                    f"Topic: {user_query}",
                    max_tokens=self.settings.PHASE2_MAX_TOKENS,
                    temperature=self.settings.PHASE2_TEMPERATURE,
                )
            opinions.append({"name": agent["name"], "response": text, "est_tokens": tokens})
            total += tokens
            console.print(Panel(
                text,
                title=f"[bold cyan]{agent['name']} ({agent.get('specialty', 'expert')})[/bold cyan]",
                border_style="cyan",
            ))
        return opinions, total

    def _phase3_synthesize(self, llm, synth_agent, opinions):
        prompt = synth_agent.get("phase2_prompt", "Synthesize opinions into spec")
        with console.status("[bold magenta]Synthesizing final specification...[/bold magenta]", spinner="dots"):
            report, tokens = synthesize_report(
                llm,
                prompt,
                opinions,
                token_budget=self.settings.PHASE3_TOKEN_BUDGET,
            )
        console.print(Panel(
            report,
            title="[bold green]Final Technical Specification[/bold green]",
            border_style="green",
        ))
        return report, tokens

    def _render_totals(self, total_tokens: int) -> None:
        cap = self.settings.TOKEN_BUDGET_WARN
        color = "green" if total_tokens <= cap else "red"
        console.print(f"[{color}]Tokens: {total_tokens} / {cap}[/{color}]")
