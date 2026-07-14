# AI PR Agent - Automated Pull Request Creator

An intelligent AI agent built with Python, LangGraph, GitHub MCP, and Postgres MCP that analyzes code changes, performs quality checks, and creates pull requests with user approval.

## Features

- 🤖 **Interactive CLI** - User-friendly command-line interface with rich formatting
- 🔍 **Code Quality Analysis** - Automated analysis using pylint and flake8
- 🔄 **GitHub Integration** - Pull commits, diffs, and create PRs via GitHub MCP
- 💾 **State Persistence** - All operations saved to PostgreSQL for audit trail
- 📊 **Rich UI** - Beautiful tables, progress indicators, and syntax highlighting
- ✅ **Approval Workflow** - Human-in-the-loop approval before PR creation

## Architecture

```
User CLI → LangGraph Agent → GitHub MCP (fetch changes) → 
Code Analysis → Display Results → User Approval → 
Create PR (GitHub MCP) → Save State (Postgres MCP)
```

## Prerequisites

- Python 3.11+
- PostgreSQL 16+
- GitHub Personal Access Token
- Docker (optional, for local PostgreSQL)

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/ai_agent_101.git
cd ai_agent_101
```

### 2. Create virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up PostgreSQL Database

The agent will use your existing PostgreSQL container. Make sure it's running and create the database:

```bash
# Connect to your existing PostgreSQL container
docker exec -it <your_postgres_container_name> psql -U postgres

# Create the database
CREATE DATABASE ai_agent_db;
\q
```

**Optional: Start pgAdmin for database management**

```bash
docker-compose up -d  # Starts pgAdmin on port 5050
```

pgAdmin credentials: `admin@admin.com` / `admin`

### 5. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` and add your credentials:

```env
GITHUB_TOKEN=ghp_your_github_token_here
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=ai_agent_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres

# LLM Configuration (Optional - for AI-generated PR descriptions)
LLM_API_KEY=your_api_key_here
LLM_BASE_URL=https://your-llm-host.com/v1
LLM_MODEL=gpt-3.5-turbo
```

**LLM Configuration Notes:**
- Supports any OpenAI-compatible API (OpenAI, Azure OpenAI, local models, etc.)
- If not configured, agent will use basic PR descriptions
- `LLM_BASE_URL` should point to your model hosting endpoint
- `LLM_MODEL` can be any model available on your endpoint

**Getting a GitHub Token:**
1. Go to GitHub Settings → Developer settings → Personal access tokens
2. Generate new token (classic)
3. Select scopes: `repo`, `workflow`, `write:packages`

### 6. Initialize database

```bash
python -m src.cli.commands init
```

## Usage

### Check Repository for Changes

```bash
python -m src.cli.commands check-repo
```

This will:
1. Prompt you to select/enter a repository URL
2. Fetch available branches
3. Pull recent commits via GitHub MCP
4. Analyze code quality
5. Display results in a formatted table
6. Ask for approval to create PR
7. Create PR if approved
8. Save all state to PostgreSQL

### View PR History

```bash
python -m src.cli.commands list-history
```

Filter by repository:

```bash
python -m src.cli.commands list-history --repo https://github.com/user/repo
```

### View Configuration

```bash
python -m src.cli.commands config
```

## Project Structure

```
ai_agent_101/
├── src/
│   ├── agent/
│   │   ├── graph.py          # LangGraph agent definition
│   │   ├── nodes.py          # Agent nodes (fetch, analyze, approve, create_pr)
│   │   └── state.py          # Agent state schema
│   ├── mcp/
│   │   ├── github_client.py  # GitHub MCP integration
│   │   ├── postgres_client.py # Postgres MCP integration
│   │   └── database.py       # SQLAlchemy models
│   ├── analysis/
│   │   └── code_quality.py   # Code quality analysis
│   └── cli/
│       ├── main.py           # CLI entry point
│       ├── commands.py       # CLI commands
│       └── ui.py             # Rich UI components
├── config/
│   └── settings.py           # Configuration management
├── requirements.txt
├── docker-compose.yml
├── .env.example
└── README.md
```

## How It Works

### 1. GitHub MCP Integration

The agent uses GitHub's REST API to:
- List commits on a branch
- Fetch commit diffs
- Compare branches
- Get file contents
- Create pull requests
- Add PR comments

### 2. Code Analysis

For Python files, the agent runs:
- **flake8**: Style and syntax checking
- **pylint**: Code quality and error detection

Results include:
- Number of files changed
- Lines added/removed
- Errors and warnings
- Quality score (0-100)

### 3. LangGraph Workflow

```
prompt_user → fetch_changes → analyze_code → display_results → 
request_approval → create_pr → save_state
```

Each node is an async function that updates the agent state.

### 4. State Persistence

All operations are saved to PostgreSQL:
- Repository tracking
- Code changes
- Analysis results
- PR requests
- Agent state checkpoints
- User sessions

## Example Workflow

```bash
$ python -m src.cli.commands check-repo

    ╔═════════════════════════════════════════════════════╗
    ║         AI PR Agent - Code Quality Assistant          ║
    ║              Powered by LangGraph & MCP               ║
    ╚═════════════════════════════════════════════════════╝

? Select repository or enter new: https://github.com/user/ai_agent_101
✓ Connected to repository
? Select branch: main
? Check commits: Since last check

⠋ Fetching commits via GitHub MCP...
✓ Found 3 new commits

⠋ Analyzing code changes...
✓ Analysis complete

╔═══════════════════════════════════════════════════════════╗
║ Code Quality Analysis Results                              ║
╠═══════════════════════════════════════════════════════════╣
║ Files Changed: 5                                           ║
║ Lines Added: +127 | Lines Removed: -43                     ║
║ Issues Found: 2 warnings, 0 errors                         ║
║ Quality Score: 96/100                                      ║
╚═══════════════════════════════════════════════════════════╝

? Create PR with these changes? Yes

⠋ Creating pull request via GitHub MCP...
✓ PR created: https://github.com/user/repo/pull/123
✓ State saved to PostgreSQL

✓ Agent completed successfully!
```

## Database Schema

- **repositories**: Track monitored repos
- **code_changes**: Store detected changes
- **analysis_results**: Code quality analysis
- **pr_requests**: PR creation requests
- **agent_state**: LangGraph state persistence
- **user_sessions**: Track CLI sessions

## Troubleshooting

### Database Connection Error

```bash
# Check if PostgreSQL is running
docker-compose ps

# Restart PostgreSQL
docker-compose restart postgres
```

### GitHub API Rate Limit

The agent respects GitHub's rate limits. If you hit the limit:
- Wait for the limit to reset (shown in error message)
- Use a GitHub token with higher limits
- Reduce the number of commits fetched

### Import Errors

```bash
# Ensure you're in the project root
cd /path/to/ai_agent_101

# Reinstall dependencies
pip install -r requirements.txt
```

## Development

### Running Tests

```bash
pytest tests/
```

### Code Quality

```bash
# Run linting
flake8 src/
pylint src/

# Type checking
mypy src/
```

## Future Enhancements

- [ ] Support for more programming languages
- [ ] AI-powered code review comments
- [ ] Webhook support for automated triggers
- [ ] Slack/Discord notifications
- [ ] Custom analysis rules via config
- [ ] Multi-repository batch processing
- [ ] PR template customization
- [ ] Integration with CI/CD pipelines

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

For issues and questions:
- Open an issue on GitHub
- Check existing documentation
- Review the troubleshooting section
