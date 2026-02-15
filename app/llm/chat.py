from rich.console import Console
from rich.panel import Panel
from pathlib import Path
from app.llm.agent_manager.service import AgentManager
from app.llm.query_manager.service import QueryManager

console = Console()

class ChatSystem(QueryManager, AgentManager):

    def chat_loop(self):
        """Main loop: user query > tech spec extraction > agent opinions > final synthesis."""
        console.clear()
        console.rule("[bold blue]Multi-Expert Technical Specification System[/bold blue]", style="bold blue")
        console.print(Panel.fit(
            "[bold green]Ready[/bold green]\nType [bold yellow]'exit'[/bold yellow] to quit",
            title="[bold cyan]Status[/bold cyan]", border_style="green"
        ))

        agent_names = [a["name"] for a in self.agents if a.get("id") != "system_synthesizer"]
        console.print(Panel.fit(
            f"[bold magenta]Experts:[/bold magenta]\n" + "\n".join(agent_names),
            border_style="magenta"
        ))

        while True:
            user_query = console.input("[bold cyan]You > [/bold cyan] ")
            if user_query.lower() in {"exit", "quit"}:
                console.print("[bold red]Goodbye![/bold red]")
                break

            #with console.status("[bold magenta]Analyzing...[/bold magenta]", spinner="dots"):
            self.process_query(user_query)

