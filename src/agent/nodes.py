from typing import Dict, Any
from datetime import datetime
import uuid
from src.agent.state import AgentState
from src.mcp.github_client import GitHubMCPClient
from src.mcp.postgres_client import PostgresMCPClient
from src.mcp.database import CodeChange
from src.analysis.code_quality import CodeQualityAnalyzer
from src.agent.llm_client import generate_pr_description
from src.cli.ui import (
    prompt_repo_url, prompt_branch, prompt_commit_range,
    display_commits, display_analysis_results, prompt_approval,
    display_success, display_error, display_info, console
)


async def prompt_user_node(state: AgentState) -> AgentState:
    try:
        with PostgresMCPClient() as db_client:
            history = db_client.query_history(limit=10)
            repo_urls = list(set([h['repo_url'] for h in history]))
        
        repo_url = prompt_repo_url(repo_urls if repo_urls else None)
        state["repo_url"] = repo_url
        
        github_client = GitHubMCPClient()
        
        display_info("Fetching branches...")
        branches = await github_client.list_branches(repo_url)
        branch_names = [b['name'] for b in branches]
        
        branch = prompt_branch(branch_names)
        state["branch"] = branch
        
        commit_range = prompt_commit_range()
        state["commit_range"] = commit_range
        
        session_id = str(uuid.uuid4())
        state["session_id"] = session_id
        
        with PostgresMCPClient() as db_client:
            db_client.create_session(repo_url, status="started")
        
        return state
    except Exception as e:
        state["error"] = f"Error in prompt_user_node: {str(e)}"
        display_error(state["error"])
        return state


async def fetch_changes_node(state: AgentState) -> AgentState:
    try:
        github_client = GitHubMCPClient()
        repo_url = state["repo_url"]
        branch = state["branch"]
        
        display_info(f"Fetching commits from {repo_url} (branch: {branch})...")
        
        with PostgresMCPClient() as db_client:
            repo_data = db_client.get_repository(repo_url)
            last_commit = repo_data['last_checked_commit'] if repo_data else None
        
        commits = await github_client.list_commits(
            repo_url, 
            branch=branch,
            since=last_commit,
            per_page=30
        )
        
        if not commits:
            display_info("No new commits found.")
            state["commits"] = []
            state["diff_content"] = ""
            return state
        
        display_commits(commits)
        
        state["commits"] = commits
        
        if commits:
            latest_commit = commits[0]
            commit_detail = await github_client.get_commit_diff(repo_url, latest_commit['sha'])
            state["commit_hash"] = latest_commit['sha']
            state["diff_content"] = str(commit_detail.get('files', []))
            
            with PostgresMCPClient() as db_client:
                repo_id = db_client.save_repository(repo_url, latest_commit['sha'])
                
                commit_date = datetime.fromisoformat(
                    latest_commit['commit']['author']['date'].replace('Z', '+00:00')
                )
                
                db_client.save_code_change(
                    repo_id=repo_id,
                    commit_hash=latest_commit['sha'],
                    branch=branch,
                    author=latest_commit['commit']['author']['name'],
                    timestamp=commit_date
                )
        
        return state
    except Exception as e:
        state["error"] = f"Error in fetch_changes_node: {str(e)}"
        display_error(state["error"])
        return state


async def analyze_code_node(state: AgentState) -> AgentState:
    try:
        if not state.get("commits") or not state["commits"]:
            state["analysis_results"] = {
                "files_changed": 0,
                "issues": [],
                "score": 100,
                "summary": "No changes to analyze"
            }
            return state
        
        display_info("Analyzing code quality...")
        
        github_client = GitHubMCPClient()
        commit_hash = state["commit_hash"]
        repo_url = state["repo_url"]
        
        commit_detail = await github_client.get_commit_diff(repo_url, commit_hash)
        files = commit_detail.get('files', [])
        
        analyzer = CodeQualityAnalyzer()
        results = analyzer.analyze_diff("", files)
        
        state["analysis_results"] = results
        
        with PostgresMCPClient() as db_client:
            repo_data = db_client.get_repository(repo_url)
            if repo_data:
                changes = db_client.db.query(CodeChange).filter_by(
                    repo_id=repo_data['id'],
                    commit_hash=commit_hash
                ).first()
                
                if changes:
                    db_client.save_analysis_result(
                        change_id=changes.id,
                        issues_found=results,
                        suggestions=results.get('summary', ''),
                        score=results.get('score', 0)
                    )
        
        return state
    except Exception as e:
        state["error"] = f"Error in analyze_code_node: {str(e)}"
        display_error(state["error"])
        return state


