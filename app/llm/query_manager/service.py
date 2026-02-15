from rich.console import Console
from rich.panel import Panel
from app.llm.agent_manager.service import AgentManager

console = Console()

class QueryManager(AgentManager):

    def __init__(self):
        super().__init__()
        self.load_agents()


    def process_query(self, user_query):
        """Process user query: extract spec then get 3-point opinions then synthesize final report."""
        synth_agent = next((a for a in self.agents if a.get("id") == "system_synthesizer"), None)
        if not synth_agent:
            console.print("[red]Error: System Synthesizer not found[/red]")
            return

        synth_llm = self.llms[0]  # Use single shared instance

        # Phase 1: Extract tech spec from user query
        with console.status("[bold magenta]Analyzing User Request...[/bold magenta]", spinner="dots"):
            tech_spec_json, tech_spec_tokens = self.call_llm(
                synth_llm, synth_agent["system_prompt"], 
                synth_agent.get("phase1_prompt", "") + "\nQuery: " + user_query,
                max_tokens=2000,
                temperature=0.1,
                force_json=True
            )

        console.print(Panel(
            f"[bold]Extracted Spec:[/bold]\n{tech_spec_json[:500]}...",
            title="[bold cyan]Phase 1: Tech Spec Extraction[/bold cyan]", border_style="cyan"
        ))

        # Phase 2: Gather 3-point opinions from all specialist agents
        opinions = []
        total_tokens = tech_spec_tokens

        for idx, agent in enumerate(self.agents):
            if agent.get("id") == "system_synthesizer":
                continue

            llm = self.llms[0]  # Use single shared instance for all agents
            with console.status(f"[bold magenta]Getting {agent['name']}'s opinion...[/bold magenta]", spinner="dots"):
                opinion_text, opinion_tokens = self.call_llm(
                    llm, 
                    agent["system_prompt"], 
                    f"Topic: {user_query}", 
                    max_tokens=500, 
                    temperature=0.3
                )

            opinions.append({
                "name": agent["name"],
                "response": opinion_text,
                "est_tokens": opinion_tokens
            })
            total_tokens += opinion_tokens

            console.print(Panel(
                opinion_text, 
                title=f"[bold cyan]{agent['name']} ({agent.get('specialty', 'expert')})[/bold cyan]", 
                border_style="cyan"
            ))

        # Phase 3: Synthesize all opinions into final specification
        synth_prompt_phase2 = synth_agent.get("phase2_prompt", "Synthesize opinions into spec")
        with console.status("[bold magenta]Synthesizing final specification...[/bold magenta]", spinner="dots"):
            final_report, final_tokens = self.synthesize_report(
                synth_llm, 
                synth_prompt_phase2,
                opinions, 
                token_budget=2048
            )
        total_tokens += final_tokens

        console.print(Panel(
            final_report,
            title="[bold green]Final Technical Specification[/bold green]",
            border_style="green"
        ))

        status_color = "green" if total_tokens <= 8192 else "red"
        console.print(f"[{status_color}]Tokens: {total_tokens} / 8192[/{status_color}]")
