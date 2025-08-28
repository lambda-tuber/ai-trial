import asyncio
from agents import (
    Agent,
    Runner,
    set_default_openai_client,
    set_default_openai_api,
    ModelSettings,
    SQLiteSession,
    set_default_openai_key,
    set_tracing_disabled,
    enable_verbose_stdout_logging,
    ModelProvider,
    RunConfig,
    OpenAIChatCompletionsModel,
    AgentBase,
    RunResult,
    RunContextWrapper,
    Tool,
    function_tool,
    ItemHelpers
)
import inspect
from typing import Callable, Awaitable, Any, List
from agents.mcp import MCPServerStdio
from openai import AsyncOpenAI
import logging
import sys
import json
from agents.util._types import MaybeAwaitable
import utility


#-----------------------------------------------------------------
project_dir = "C:\\work\\lambda-tuber\\ai-trial\\mission07"
global_session_db = ":memory:"


#-----------------------------------------------------------------
async def setup_agents():
    mcp_servers = []
    tools = []

    melchior_agent, mcp_server = await utility.create_mcp_based_agent(
        project_dir=project_dir,
        agent_name="melchior",
        model="gpt-oss-20b",
        #model="phi-4-reasoning-plus",
        prompt_names=[], resources=[], sub_agents=[], sub_agent_tools=[]
    )
    mcp_servers.append(mcp_server)
    tools.append(utility.convert_agent_to_tool(
        global_run_configs, global_session, melchior_agent,
        tool_name="ask_to_melchior",
        tool_description=("MAGIシステムにおける三賢者の一人であるメルキオール (Melchior)に問い合わせるツールである。")
    ))

    balthasar_agent, mcp_server = await utility.create_mcp_based_agent(
        project_dir=project_dir,
        agent_name="balthasar",
        model="gpt-oss-20b",
        #model="gemma-3-12b",
        prompt_names=[], resources=[], sub_agents=[], sub_agent_tools=[]
    )
    mcp_servers.append(mcp_server)
    tools.append(utility.convert_agent_to_tool(
        global_run_configs, global_session, balthasar_agent,
        tool_name="ask_to_balthasar",
        tool_description=("MAGIシステムにおける三賢者の一人であるバルタザール (Balthasar)に問い合わせるツールである。")
    ))

    casper_agent, mcp_server = await utility.create_mcp_based_agent(
        project_dir=project_dir,
        agent_name="casper",
        #model="phi-4-mini-reasoning",
        model="gpt-oss-20b",
        prompt_names=[], resources=[], sub_agents=[], sub_agent_tools=[]
    )
    mcp_servers.append(mcp_server)
    tools.append(utility.convert_agent_to_tool(
        global_run_configs, global_session, casper_agent,
        tool_name="ask_to_casper",
        tool_description=("MAGIシステムにおける三賢者の一人であるカスパー (Casper)に問い合わせるツールである。")
    ))

    para_tool = utility.create_parallel_merge_tool(
        tools=tools,
        tool_name="ask_to_magi_system",
        tool_description=("MAGIシステムにおける三賢者に全員に、同時に問い合わせるツールである。")
    )

    starting_agent, mcp_server = await utility.create_mcp_based_agent(
        project_dir=project_dir,
        agent_name="misato", 
        model="gpt-oss-20b",
        prompt_names=[],
        resources=["file:///MAGI_system_definition.md"],
        sub_agents=[melchior_agent, balthasar_agent, casper_agent],
        sub_agent_tools=[para_tool]+tools
    )
    mcp_servers.append(mcp_server)

    return starting_agent, list(reversed(mcp_servers))


#-----------------------------------------------------------------
global_run_configs = {
    "misato": RunConfig(
        model_provider=utility.CustomModelProvider(AsyncOpenAI(
            # base_url="http://172.16.0.198:1234/v1",
            base_url="http://172.16.0.43:1234/v1",
            api_key="lmstudio"
        ))),
    "melchior": RunConfig(
        model_provider=utility.CustomModelProvider(AsyncOpenAI(
            base_url="http://172.16.0.43:1234/v1",
            api_key="lmstudio"
        ))),
    "balthasar": RunConfig(
        model_provider=utility.CustomModelProvider(AsyncOpenAI(
            # base_url="http://172.16.0.99:1234/v1",
            # base_url="http://172.16.0.198:1234/v1",
            base_url="http://172.16.0.43:1234/v1",
            api_key="lmstudio"
        ))),
    "casper": RunConfig(
        model_provider=utility.CustomModelProvider(AsyncOpenAI(
            # base_url="http://172.16.0.100:1234/v1",
            base_url="http://172.16.0.43:1234/v1",
            api_key="lmstudio"
        ))),
}


#-----------------------------------------------------------------
logger = logging.getLogger(__name__)
global_session = SQLiteSession(session_id="conversation_global", db_path=global_session_db)
# enable_verbose_stdout_logging()
set_default_openai_api("chat_completions")
set_tracing_disabled(True)


#-----------------------------------------------------------------
async def main():

    starting_agent, mcp_servers = await setup_agents()

    while True:
        user_input = input("You: ")

        if user_input.strip().lower() in ("exit", "q"):
            print("会話を終了します。")
            break

        # run_config = RunConfig(model_provider=provider)
        result = await Runner.run(
            starting_agent=starting_agent,
            input=user_input,
            session=global_session,
            max_turns=30,
            run_config=global_run_configs[starting_agent.name]
        )

        print("AI:", result.final_output)

        await utility.update_memory(global_session, starting_agent, global_run_configs[starting_agent.name])

    global_session.close()
    for server in mcp_servers:
        await server.cleanup()


#-----------------------------------------------------------------
asyncio.run(main())

