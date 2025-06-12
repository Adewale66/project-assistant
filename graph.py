from typing_extensions import TypedDict, List, Annotated
from langchain.tools import BaseTool
from langgraph.graph import StateGraph, START, END, add_messages
from langchain_core.messages import SystemMessage, HumanMessage, BaseMessage
from langchain.chat_models import init_chat_model
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver
from dotenv import load_dotenv
import os

load_dotenv()

model = os.environ.get("LLM_MODEL")

llm = init_chat_model(
    model,
    temperature=0,
)

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
You should use git tools to manage the version history of the project and Github tools to manage the project's remote repository.
Keep a clean, logical commit history for the repo where each commit should represent a logical, atomic change.
</version_control>

"""


class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]


def build_agent(tools: List[BaseTool] = []):

    llm_with_tools = llm.bind_tools(tools)
    system_prompt = PROMPT.format(
        working_dir=os.environ.get("FILESYSTEM_DIR"),
        dir_name=os.environ.get("DIR_NAME"),
    )

    def agent(state: AgentState):
        full_prompt = [SystemMessage(content=system_prompt)] + state["messages"]
        return {"messages": [llm_with_tools.invoke(full_prompt)]}

    builder = StateGraph(AgentState)
    builder.add_node("agent", agent)
    builder.add_node("tools", ToolNode(tools))
    builder.add_edge("tools", "agent")
    builder.add_conditional_edges("agent", tools_condition)
    builder.set_entry_point("agent")
    return builder.compile(checkpointer=MemorySaver())


if __name__ == "__main__":
    from IPython.display import display, Image

    graph = build_agent()
    display(Image(graph.get_graph().draw_mermaid_png()))
