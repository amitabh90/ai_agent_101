from typing import TypedDict, Optional, List, Dict, Any


class AgentState(TypedDict):
    repo_url: str
    branch: str
    commit_hash: Optional[str]
    commits: List[Dict[str, Any]]
    diff_content: str
    analysis_results: Dict[str, Any]
    approval_status: str
    pr_url: Optional[str]
    error: Optional[str]
    session_id: Optional[str]
