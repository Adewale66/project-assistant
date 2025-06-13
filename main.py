"""
This file implements the MCP Client for our Langgraph Agent.

MCP Clients are responsible for connecting and communicating with MCP servers.
"""

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_core.messages import HumanMessage, AIMessageChunk, ToolMessage
from typing import AsyncGenerator, Any
from langchain_core.runnables import RunnableConfig
from config import mcp_config
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import SystemMessage
import logging
import os


PROMPT = """
You're name is Bob, you are a project assistant. You help the user in creating, updating and managing files both locally and on Github.

<filesystem>
You have access to a set of tools that allow you to interact with the user's local filesystem. 
You are only able to access files within the working directory `{dir_name}`. 
The absolute path to this directory is: {working_dir}
If you try to access a file outside of this directory, you will receive an error.
Always use absolute paths when specifying files.
</filesystem>

<version_control>
You have access to git and Github tools.
You should use git tools to manage remote repositories.
Keep a clean, logical commit history for the repo where each commit should represent a logical, atomic change.
</version_control>

"""


async def main():
    """
    Initialize the MCP client and run the agent conversation loop.

    The MultiServerMCPClient allows connection to multiple MCP servers using a single client and config.
    """
    model = os.environ.get("LLM_MODEL")
    if os.environ.get("GOOGLE_API_KEY"):
        model = "google_genai:" + (model or "")

    llm = init_chat_model(
        model,
        temperature=0,
    )
    client = MultiServerMCPClient(mcp_config)
    tools = await client.get_tools()
    system_prompt = PROMPT.format(
        working_dir=os.environ.get("FILESYSTEM_DIR"),
        dir_name=os.environ.get("DIR_NAME"),
    )
    promt_template = ChatPromptTemplate.from_messages(
        [
            SystemMessage(content=system_prompt),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )
    agent_executor = create_react_agent(
        llm, tools, checkpointer=MemorySaver(), prompt=promt_template
    )
    stream_config: RunnableConfig = {"configurable": {"thread_id": "1"}}

    async def stream_graph_response(
        input: dict[str, HumanMessage],
    ) -> AsyncGenerator[Any, None]:
        """
        Stream the response from the agent while parsing out tool calls.

        Yields:
            A processed string from the graph's chunked response.
        """
        async for message_chunk, meta in agent_executor.astream(
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

    logging.disable(logging.WARNING)  # Issues with Gemini
    asyncio.run(main())
