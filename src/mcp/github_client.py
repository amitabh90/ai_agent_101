import httpx
from typing import List, Dict, Any, Optional
from datetime import datetime
from config.settings import settings


class GitHubMCPClient:
    def __init__(self, token: Optional[str] = None):
        self.token = token or settings.github_token
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }
    
    def _parse_repo_url(self, repo_url: str) -> tuple[str, str]:
        if repo_url.startswith("https://github.com/"):
            repo_url = repo_url.replace("https://github.com/", "")
        if repo_url.endswith(".git"):
            repo_url = repo_url[:-4]
        parts = repo_url.split("/")
        if len(parts) >= 2:
            return parts[0], parts[1]
        raise ValueError(f"Invalid repository URL: {repo_url}")
    
    async def list_commits(
        self, 
        repo_url: str, 
        branch: str = "main", 
        since: Optional[str] = None,
        per_page: int = 30
    ) -> List[Dict[str, Any]]:
        owner, repo = self._parse_repo_url(repo_url)
        url = f"{self.base_url}/repos/{owner}/{repo}/commits"
        params = {"sha": branch, "per_page": per_page}
        if since:
            params["since"] = since
        
        async with httpx.AsyncClient(verify=False) as client:
            response = await client.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
    
    async def get_commit_diff(self, repo_url: str, commit_hash: str) -> Dict[str, Any]:
        owner, repo = self._parse_repo_url(repo_url)
        url = f"{self.base_url}/repos/{owner}/{repo}/commits/{commit_hash}"
        
        async with httpx.AsyncClient(verify=False) as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
    
    async def compare_branches(
        self, 
        repo_url: str, 
        base: str, 
        head: str
    ) -> Dict[str, Any]:
        owner, repo = self._parse_repo_url(repo_url)
        url = f"{self.base_url}/repos/{owner}/{repo}/compare/{base}...{head}"
        
        async with httpx.AsyncClient(verify=False) as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
    
    async def get_file_content(
        self, 
        repo_url: str, 
        path: str, 
        ref: str = "main"
    ) -> str:
        owner, repo = self._parse_repo_url(repo_url)
        url = f"{self.base_url}/repos/{owner}/{repo}/contents/{path}"
        params = {"ref": ref}
        
        async with httpx.AsyncClient(verify=False) as client:
            response = await client.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()
            
            import base64
            if "content" in data:
                return base64.b64decode(data["content"]).decode("utf-8")
            return ""
    
    async def list_branches(self, repo_url: str) -> List[Dict[str, Any]]:
        owner, repo = self._parse_repo_url(repo_url)
        url = f"{self.base_url}/repos/{owner}/{repo}/branches"
        
        async with httpx.AsyncClient(verify=False) as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
    
    async def create_pull_request(
        self,
        repo_url: str,
        title: str,
        body: str,
        head: str,
        base: str = "main"
    ) -> Dict[str, Any]:
        owner, repo = self._parse_repo_url(repo_url)
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls"
        
        data = {
            "title": title,
            "body": body,
            "head": head,
            "base": base
        }
        
        async with httpx.AsyncClient(verify=False) as client:
            response = await client.post(url, headers=self.headers, json=data)
            response.raise_for_status()
            return response.json()
    
    async def add_pr_comment(
        self,
        repo_url: str,
        pr_number: int,
        comment: str
    ) -> Dict[str, Any]:
        owner, repo = self._parse_repo_url(repo_url)
        url = f"{self.base_url}/repos/{owner}/{repo}/issues/{pr_number}/comments"
        
        data = {"body": comment}
        
        async with httpx.AsyncClient(verify=False) as client:
            response = await client.post(url, headers=self.headers, json=data)
            response.raise_for_status()
            return response.json()
    
    async def get_repo_info(self, repo_url: str) -> Dict[str, Any]:
        owner, repo = self._parse_repo_url(repo_url)
        url = f"{self.base_url}/repos/{owner}/{repo}"
        
        async with httpx.AsyncClient(verify=False) as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
