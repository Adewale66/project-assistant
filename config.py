"""
Contains config for MCP servers
"""

from dotenv import load_dotenv
from langchain_mcp_adapters.sessions import Connection
import os


load_dotenv()

mcp_config: dict[str, Connection] = {
    "filesystem": {
        "command": "npx",
        "args": [
            "-y",
            "@modelcontextprotocol/server-filesystem",
            f"{os.environ.get('FILESYSTEM_DIR')}",
        ],
        "transport": "stdio",
    },
    "git": {"command": "uvx", "args": ["mcp-server-git"], "transport": "stdio"},
    "github": {
        "command": "./github-mcp-server",
        "args": ["stdio"],
        "env": {"GITHUB_PERSONAL_ACCESS_TOKEN": f"{os.environ.get('GITHUB_PAT')}"},
        "transport": "stdio",
    },
}  # type: ignore
