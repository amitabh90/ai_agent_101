from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.syntax import Syntax
from rich.prompt import Prompt, Confirm
from typing import Dict, Any, List, Optional
import inquirer


console = Console()


def display_banner():
    banner = """
    ╔═════════════════════════════════════════════════════╗
    ║         AI PR Agent - Code Quality Assistant          ║
    ║              Powered by LangGraph & MCP               ║
    ╚═════════════════════════════════════════════════════╝
    """
    console.print(banner, style="bold cyan")


def prompt_repo_url(history: List[str] = None) -> str:
    console.print("\n[bold]Repository Selection[/bold]", style="cyan")
    
    if history:
        questions = [
            inquirer.List(
                'choice',
                message="Select repository or enter new",
                choices=history + ['Enter new repository URL'],
            ),
        ]
        answers = inquirer.prompt(questions)
        
        if answers and answers['choice'] != 'Enter new repository URL':
            return answers['choice']
    
    return Prompt.ask("Enter repository URL", default="https://github.com/user/repo")


def prompt_branch(branches: List[str]) -> str:
    if not branches:
        return Prompt.ask("Enter branch name", default="main")
    
    questions = [
        inquirer.List(
            'branch',
            message="Select branch",
            choices=branches,
        ),
    ]
    answers = inquirer.prompt(questions)
    return answers['branch'] if answers else "main"


def prompt_commit_range() -> str:
    questions = [
        inquirer.List(
            'range',
            message="Check commits",
            choices=[
                'Since last check',
                'Last 10 commits',
                'Last 30 commits',
                'Specific commit hash'
            ],
        ),
    ]
    answers = inquirer.prompt(questions)
    
    if answers and answers['range'] == 'Specific commit hash':
        return Prompt.ask("Enter commit hash")
    
    return answers['range'] if answers else 'Since last check'


def display_progress(message: str):
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        progress.add_task(description=message, total=None)


def display_analysis_results(results: Dict[str, Any]):
    console.print("\n")
    
    panel_content = f"""
[bold]Files Changed:[/bold] {results.get('files_changed', 0)}
[bold]Lines Added:[/bold] [green]+{results.get('lines_added', 0)}[/green] | [bold]Lines Removed:[/bold] [red]-{results.get('lines_removed', 0)}[/red]
[bold]Issues Found:[/bold] {results.get('warnings', 0)} warnings, {results.get('errors', 0)} errors
[bold]Quality Score:[/bold] {results.get('score', 0)}/100
    """
    
    console.print(Panel(panel_content, title="Code Quality Analysis Results", border_style="cyan"))
    
    if results.get('issues'):
        table = Table(title="Issues Detected", show_header=True, header_style="bold magenta")
        table.add_column("File", style="cyan", no_wrap=False)
        table.add_column("Line", justify="right", style="yellow")
        table.add_column("Severity", justify="center")
        table.add_column("Message", no_wrap=False)
        table.add_column("Tool", justify="center", style="dim")
        
        for issue in results['issues'][:20]:
            severity_style = "red" if issue['severity'] == "error" else "yellow"
            severity_icon = "✗" if issue['severity'] == "error" else "⚠"
            
            table.add_row(
                issue.get('file', 'unknown'),
                str(issue.get('line', 0)),
                f"[{severity_style}]{severity_icon} {issue['severity']}[/{severity_style}]",
                issue.get('message', ''),
                issue.get('tool', '')
            )
        
        console.print("\n")
        console.print(table)
        
        if len(results['issues']) > 20:
            console.print(f"\n[dim]... and {len(results['issues']) - 20} more issues[/dim]")
    
    console.print(f"\n[bold]{results.get('summary', '')}[/bold]\n")


def display_commits(commits: List[Dict[str, Any]]):
    if not commits:
        console.print("[yellow]No new commits found.[/yellow]")
        return
    
    table = Table(title=f"Found {len(commits)} New Commits", show_header=True, header_style="bold green")
    table.add_column("Hash", style="cyan", no_wrap=True)
    table.add_column("Author", style="magenta")
    table.add_column("Message", no_wrap=False)
    table.add_column("Date", style="dim")
    
    for commit in commits[:10]:
        commit_sha = commit.get('sha', '')[:7]
        author = commit.get('commit', {}).get('author', {}).get('name', 'Unknown')
        message = commit.get('commit', {}).get('message', '').split('\n')[0][:60]
        date = commit.get('commit', {}).get('author', {}).get('date', '')[:10]
        
        table.add_row(commit_sha, author, message, date)
    
    console.print("\n")
    console.print(table)
    
    if len(commits) > 10:
        console.print(f"[dim]... and {len(commits) - 10} more commits[/dim]\n")


def prompt_approval() -> bool:
    console.print("\n")
    return Confirm.ask("[bold cyan]Create PR with these changes?[/bold cyan]", default=False)


def display_success(pr_url: str):
    console.print("\n")
    console.print(Panel(
        f"[bold green]✓ Pull Request Created Successfully![/bold green]\n\n"
        f"[cyan]URL:[/cyan] {pr_url}",
        border_style="green"
    ))


def display_error(error_message: str):
    console.print("\n")
    console.print(Panel(
        f"[bold red]✗ Error:[/bold red]\n\n{error_message}",
        border_style="red"
    ))


def display_info(message: str):
    console.print(f"[cyan]ℹ {message}[/cyan]")


def display_warning(message: str):
    console.print(f"[yellow]⚠ {message}[/yellow]")


def display_history(history: List[Dict[str, Any]]):
    if not history:
        console.print("[yellow]No PR history found.[/yellow]")
        return
    
    table = Table(title="PR Creation History", show_header=True, header_style="bold cyan")
    table.add_column("ID", justify="right", style="cyan")
    table.add_column("Repository", style="magenta", no_wrap=False)
    table.add_column("Branch", style="green")
    table.add_column("Status", justify="center")
    table.add_column("PR URL", no_wrap=False)
    table.add_column("Created", style="dim")
    
    for item in history[:20]:
        status_style = "green" if item['status'] == "approved" else "yellow"
        status_icon = "✓" if item['status'] == "approved" else "⊗"
        
        table.add_row(
            str(item['id']),
            item.get('repo_url', 'N/A'),
            item.get('branch', 'N/A'),
            f"[{status_style}]{status_icon} {item['status']}[/{status_style}]",
            item.get('pr_url', 'N/A') if item.get('pr_url') else '[dim]N/A[/dim]',
            item.get('created_at', '')[:10]
        )
    
    console.print("\n")
    console.print(table)
    
    if len(history) > 20:
        console.print(f"\n[dim]... and {len(history) - 20} more entries[/dim]")
