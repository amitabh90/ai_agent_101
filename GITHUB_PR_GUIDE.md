# GitHub PR Creation Guide

## Why PR Creation Failed (422 Error)

The error `422 Unprocessable Entity` occurs when trying to create a pull request because:

**You cannot create a PR from a branch to itself (e.g., main → main)**

## How to Use the Agent Correctly

### Option 1: Create a Feature Branch First

```bash
# 1. Create and switch to a new branch
git checkout -b feature/my-changes

# 2. Make your changes
# ... edit files ...

# 3. Commit changes
git add .
git commit -m "Add new feature"

# 4. Push to GitHub
git push origin feature/my-changes

# 5. NOW run the agent
python -m src.cli.commands check-repo
# Select: feature/my-changes branch
# This will create PR: feature/my-changes → main
```

### Option 2: Check Existing Feature Branches

```bash
# List all branches
git branch -a

# If you have a feature branch, switch to it
git checkout feature-branch-name

# Run the agent
python -m src.cli.commands check-repo
```

## Typical Workflow

```
main branch (protected)
    ↓
feature/new-feature (your work)
    ↓
Make changes & commit
    ↓
Run AI PR Agent
    ↓
Agent creates PR: feature/new-feature → main
    ↓
Review & merge on GitHub
```

## Current Limitation

The agent currently creates PRs with:
- **Head**: The branch you select (e.g., `feature/my-changes`)
- **Base**: `main` (hardcoded)

This means:
- ✅ Works: `feature-branch` → `main`
- ❌ Fails: `main` → `main`
- ❌ Fails: `main` → `develop`

## Example: Testing the Agent

```bash
# 1. Create a test branch
git checkout -b test/agent-demo

# 2. Make a small change
echo "# Test" >> test.md
git add test.md
git commit -m "Test commit for PR agent"

# 3. Push to GitHub
git push origin test/agent-demo

# 4. Run the agent
python -m src.cli.commands check-repo

# When prompted:
# - Repository: https://github.com/amitabh90/ai_agent_101
# - Branch: test/agent-demo  ← Important!
# - Commits: Since last check

# 5. Agent will create PR: test/agent-demo → main
```

## Future Enhancement

To make the agent work with `main` branch commits, you would need to:

1. **Auto-create a feature branch** from the commits
2. **Push the branch** to GitHub
3. **Then create the PR** from that branch

This requires additional logic in the agent to:
- Detect if on main branch
- Create a new branch name
- Push commits to new branch
- Create PR from new branch

## Workaround for Now

If you want to create PRs for changes on `main`:

```bash
# 1. Create a branch from current main
git checkout -b feature/from-main

# 2. Push it
git push origin feature/from-main

# 3. Run agent and select this branch
python -m src.cli.commands check-repo
```

## Summary

✅ **Do**: Work on feature branches, run agent on those branches
❌ **Don't**: Try to create PRs from main to main

The agent is designed for the standard Git workflow where:
- Development happens on feature branches
- PRs merge feature branches into main
- Main branch is protected
