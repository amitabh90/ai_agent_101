# Quick Setup Guide

## Prerequisites Checklist

- [ ] Python 3.11+ installed
- [ ] Existing PostgreSQL container running
- [ ] GitHub Personal Access Token
- [ ] Git installed

## Step-by-Step Setup

### 1. Verify PostgreSQL is Running

```bash
# Check if your PostgreSQL container is running
docker ps | grep postgres

# If not running, start it
docker start <your_postgres_container_name>
```

### 2. Create Database

```bash
# Connect to PostgreSQL
docker exec -it <your_postgres_container_name> psql -U postgres

# Create database
CREATE DATABASE ai_agent_db;

# Verify
\l

# Exit
\q
```

### 3. Clone and Setup Project

```bash
# Clone repository
cd /Users/amitabhdas/ai_agent_101

# Run quick start script
chmod +x quickstart.sh
./quickstart.sh
```

The script will:
- Create `.env` file from template
- Create Python virtual environment
- Install all dependencies
- Initialize database schema

### 4. Configure Environment

Edit `.env` file with your credentials:

```bash
nano .env  # or use your preferred editor
```

Required settings:
```env
GITHUB_TOKEN=ghp_your_token_here
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=ai_agent_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_postgres_password
```

**Get GitHub Token:**
1. Go to https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Select scopes: `repo`, `workflow`
4. Copy the token to `.env`

### 5. Test Connection

```bash
# Activate virtual environment
source venv/bin/activate

# Test database connection
python -c "from config.settings import settings; print(f'Config loaded: {settings.postgres_db}')"

# View configuration
python -m src.cli.commands config
```

### 6. Initialize Database Schema

```bash
python -m src.cli.commands init
```

You should see: `✓ Database initialized successfully!`

### 7. Run Your First Check

```bash
python -m src.cli.commands check-repo
```

Follow the interactive prompts to:
1. Enter a repository URL
2. Select a branch
3. Choose commit range
4. View analysis results
5. Approve/reject PR creation

## Troubleshooting

### Database Connection Failed

```bash
# Check PostgreSQL is running
docker ps | grep postgres

# Check connection details in .env match your PostgreSQL setup
cat .env | grep POSTGRES

# Test direct connection
docker exec -it <container_name> psql -U postgres -d ai_agent_db -c "SELECT 1;"
```

### GitHub API Authentication Failed

```bash
# Verify token is set
cat .env | grep GITHUB_TOKEN

# Test token validity
curl -H "Authorization: token YOUR_TOKEN" https://api.github.com/user
```

### Import Errors

```bash
# Ensure virtual environment is activated
which python  # Should show path to venv/bin/python

# Reinstall dependencies
pip install -r requirements.txt
```

### Module Not Found

```bash
# Make sure you're in the project root
pwd  # Should show /Users/amitabhdas/ai_agent_101

# Run commands with -m flag
python -m src.cli.commands check-repo
```

## Next Steps

1. **Test with a sample repository**
   ```bash
   python -m src.cli.commands check-repo
   ```

2. **View PR history**
   ```bash
   python -m src.cli.commands list-history
   ```

3. **Run tests**
   ```bash
   pytest tests/ -v
   ```

4. **Optional: Start pgAdmin**
   ```bash
   docker-compose up -d
   # Access at http://localhost:5050
   ```

## Common Commands

```bash
# Check repository
python -m src.cli.commands check-repo

# View history
python -m src.cli.commands list-history

# View configuration
python -m src.cli.commands config

# Initialize/reset database
python -m src.cli.commands init

# Run tests
pytest tests/

# Deactivate virtual environment
deactivate
```

## Project Structure

```
ai_agent_101/
├── src/
│   ├── agent/          # LangGraph agent
│   ├── mcp/            # GitHub & Postgres MCP clients
│   ├── analysis/       # Code quality analysis
│   └── cli/            # Interactive CLI
├── config/             # Settings
├── tests/              # Unit tests
├── .env                # Your credentials (not in git)
└── README.md           # Full documentation
```

## Support

If you encounter issues:
1. Check this guide's troubleshooting section
2. Review the main README.md
3. Check that all prerequisites are met
4. Verify .env configuration is correct
