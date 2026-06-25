import click
import asyncio
from src.agent.graph import agent_graph
from src.agent.state import AgentState
from src.mcp.postgres_client import PostgresMCPClient
from src.mcp.database import init_db
from src.cli.ui import display_banner, display_history, display_info, console


@click.group()
def cli():
    pass


@cli.command()
def check_repo():
    display_banner()
    
    initial_state: AgentState = {
        "repo_url": "",
        "branch": "",
        "commit_hash": None,
        "commits": [],
        "diff_content": "",
        "analysis_results": {},
        "approval_status": "pending",
        "pr_url": None,
        "error": None,
        "session_id": None
    }
    
    try:
        result = asyncio.run(agent_graph.ainvoke(initial_state))
        
        if result.get("error"):
            console.print(f"\n[red]Agent completed with errors.[/red]")
        elif result.get("pr_url"):
            console.print(f"\n[green]✓ Agent completed successfully![/green]")
        else:
            console.print(f"\n[yellow]Agent completed without creating PR.[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Fatal error: {str(e)}[/red]")


@cli.command()
@click.option('--repo', default=None, help='Filter by repository URL')
@click.option('--limit', default=20, help='Number of records to show')
def list_history(repo, limit):
    display_banner()
    display_info("Fetching PR history...")
    
    try:
        with PostgresMCPClient() as db_client:
            history = db_client.query_history(repo_url=repo, limit=limit)
            display_history(history)
    except Exception as e:
        console.print(f"[red]Error fetching history: {str(e)}[/red]")


@cli.command()
def init():
    display_banner()
    display_info("Initializing database...")
    
    try:
        init_db()
        console.print("[green]✓ Database initialized successfully![/green]")
    except Exception as e:
        console.print(f"[red]Error initializing database: {str(e)}[/red]")


@cli.command()
def config():
    display_banner()
    console.print("\n[bold cyan]Configuration[/bold cyan]\n")
    
    from config.settings import settings
    
    console.print("[bold]GitHub Settings:[/bold]")
    console.print(f"  [dim]Token:[/dim] {'*' * 20 if settings.github_token else '[red]Not set[/red]'}")
    
    console.print("\n[bold]Database Settings:[/bold]")
    console.print(f"  [dim]Host:[/dim] {settings.postgres_host}")
    console.print(f"  [dim]Port:[/dim] {settings.postgres_port}")
    console.print(f"  [dim]Database:[/dim] {settings.postgres_db}")
    console.print(f"  [dim]User:[/dim] {settings.postgres_user}")
    
    console.print("\n[bold]LLM Settings:[/bold]")
    console.print(f"  [dim]API Key:[/dim] {'*' * 20 if settings.llm_api_key else '[yellow]Not set (optional)[/yellow]'}")
    console.print(f"  [dim]Base URL:[/dim] {settings.llm_base_url or '[yellow]Not set (optional)[/yellow]'}")
    console.print(f"  [dim]Model:[/dim] {settings.llm_model}")
    
    if not settings.llm_api_key:
        console.print("\n[yellow]Note: LLM features disabled. PR descriptions will be basic.[/yellow]")
        console.print("[yellow]To enable AI-generated descriptions, set LLM_API_KEY and LLM_BASE_URL in .env[/yellow]")
    
    console.print("\n[dim]To update configuration, edit the .env file[/dim]\n")


if __name__ == "__main__":
    cli()
