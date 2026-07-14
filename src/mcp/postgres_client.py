from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
from src.mcp.database import (
    Repository, CodeChange, AnalysisResult, PRRequest,
    AgentState as AgentStateModel, UserSession, get_db
)


class PostgresMCPClient:
    def __init__(self):
        self.db_generator = get_db()
        self.db: Optional[Session] = None
    
    def __enter__(self):
        self.db = next(self.db_generator)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.db:
            self.db.close()
    
    def save_state(self, request_id: str, state_data: Dict[str, Any], checkpoint: Optional[str] = None) -> int:
        if not self.db:
            raise RuntimeError("Database session not initialized. Use context manager.")
        
        existing = self.db.query(AgentStateModel).filter(
            AgentStateModel.request_id == request_id
        ).first()
        
        if existing:
            existing.state_data = state_data
            existing.checkpoint = checkpoint
            existing.updated_at = datetime.utcnow()
            self.db.commit()
            return existing.id
        else:
            agent_state = AgentStateModel(
                request_id=request_id,
                state_data=state_data,
                checkpoint=checkpoint
            )
            self.db.add(agent_state)
            self.db.commit()
            self.db.refresh(agent_state)
            return agent_state.id
    
    def load_state(self, request_id: str) -> Optional[Dict[str, Any]]:
        if not self.db:
            raise RuntimeError("Database session not initialized. Use context manager.")
        
        agent_state = self.db.query(AgentStateModel).filter(
            AgentStateModel.request_id == request_id
        ).first()
        
        if agent_state:
            return {
                "id": agent_state.id,
                "request_id": agent_state.request_id,
                "state_data": agent_state.state_data,
                "checkpoint": agent_state.checkpoint,
                "created_at": agent_state.created_at.isoformat(),
                "updated_at": agent_state.updated_at.isoformat()
            }
        return None
    
    def save_repository(self, repo_url: str, last_checked_commit: Optional[str] = None) -> int:
        if not self.db:
            raise RuntimeError("Database session not initialized. Use context manager.")
        
        existing = self.db.query(Repository).filter(Repository.repo_url == repo_url).first()
        
        if existing:
            if last_checked_commit:
                existing.last_checked_commit = last_checked_commit
                existing.updated_at = datetime.utcnow()
            self.db.commit()
            return existing.id
        else:
            repo = Repository(repo_url=repo_url, last_checked_commit=last_checked_commit)
            self.db.add(repo)
            self.db.commit()
            self.db.refresh(repo)
            return repo.id
    
    def get_repository(self, repo_url: str) -> Optional[Dict[str, Any]]:
        if not self.db:
            raise RuntimeError("Database session not initialized. Use context manager.")
        
        repo = self.db.query(Repository).filter(Repository.repo_url == repo_url).first()
        if repo:
            return {
                "id": repo.id,
                "repo_url": repo.repo_url,
                "last_checked_commit": repo.last_checked_commit,
                "created_at": repo.created_at.isoformat(),
                "updated_at": repo.updated_at.isoformat()
            }
        return None
    
    def save_code_change(
        self, 
        repo_id: int, 
        commit_hash: str, 
        branch: str, 
        author: str, 
        timestamp: datetime
    ) -> int:
        if not self.db:
            raise RuntimeError("Database session not initialized. Use context manager.")
        
        code_change = CodeChange(
            repo_id=repo_id,
            commit_hash=commit_hash,
            branch=branch,
            author=author,
            timestamp=timestamp
        )
        self.db.add(code_change)
        self.db.commit()
        self.db.refresh(code_change)
        return code_change.id
    
    def save_analysis_result(
        self, 
        change_id: int, 
        issues_found: Dict[str, Any], 
        suggestions: Optional[str] = None, 
        score: Optional[int] = None
    ) -> int:
        if not self.db:
            raise RuntimeError("Database session not initialized. Use context manager.")
        
        analysis = AnalysisResult(
            change_id=change_id,
            issues_found=issues_found,
            suggestions=suggestions,
            score=score
        )
        self.db.add(analysis)
        self.db.commit()
        self.db.refresh(analysis)
        return analysis.id
    
    def save_pr_request(
        self, 
        change_id: int, 
        status: str, 
        pr_url: Optional[str] = None,
        created_by: Optional[str] = None,
        approval_timestamp: Optional[datetime] = None
    ) -> int:
        if not self.db:
            raise RuntimeError("Database session not initialized. Use context manager.")
        
        pr_request = PRRequest(
            change_id=change_id,
            status=status,
            pr_url=pr_url,
            created_by=created_by,
            approval_timestamp=approval_timestamp
        )
        self.db.add(pr_request)
        self.db.commit()
        self.db.refresh(pr_request)
        return pr_request.id
    
    def query_history(self, repo_url: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        if not self.db:
            raise RuntimeError("Database session not initialized. Use context manager.")
        
        query = self.db.query(PRRequest).join(CodeChange).join(Repository)
        
        if repo_url:
            query = query.filter(Repository.repo_url == repo_url)
        
        pr_requests = query.order_by(PRRequest.created_at.desc()).limit(limit).all()
        
        results = []
        for pr in pr_requests:
            results.append({
                "id": pr.id,
                "status": pr.status,
                "pr_url": pr.pr_url,
                "created_by": pr.created_by,
                "approval_timestamp": pr.approval_timestamp.isoformat() if pr.approval_timestamp else None,
                "created_at": pr.created_at.isoformat(),
                "commit_hash": pr.code_change.commit_hash,
                "branch": pr.code_change.branch,
                "author": pr.code_change.author,
                "repo_url": pr.code_change.repository.repo_url
            })
        
        return results
    
    def update_status(self, pr_request_id: int, status: str) -> bool:
        if not self.db:
            raise RuntimeError("Database session not initialized. Use context manager.")
        
        pr_request = self.db.query(PRRequest).filter(PRRequest.id == pr_request_id).first()
        if pr_request:
            pr_request.status = status
            self.db.commit()
            return True
        return False
    
    def create_session(self, repo_url: str, status: str = "started") -> int:
        if not self.db:
            raise RuntimeError("Database session not initialized. Use context manager.")
        
        session = UserSession(repo_url=repo_url, status=status)
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session.id
    
    def complete_session(self, session_id: int, status: str = "completed") -> bool:
        if not self.db:
            raise RuntimeError("Database session not initialized. Use context manager.")
        
        session = self.db.query(UserSession).filter(UserSession.id == session_id).first()
        if session:
            session.completed_at = datetime.utcnow()
            session.status = status
            self.db.commit()
            return True
        return False
