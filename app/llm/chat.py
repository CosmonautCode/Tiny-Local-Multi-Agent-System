from rich.console import Console
from rich.panel import Panel

from app.llm.agent_manager.service import AgentManager
from app.llm.query_manager.service import QueryManager


console = Console()


class ChatSystem:
    """UI shell for the multi-expert REPL."""

    def __init__(self):
        self.agent_manager = AgentManager()
        self.query_manager: QueryManager | None = None

    def load_agents(self):
        self.agent_manager.load()
        self.query_manager = QueryManager(self.agent_manager)

    def chat_loop(self):
        """Main loop: user query → tech spec extraction → agent opinions → final synthesis."""
        console.clear()
        console.rule(
            "[bold blue]Multi-Expert Technical Specification System[/bold blue]",
            style="bold blue",
        )
        console.print(Panel.fit(
            "[bold green]Ready[/bold green]\nType [bold yellow]'exit'[/bold yellow] to quit",
            title="[bold cyan]Status[/bold cyan]",
            border_style="green",
        ))
        console.print(Panel.fit(
            "[bold magenta]Experts:[/bold magenta]\n"
            + "\n".join(a["name"] for a in self.agent_manager.specialists()),
            border_style="magenta",
        ))
        while True:
            user_query = console.input("[bold cyan]You > [/bold cyan] ")
            if not user_query.strip():
                continue
            if user_query.lower() in {"exit", "quit"}:
                console.print("[bold red]Goodbye![/bold red]")
                break
            self.query_manager.process_query(user_query)
