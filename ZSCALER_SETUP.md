# Zscaler LLM Proxy Setup Guide

This guide shows how to configure the AI PR Agent to work with Zscaler's LLM proxy.

## Configuration

Edit your `.env` file:

```env
# GitHub Configuration
GITHUB_TOKEN=your_github_token_here

# PostgreSQL Configuration
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=ai_agent_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_postgres_password

# Zscaler LLM Proxy Configuration
LLM_API_KEY=your_zscaler_api_key
LLM_BASE_URL=https://zllama.corp.zscaler.com
LLM_MODEL=claude-4-sonnet
```

## Available Models

Check with your Zscaler admin for available models. Common options:

- `claude-4-sonnet` - Anthropic Claude 4 Sonnet
- `claude-sonnet-4-6` - Anthropic Claude Sonnet 4.6
- `gpt-4` - OpenAI GPT-4
- `gpt-3.5-turbo` - OpenAI GPT-3.5 Turbo

## How It Works

The agent uses the OpenAI Python library with custom base URL:

```python
import openai

client = openai.OpenAI(
    api_key="your_api_key",
    base_url="https://zllama.corp.zscaler.com"
)

response = client.chat.completions.create(
    model="claude-4-sonnet",
    messages=[
        {
            "role": "user",
            "content": "Your prompt here"
        }
    ]
)
```

This is exactly what the agent does internally when generating PR descriptions.

## Testing Your Setup

### 1. Check Configuration

```bash
python -m src.cli.commands config
```

You should see:

```
LLM Settings:
  API Key: ********************
  Base URL: https://zllama.corp.zscaler.com
  Model: claude-4-sonnet
```

### 2. Test with a Repository

```bash
python -m src.cli.commands check-repo
```

When creating a PR, you'll see:

```
ℹ Generating PR description with AI...
```

If successful, the PR will have an AI-generated description from Claude.

## Troubleshooting

### Connection Issues

**Error:** `Connection refused` or `Timeout`

**Solutions:**
1. Verify you're on the corporate network/VPN
2. Check the base URL is correct
3. Test connectivity: `curl https://zllama.corp.zscaler.com`

### Authentication Issues

**Error:** `Invalid API key` or `401 Unauthorized`

**Solutions:**
1. Verify your API key is correct
2. Check if your key has expired
3. Contact your Zscaler admin for a new key

### Model Not Available

**Error:** `Model not found` or `Invalid model`

**Solutions:**
1. Check available models with your admin
2. Try a different model name
3. Update `LLM_MODEL` in `.env`

## Example PR Description

**Without LLM:**
```markdown
## Changes

### Commits
- Fix authentication bug
- Update dependencies

### Code Quality
- Files changed: 3
- Lines: +45 / -12
- Quality score: 92/100
```

**With Zscaler LLM (Claude):**
```markdown
## Summary

This PR addresses a critical authentication bug that was preventing users from 
logging in with SSO credentials. The fix implements proper token validation and 
adds comprehensive error handling.

## Key Changes

- Fixed SSO authentication flow by correcting token validation logic
- Updated authentication dependencies to latest secure versions
- Added error handling for edge cases in login process

## Code Quality

All changes maintain high code quality standards with a score of 92/100. 
Minor linting warnings have been addressed, and the code follows established 
patterns in the codebase.
```

## Network Configuration

If you're behind a corporate proxy, you may need to configure:

```bash
# Set proxy environment variables
export HTTP_PROXY=http://proxy.corp.zscaler.com:8080
export HTTPS_PROXY=http://proxy.corp.zscaler.com:8080
export NO_PROXY=localhost,127.0.0.1
```

## Security Notes

1. **Never commit `.env` file** - It contains your API key
2. **Rotate keys regularly** - Request new keys from your admin
3. **Use VPN** - Ensure you're on corporate network
4. **Check logs** - Review logs for any security issues

## Support

For Zscaler LLM proxy issues:
- Contact your Zscaler administrator
- Check internal documentation
- Verify network connectivity

For AI PR Agent issues:
- Check `README.md`
- Review `LLM_CONFIGURATION.md`
- Check application logs
