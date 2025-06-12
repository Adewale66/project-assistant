# Project Assistant

## Overview

This is a project to assist users in managing their projects, both locally and on GitHub. It provides tools for file management, version control, and collaboration.

## MCP servers

- [Filesystem](https://github.com/modelcontextprotocol/servers/tree/main/src/filesystem)
- [Git](https://github.com/modelcontextprotocol/servers/tree/main/src/git)
- [Github](https://github.com/github/github-mcp-server)

## Supported LLMs

- OpenAI
- Gemini
- Anthropic
- Groq
- Ollama
- Deepseek

## Required tools:

- Python >=3.11
- [uv](https://docs.astral.sh/uv/)

## Installatiion

```bash
uv sync
```

## Usage

### Copy and add env variables

```bash
cp .env.example .env
```

### Run application

```bash
uv run python main.py
```
