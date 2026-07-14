from typing import Optional
import openai
from openai import OpenAI
from config.settings import settings


def get_llm_client(
    model: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: Optional[int] = None
) -> OpenAI:
    """
    Get LLM client configured with custom base URL and API key.
    
    Supports any OpenAI-compatible API endpoint (OpenAI, Azure, llm proxy, local models, etc.)
    
    Args:
        model: Model name to use (defaults to settings.llm_model)
        temperature: Sampling temperature (0-1)
        max_tokens: Maximum tokens in response
    
    Returns:
        Configured OpenAI client
    """
    client = openai.OpenAI(
        api_key=settings.llm_api_key or "dummy-key",
        base_url=settings.llm_base_url
    )
    
    return client


def generate_pr_description(
    commit_messages: list[str],
    analysis_results: dict,
    max_length: int = 500
) -> str:
    """
    Generate AI-powered PR description based on commits and analysis.
    
    Args:
        commit_messages: List of commit messages
        analysis_results: Code quality analysis results
        max_length: Maximum description length
    
    Returns:
        Generated PR description
    """
    if not settings.llm_api_key or not settings.llm_base_url:
        return _generate_simple_description(commit_messages, analysis_results)
    
    try:
        client = get_llm_client()
        model = settings.llm_model
        
        prompt = f"""Generate a concise pull request description based on:

Commits:
{chr(10).join(f"- {msg}" for msg in commit_messages[:5])}

Code Quality Analysis:
- Files changed: {analysis_results.get('files_changed', 0)}
- Lines added: {analysis_results.get('lines_added', 0)}
- Lines removed: {analysis_results.get('lines_removed', 0)}
- Quality score: {analysis_results.get('score', 0)}/100
- Issues: {analysis_results.get('errors', 0)} errors, {analysis_results.get('warnings', 0)} warnings

Write a professional PR description that:
1. Summarizes the changes
2. Highlights key improvements
3. Mentions any code quality concerns
4. Is concise (max 3-4 paragraphs)

PR Description:"""
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.5,
            max_tokens=max_length
        )
        
        return response.choices[0].message.content.strip()
    
    except Exception as e:
        print(f"Warning: LLM generation failed ({str(e)}), using simple description")
        return _generate_simple_description(commit_messages, analysis_results)


def _generate_simple_description(commit_messages: list[str], analysis_results: dict) -> str:
    """Fallback: Generate simple description without LLM."""
    description = "## Changes\n\n"
    
    if commit_messages:
        description += "### Commits\n"
        for msg in commit_messages[:5]:
            description += f"- {msg}\n"
        description += "\n"
    
    description += "### Code Quality\n"
    description += f"- Files changed: {analysis_results.get('files_changed', 0)}\n"
    description += f"- Lines: +{analysis_results.get('lines_added', 0)} / -{analysis_results.get('lines_removed', 0)}\n"
    description += f"- Quality score: {analysis_results.get('score', 0)}/100\n"
    description += f"- Issues: {analysis_results.get('errors', 0)} errors, {analysis_results.get('warnings', 0)} warnings\n"
    
    return description


def generate_code_review_comment(
    file_path: str,
    issue: dict,
    context: str
) -> Optional[str]:
    """
    Generate AI-powered code review comment for a specific issue.
    
    Args:
        file_path: Path to the file
        issue: Issue details (line, message, severity)
        context: Code context around the issue
    
    Returns:
        Generated review comment or None if LLM not available
    """
    if not settings.llm_api_key or not settings.llm_base_url:
        return None
    
    try:
        client = get_llm_client()
        model = settings.llm_model
        
        prompt = f"""Review this code issue and provide a helpful comment:

File: {file_path}
Line: {issue.get('line', 0)}
Issue: {issue.get('message', '')}
Severity: {issue.get('severity', 'warning')}

Code context:
```
{context}
```

Provide a brief, actionable code review comment (1-2 sentences) that:
1. Explains why this is an issue
2. Suggests how to fix it

Comment:"""
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,
            max_tokens=200
        )
        
        return response.choices[0].message.content.strip()
    
    except Exception:
        return None
