"""
This file implements the MCP Client for our Langgraph Agent.

MCP Clients are responsible for connecting and communicating with MCP servers.
"""

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_core.messages import HumanMessage, AIMessageChunk, ToolMessage
from typing import AsyncGenerator, Any
from graph import build_agent
from langchain_core.runnables import RunnableConfig
from config import mcp_config
import logging

logging.disable(logging.WARNING)  # Issues with Gemini


async def main():
    """
    Initialize the MCP client and run the agent conversation loop.

    The MultiServerMCPClient allows connection to multiple MCP servers using a single client and config.
    """
    client = MultiServerMCPClient(mcp_config)
    tools = await client.get_tools()
    graph = build_agent(tools=tools)
    stream_config: RunnableConfig = {"configurable": {"thread_id": "1"}}

    async def stream_graph_response(
        input: dict[str, HumanMessage],
    ) -> AsyncGenerator[Any, None]:
        """
        Stream the response from the graph while parsing out tool calls.

        Yields:
            A processed string from the graph's chunked response.
        """
        async for message_chunk, metadata in graph.astream(
            input=input, stream_mode="messages", config=stream_config
        ):
            if isinstance(message_chunk, AIMessageChunk):
                yield message_chunk.content
            elif isinstance(message_chunk, ToolMessage):
                yield message_chunk.pretty_print()
            continue

    while True:
        user_input = input("\nUSER: ")
        if user_input in ["quit", "exit"]:
            break
        messages = {"messages": HumanMessage(content=user_input)}

        print(
            "\n\n=================================== Assistant ==================================="
        )
        async for response in stream_graph_response(messages):
            print(response, end="", flush=True)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
