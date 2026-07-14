from setuptools import setup, find_packages

setup(
    name="ai-pr-agent",
    version="0.1.0",
    description="AI agent for automated PR creation with code quality analysis",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(),
    install_requires=[
        "langgraph>=0.0.20",
        "langchain>=0.1.0",
        "langchain-openai>=0.1.0",
        "click>=8.1.0",
        "rich>=13.7.0",
        "inquirer>=3.1.0",
        "sqlalchemy>=2.0.0",
        "psycopg2-binary>=2.9.9",
        "pydantic>=2.5.0",
        "pydantic-settings>=2.1.0",
        "python-dotenv>=1.0.0",
        "keyring>=24.3.0",
        "pylint>=3.0.0",
        "flake8>=6.1.0",
        "mypy>=1.7.0",
        "httpx>=0.25.0",
        "alembic>=1.13.0",
        "pygments>=2.17.0",
        "mcp>=0.9.0",
    ],
    entry_points={
        "console_scripts": [
            "ai-pr-agent=src.cli.commands:cli",
        ],
    },
    python_requires=">=3.11",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
