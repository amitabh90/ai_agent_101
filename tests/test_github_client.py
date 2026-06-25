import pytest
from unittest.mock import Mock, patch
from src.mcp.github_client import GitHubMCPClient


def test_parse_repo_url():
    client = GitHubMCPClient(token="test_token")
    
    owner, repo = client._parse_repo_url("https://github.com/user/repo")
    assert owner == "user"
    assert repo == "repo"
    
    owner, repo = client._parse_repo_url("https://github.com/user/repo.git")
    assert owner == "user"
    assert repo == "repo"
    
    owner, repo = client._parse_repo_url("user/repo")
    assert owner == "user"
    assert repo == "repo"


def test_parse_repo_url_invalid():
    client = GitHubMCPClient(token="test_token")
    
    with pytest.raises(ValueError):
        client._parse_repo_url("invalid")


@pytest.mark.asyncio
async def test_list_commits():
    client = GitHubMCPClient(token="test_token")
    
    with patch('httpx.AsyncClient') as mock_client:
        mock_response = Mock()
        mock_response.json.return_value = [
            {"sha": "abc123", "commit": {"message": "Test commit"}}
        ]
        mock_response.raise_for_status = Mock()
        
        mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
        
        commits = await client.list_commits("user/repo", "main")
        
        assert len(commits) == 1
        assert commits[0]["sha"] == "abc123"