async def display_results_node(state: AgentState) -> AgentState:
    try:
        results = state.get("analysis_results", {})
        display_analysis_results(results)
        return state
    except Exception as e:
        state["error"] = f"Error in display_results_node: {str(e)}"
        display_error(state["error"])
        return state


async def request_approval_node(state: AgentState) -> AgentState:
    try:
        approved = prompt_approval()
        state["approval_status"] = "approved" if approved else "rejected"
        
        if not approved:
            display_info("PR creation cancelled by user.")
        
        return state
    except Exception as e:
        state["error"] = f"Error in request_approval_node: {str(e)}"
        display_error(state["error"])
        return state


async def create_pr_node(state: AgentState) -> AgentState:
    try:
        display_info("Creating pull request...")
        
        github_client = GitHubMCPClient()
        repo_url = state["repo_url"]
        branch = state["branch"]
        commit_hash = state["commit_hash"]
        analysis = state.get("analysis_results", {})
        
        commits = state.get("commits", [])
        commit_messages = []
        if commits:
            commit_message = commits[0]['commit']['message'].split('\n')[0]
            commit_messages = [c['commit']['message'].split('\n')[0] for c in commits[:5]]
        else:
            commit_message = "Code quality improvements"
        
        pr_title = f"[Auto] {commit_message}"
        
        display_info("Generating PR description with AI...")
        ai_description = generate_pr_description(commit_messages, analysis)
        
        pr_body = f"""
## Automated PR - Code Quality Analysis

**Commit:** `{commit_hash[:7]}`
**Branch:** `{branch}`

{ai_description}

---

### Detailed Analysis
- **Files Changed:** {analysis.get('files_changed', 0)}
- **Lines Added:** +{analysis.get('lines_added', 0)}
- **Lines Removed:** -{analysis.get('lines_removed', 0)}
- **Quality Score:** {analysis.get('score', 0)}/100
- **Issues:** {analysis.get('errors', 0)} errors, {analysis.get('warnings', 0)} warnings

{analysis.get('summary', '')}

---
*This PR was automatically created by AI PR Agent*
"""
        
        pr_response = await github_client.create_pull_request(
            repo_url=repo_url,
            title=pr_title,
            body=pr_body,
            head=branch,
            base="main"
        )
        
        state["pr_url"] = pr_response.get('html_url', '')
        display_success(state["pr_url"])
        
        return state
    except Exception as e:
        state["error"] = f"Error in create_pr_node: {str(e)}"
        display_error(state["error"])
        return state


async def save_state_node(state: AgentState) -> AgentState:
    try:
        with PostgresMCPClient() as db_client:
            request_id = state.get("session_id", str(uuid.uuid4()))
            
            db_client.save_state(
                request_id=request_id,
                state_data=dict(state),
                checkpoint="completed"
            )
            
            repo_data = db_client.get_repository(state["repo_url"])
            if repo_data and state.get("commit_hash"):
                changes = db_client.db.query(CodeChange).filter_by(
                    repo_id=repo_data['id'],
                    commit_hash=state["commit_hash"]
                ).first()
                
                if changes:
                    db_client.save_pr_request(
                        change_id=changes.id,
                        status=state.get("approval_status", "unknown"),
                        pr_url=state.get("pr_url"),
                        created_by="ai_agent",
                        approval_timestamp=datetime.utcnow() if state.get("approval_status") == "approved" else None
                    )
            
            if state.get("session_id"):
                session_id = int(state["session_id"].split('-')[0], 16) % 1000000
                db_client.complete_session(
                    session_id=session_id,
                    status="completed" if not state.get("error") else "failed"
                )
        
        display_info("State saved to database.")
        return state
    except Exception as e:
        state["error"] = f"Error in save_state_node: {str(e)}"
        console.print(f"[yellow]Warning: Could not save state - {str(e)}[/yellow]")
        return state


async def handle_error_node(state: AgentState) -> AgentState:
    error = state.get("error", "Unknown error occurred")
    display_error(error)
    
    try:
        with PostgresMCPClient() as db_client:
            request_id = state.get("session_id", str(uuid.uuid4()))
            db_client.save_state(
                request_id=request_id,
                state_data=dict(state),
                checkpoint="error"
            )
    except:
        pass
    
    return state
