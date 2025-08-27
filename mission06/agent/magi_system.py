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

# from foundry_local import FoundryLocalManager
from agents.util._types import MaybeAwaitable

#-----------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s [%(levelname)s] %(message)s",
    stream=sys.stderr
)
logger = logging.getLogger(__name__)

# ============================
# 
# ============================
project_dir = "C:\\work\\lambda-tuber\\ai-trial\\mission06"

# ============================
# 
# ============================
async def setup_agents():
    mcp_servers = []
    tools = []

    melchior_agent, mcp_server = await create_mcp_based_agent(
        agent_name="melchior",
        model="gpt-oss-20b",
        #model="phi-4-reasoning-plus",
        prompt_names=[], resources=[], sub_agents=[], sub_agent_tools=[]
    )
    mcp_servers.append(mcp_server)
    tools.append(convert_agent_to_tool(
        melchior_agent,
        tool_name="ask_to_melchior",
        tool_description=("MAGIシステムにおける三賢者の一人であるメルキオール (Melchior)に問い合わせるツールである。")
    ))

    balthasar_agent, mcp_server = await create_mcp_based_agent(
        agent_name="balthasar",
        model="gpt-oss-20b",
        #model="gemma-3-12b",
        prompt_names=[], resources=[], sub_agents=[], sub_agent_tools=[]
    )
    mcp_servers.append(mcp_server)
    tools.append(convert_agent_to_tool(
        balthasar_agent,
        tool_name="ask_to_balthasar",
        tool_description=("MAGIシステムにおける三賢者の一人であるバルタザール (Balthasar)に問い合わせるツールである。")
    ))

    casper_agent, mcp_server = await create_mcp_based_agent(
        agent_name="casper",
        #model="phi-4-mini-reasoning",
        model="gpt-oss-20b",
        prompt_names=[], resources=[], sub_agents=[], sub_agent_tools=[]
    )
    mcp_servers.append(mcp_server)
    tools.append(convert_agent_to_tool(
        casper_agent,
        tool_name="ask_to_casper",
        tool_description=("MAGIシステムにおける三賢者の一人であるカスパー (Casper)に問い合わせるツールである。")
    ))

    para_tool = create_parallel_merge_tool(
        tools=tools,
        tool_name="ask_to_magi_system",
        tool_description=("MAGIシステムにおける三賢者に全員に、同時に問い合わせるツールである。")
    )

    starting_agent, mcp_server = await create_mcp_based_agent(
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
class CustomModelProvider(ModelProvider):
    def __init__(self, client: AsyncOpenAI):
        self.client = client

    def get_model(self, model_name: str | None) -> OpenAIChatCompletionsModel:
        return OpenAIChatCompletionsModel(model=model_name, openai_client=self.client)

global_run_configs = {
    "misato": RunConfig(
        model_provider=CustomModelProvider(AsyncOpenAI(
            base_url="http://172.16.0.198:1234/v1",
            # base_url="http://172.16.0.43:1234/v1",
            api_key="lmstudio"
        ))),
    "melchior": RunConfig(
        model_provider=CustomModelProvider(AsyncOpenAI(
            base_url="http://172.16.0.43:1234/v1",
            api_key="lmstudio"
        ))),
    "balthasar": RunConfig(
        model_provider=CustomModelProvider(AsyncOpenAI(
            # base_url="http://172.16.0.99:1234/v1",
            base_url="http://172.16.0.198:1234/v1",
            #base_url="http://172.16.0.43:1234/v1",
            api_key="lmstudio"
        ))),
    "casper": RunConfig(
        model_provider=CustomModelProvider(AsyncOpenAI(
            base_url="http://172.16.0.100:1234/v1",
            #base_url="http://172.16.0.43:1234/v1",
            api_key="lmstudio"
        ))),
}

#-----------------------------------------------------------------
class CustomModelProvider2(ModelProvider):

    # manager = FoundryLocalManager("Phi-4-generic-gpu")

    def _create_client(self, model_name: str):
        if model_name == "melchior":
            # Melchior@n-note
            return AsyncOpenAI(
                base_url="http://172.16.0.43:1234/v1",
                api_key="lmstudio"
            )
        elif model_name == "balthasar":
            # Balthasar@t-pc
            return AsyncOpenAI(
                base_url="http://172.16.0.198:1234/v1",
                # base_url="http://172.16.0.99:1234/v1",
                api_key="lmstudio"
            )
        elif model_name == "casper":
            # Casper@o-note
            return AsyncOpenAI(
                base_url="http://172.16.0.100:1234/v1",
                api_key="lmstudio"
            )
        elif model_name == "misato":
            # misato@k-pc
            return AsyncOpenAI(
                base_url="http://172.16.0.198:1234/v1",
                api_key="lmstudio"
            )



        elif model_name.startswith("phi-4-reasoning-plus"):
            # Melchior@n-note
            return AsyncOpenAI(
                base_url="http://172.16.0.43:1234/v1",
                api_key="lmstudio"
            )
        elif model_name.startswith("gemma-3-12b"):
            # Balthasar@t-pc
            return AsyncOpenAI(
                base_url="http://172.16.0.99:1234/v1",
                api_key="lmstudio"
            )
        elif model_name.startswith("phi-4-mini-reasoning"):
            # Casper@o-note
            return AsyncOpenAI(
                base_url="http://172.16.0.100:1234/v1",
                api_key="lmstudio"
            )
        elif model_name.startswith("gpt-oss-20b"):
            # misato@k-pc
            return AsyncOpenAI(
                base_url="http://172.16.0.198:1234/v1",
                api_key="lmstudio"
            )
        else:
            return AsyncOpenAI(
                base_url="http://localhost:1234/v1",
                api_key="lmstudio"
            )

    def __init__(self):
        self.client_cache = {}

    def get_model(self, model_name: str):
        logger.info('=========================================')
        logger.info("get_model %s", model_name)
        frame = inspect.currentframe()
        caller_frame = frame.f_back
        local_vars = caller_frame.f_locals
        logger.info('sssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssss=========================================')
        logger.info(local_vars)
        if 'agent' in local_vars:
           agent_instance = local_vars['agent']
           agent_name = agent_instance.name
           logger.info('=========================================')
           logger.info("agent_name %s", agent_name)
           model_name = agent_name
        else:
           logger.info(local_vars)
           logger.info('=========================================')
           logger.info("agent_name nont")

        if model_name in self.client_cache:
            client = self.client_cache[model_name]
        else:
            client = self._create_client(model_name)
            self.client_cache[model_name] = client

        return OpenAIChatCompletionsModel(model=model_name, openai_client=client)

# ============================
# 
# ============================
global_session = SQLiteSession(session_id="conversation_global", db_path=":memory:")
global_run_config = RunConfig(model_provider=CustomModelProvider2())


# ============================
# 
# ============================
def create_parallel_merge_tool(tools: List[Tool], tool_name: str, tool_description: str) -> Tool:
    @function_tool(
        name_override=tool_name,
        description_override=tool_description,
        is_enabled=True
    )
    async def merged_tool(context: RunContextWrapper, input_text: str) -> List[dict]:
        logger.info('=========================================')
        logger.info('create_parallel_merge_tool.merged_tool %s', input_text)

        tasks = []
        for tool in tools:
            json_input = json.dumps({"input_text": input_text}, ensure_ascii=False)
            # logger.info("Creating task for tool=%s with input JSON: %s", tool.name, json_input)
            tasks.append(tool.on_invoke_tool(context, json_input))

        results = await asyncio.gather(*tasks, return_exceptions=True)
        #logger.info('create_parallel_merge_tool.merged_tool result=%s', results)

        merged = []
        for tool_obj, result in zip(tools, results):
            if isinstance(result, Exception):
                merged.append({
                    "tool": tool_obj.name,
                    "success": False,
                    "error": str(result),
                })
            else:
                merged.append({
                    "tool": tool_obj.name,
                    "success": True,
                    "output": result,
                })

        return merged

    return merged_tool

# ============================
# 
# ============================
def convert_agent_to_tool(
    agent: AgentBase,
    tool_name: str | None = None,
    tool_description: str | None = None,
    custom_output_extractor: Callable[[RunResult], Awaitable[str]] | None = None,
    is_enabled: bool
        | Callable[[RunContextWrapper[Any], AgentBase[Any]], MaybeAwaitable[bool]] = True,
) -> Tool:
    """
    Agent インスタンスを Tool に変換する関数。
    """

    @function_tool(
        name_override=tool_name or _transforms.transform_string_function_style(agent.name),
        description_override=tool_description or "",
        is_enabled=is_enabled,
    )
    async def run_agent(context: RunContextWrapper, input_text: str) -> str:
        logger.info('=========================================')
        logger.info('convert_agent_to_tool.run_agent agent=%s', agent.name)
        output = await Runner.run(
            starting_agent=agent,
            input=input_text,
            context=context.context,
            max_turns=30,
            session=global_session,
            run_config=global_run_configs[agent.name]
        )
        if custom_output_extractor:
            return await custom_output_extractor(output)

        return ItemHelpers.text_message_outputs(output.new_items)

    return run_agent

# ============================
# 
# ============================
class ExtendedMCPServerStdio(MCPServerStdio):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    async def list_resources(self):
        response = await self.session.list_resources()
        return response.resources

    async def get_resource(self, uri):
        response = await self.session.read_resource(uri)
        return response.contents

# ============================
# 
# ============================
def get_role_content(item):
    role = getattr(item, "role", None) or item.get("role", "")
    content = getattr(item, "content", None) or item.get("content", "")
    return role, content

# ============================
# 
# ============================
async def summarize_memory(session, agent, run_config, max_memory_items=10, max_summary_length=500):
    logger.info('=========================================')
    logger.info('start summarize_memory')

    history = await session.get_items()
    if len(history) <= max_memory_items - 1:
        return None

    old_history = history[: len(history) - (max_memory_items - 1)]
    old_text = "\n".join([f"{role}: {content}" for m in old_history for role, content in [get_role_content(m)]])

    summary_prompt = f"""
        以下の古い会話を短く要約してください（重要な情報だけ残す）。
        要約は **最大 {max_summary_length} 文字** に収めてください。

        {old_text}
    """

    result = await Runner.run(starting_agent=agent, input=summary_prompt, max_turns=10, run_config=run_config)
    conversation_summary = result.final_output.strip()

    while len(await session.get_items()) > max_memory_items - 1:
        await session.pop_item()

    await session.add_items([
        {"role": "system", "content": f"[要約更新]: {conversation_summary}"}
    ])

    logger.info("履歴：%s", old_text)
    logger.info("要約：%s", conversation_summary)
    logger.info('=========================================')

    return conversation_summary


# ============================
# 
# ============================
async def update_memory(session, agent, run_config):
    max_memory_items = 50
    max_summary_length = 500
    chat_size = len(await session.get_items())
    logger.info('chat size:%d', chat_size)
    if chat_size > max_memory_items:
        await summarize_memory(
            session=session,
            agent=agent,
            run_config=run_config,
            max_memory_items=max_memory_items,
            max_summary_length=max_summary_length
        )

# ============================
# 
# ============================
async def load_prompts(mcp_server, prompt_names: list[str]) -> str:
    required_prompt = "agent_core_prompt"
    if required_prompt not in prompt_names:
        prompt_names = [required_prompt] + prompt_names
        
    prompts = await asyncio.gather(
        *[mcp_server.get_prompt(name, {}) for name in prompt_names]
    )

    texts = []
    for prompt in prompts:
        for m in prompt.messages:
            if hasattr(m.content, "text"):
                texts.append(m.content.text)

    return "\n".join(texts)

# ============================
# 
# ============================
async def load_resources(mcp_server, resource_uris: list[str]) -> str:
    core_uri = "file:///agent_core_specification.md"
    if core_uri not in resource_uris:
        resource_uris = [core_uri] + resource_uris

    resources = await asyncio.gather(
        *[mcp_server.get_resource(uri) for uri in resource_uris]
    )

    texts = []
    for resource in resources:
        for item in resource:
            if hasattr(item, "text"):
                texts.append(item.text)

    return "\n".join(texts)

# ============================
# 
# ============================
async def create_mcp_based_agent(
    agent_name: str, model: str, prompt_names: list[str],
    resources: list[str],
    sub_agents: [Agent],
    sub_agent_tools: []
    ):
    
    yaml_path = f"{project_dir}\\{agent_name}-mcp-server.yaml"
    logger.info(yaml_path)
    mcp_server = ExtendedMCPServerStdio(
        params={
            "command": "C:\\tools\\cabal\\bin\\pty-mcp-server.exe",
            "args": ["-y", yaml_path],
        },
        client_session_timeout_seconds=30
    )
    await mcp_server.connect()

    core_prompt_all = await load_prompts(mcp_server, prompt_names)
    resourse_all = await load_resources(mcp_server, resources)
    context_prompt = f"""

{core_prompt_all}

{resourse_all}

    """
    logger.info('=========================================')
    logger.info('context_prompt')
    logger.info('=========================================')
    logger.info(context_prompt)

    model_settings = ModelSettings(
        tool_choice="auto",
        parallel_tool_calls=True,
        extra_body={"max_tokens": 8000, "num_ctx": 8000}
    )
    agent = Agent(
        name=agent_name,
        instructions=context_prompt,
        model=model,
        model_settings=model_settings,
        mcp_servers=[mcp_server],
        tools = sub_agent_tools,
        handoffs=sub_agents
    )

    return agent, mcp_server

#-----------------------------------------------------------------
async def main():

    # enable_verbose_stdout_logging()
    set_default_openai_api("chat_completions")
    set_tracing_disabled(True)
    starting_agent, mcp_servers = await setup_agents()
    #provider = CustomModelProvider()
    #session = SQLiteSession(session_id="conversation_123", db_path=":memory:")

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

        await update_memory(global_session, starting_agent, global_run_configs[starting_agent.name])

    global_session.close()
    for server in mcp_servers:
        await server.cleanup()
    
#-----------------------------------------------------------------
asyncio.run(main())

