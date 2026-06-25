# LLM Configuration Guide

The AI PR Agent supports custom LLM endpoints for generating AI-powered PR descriptions and code review comments.

## Configuration

Add these variables to your `.env` file:

```env
LLM_API_KEY=your_api_key_here
LLM_BASE_URL=https://your-llm-host.com/v1
LLM_MODEL=gpt-3.5-turbo
```

## Supported Providers

### 1. OpenAI

```env
LLM_API_KEY=sk-...
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-3.5-turbo
```

### 2. Azure OpenAI

```env
LLM_API_KEY=your_azure_key
LLM_BASE_URL=https://your-resource.openai.azure.com/openai/deployments/your-deployment
LLM_MODEL=gpt-35-turbo
```

### 3. Local Models (Ollama, LM Studio, etc.)

```env
LLM_API_KEY=not-needed
LLM_BASE_URL=http://localhost:11434/v1
LLM_MODEL=llama2
```

### 4. Custom Hosted Models

```env
LLM_API_KEY=your_custom_key
LLM_BASE_URL=https://your-custom-host.com/v1
LLM_MODEL=your-model-name
```

## Features Using LLM

### 1. AI-Generated PR Descriptions

When creating a PR, the agent uses the LLM to generate:
- Summary of changes based on commit messages
- Key improvements and highlights
- Code quality concerns
- Professional, concise descriptions

**Without LLM:** Basic template with commit list and statistics
**With LLM:** Intelligent, context-aware descriptions

### 2. Code Review Comments (Future)

The `llm_client.py` module includes a `generate_code_review_comment()` function for future enhancements.

## Testing Your Configuration

```bash
# View current configuration
python -m src.cli.commands config

# Test with a repository
python -m src.cli.commands check-repo
```

If LLM is configured correctly, you'll see:
```
ℹ Generating PR description with AI...
```

If not configured:
```
Note: LLM features disabled. PR descriptions will be basic.
```

## Model Selection

Choose models based on your needs:

| Use Case | Recommended Model | Notes |
|----------|------------------|-------|
| Fast, cheap | gpt-3.5-turbo | Good for basic descriptions |
| High quality | gpt-4 | Better analysis and writing |
| Local/Private | llama2, mistral | No external API calls |
| Code-specific | codellama | Optimized for code |

## API Key Security

**Best Practices:**
1. Never commit `.env` to git (already in `.gitignore`)
2. Use environment-specific keys
3. Rotate keys regularly
4. Use read-only keys when possible

## Troubleshooting

### LLM Not Working

```bash
# Check configuration
python -m src.cli.commands config

# Verify .env file exists
ls -la .env

# Test API connection
curl -H "Authorization: Bearer YOUR_KEY" YOUR_BASE_URL/models
```

### Common Issues

**Issue:** "LLM features disabled"
**Solution:** Set `LLM_API_KEY` and `LLM_BASE_URL` in `.env`

**Issue:** "Connection refused"
**Solution:** Check `LLM_BASE_URL` is correct and accessible

**Issue:** "Invalid API key"
**Solution:** Verify `LLM_API_KEY` is correct

**Issue:** "Model not found"
**Solution:** Check `LLM_MODEL` is available on your endpoint

## Fallback Behavior

If LLM fails or is not configured:
- Agent continues to work normally
- Uses simple template-based PR descriptions
- No errors or crashes
- Warning message displayed

## Cost Considerations

**OpenAI Pricing (approximate):**
- gpt-3.5-turbo: ~$0.002 per PR description
- gpt-4: ~$0.03 per PR description

**Local Models:**
- Free (requires local compute)
- No API rate limits
- Complete privacy

## Advanced Configuration

### Custom Temperature

Edit `src/agent/llm_client.py`:

```python
llm = get_llm_client(temperature=0.5)  # 0.0 = deterministic, 1.0 = creative
```

### Custom Max Tokens

```python
llm = get_llm_client(max_tokens=500)  # Limit response length
```

### Multiple Models

You can use different models for different tasks by modifying the `get_llm_client()` calls in the code.

## Example Configurations

### Development (Local)

```env
LLM_API_KEY=not-needed
LLM_BASE_URL=http://localhost:11434/v1
LLM_MODEL=llama2
```

### Production (OpenAI)

```env
LLM_API_KEY=sk-proj-...
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-3.5-turbo
```

### Enterprise (Azure)

```env
LLM_API_KEY=abc123...
LLM_BASE_URL=https://company.openai.azure.com/openai/deployments/gpt-35-turbo
LLM_MODEL=gpt-35-turbo
```

## Disabling LLM

To disable LLM features:
1. Remove or comment out LLM variables in `.env`
2. Or set `LLM_API_KEY=` (empty)

The agent will work normally with basic PR descriptions.
