
import asyncio
import agents
import logging
import sys
from typing import Callable, Awaitable, Any, List
import json

#-----------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
    stream=sys.stderr
)
logger = logging.getLogger(__name__)

#-----------------------------------------------------------------
class CustomModelProvider(agents.ModelProvider):
    def __init__(self, client: agents.AsyncOpenAI):
        self.client = client

    def get_model(self, model_name: str | None) -> agents.OpenAIChatCompletionsModel:
        return agents.OpenAIChatCompletionsModel(model=model_name, openai_client=self.client)

# ============================
# 
# ============================
def create_parallel_merge_tool(tools: List[agents.Tool], tool_name: str, tool_description: str) -> agents.Tool:
    @agents.function_tool(
        name_override=tool_name,
        description_override=tool_description,
        is_enabled=True
    )
    async def merged_tool(context: agents.RunContextWrapper, input_text: str) -> List[dict]:
        logger.info('=========================================')
        logger.info('create_parallel_merge_tool.merged_tool %s', input_text)

        tasks = []
        for tool in tools:
            json_input = json.dumps({"input_text": input_text}, ensure_ascii=False)
            # logger.info("Creating task for tool=%s with input JSON: %s", tool.name, json_input)
            tasks.append(tool.on_invoke_tool(context, json_input))

        results = await asyncio.gather(*tasks, return_exceptions=True)

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
class ExtendedMCPServerStdio(agents.mcp.MCPServerStdio):
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

    result = await agents.Runner.run(starting_agent=agent, input=summary_prompt, max_turns=10, run_config=run_config)
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
async def create_mcp_based_agent(
    project_dir,
    agent_name: str, model: str, prompt_names: list[str],
    resources: list[str],
    handoffs: [agents.Agent],
    tools: [],
    mcp_servers=[]
    ):
    
    mcp_exec = "C:\\tools\\cabal\\bin\\pty-mcp-server.exe"
    yaml_path = f"{project_dir}\\{agent_name}-mcp-server.yaml"
    logger.info(yaml_path)
    mcp_server = ExtendedMCPServerStdio(
        params={
            "command": mcp_exec,
            "args": ["-y", yaml_path],
        },
        client_session_timeout_seconds=30
    )
    merged_mcp_servers = [mcp_server]+mcp_servers
    for server in merged_mcp_servers:
        await server.connect()

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

    model_settings = agents.ModelSettings(
        tool_choice="auto",
        parallel_tool_calls=True,
        extra_body={"max_tokens": 8000, "num_ctx": 8000}
    )
    agent = agents.Agent(
        name=agent_name,
        instructions=context_prompt,
        model=model,
        model_settings=model_settings,
        mcp_servers=merged_mcp_servers,
        tools = tools,
        handoffs =handoffs
    )

    return agent, mcp_server


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
def convert_agent_to_tool(
    run_configs,
    session,
    agent: agents.AgentBase,
    tool_name: str | None = None,
    tool_description: str | None = None,
    custom_output_extractor: Callable[[agents.RunResult], Awaitable[str]] | None = None,
    is_enabled: bool
        | Callable[[agents.RunContextWrapper[Any], agents.AgentBase[Any]], agents.util._types.MaybeAwaitable[bool]] = True,
) -> agents.Tool:
    """
    Agent インスタンスを Tool に変換する関数。
    """

    @agents.function_tool(
        name_override=tool_name or _transforms.transform_string_function_style(agent.name),
        description_override=tool_description or "",
        is_enabled=is_enabled,
    )
    async def run_agent(context: agents.RunContextWrapper, input_text: str) -> str:
        logger.info('=========================================')
        logger.info('convert_agent_to_tool.run_agent agent=%s', agent.name)
        output = await agents.Runner.run(
            starting_agent=agent,
            input=input_text,
            context=context.context,
            max_turns=30,
            session=session,
            run_config=run_configs[agent.name]
        )
        if custom_output_extractor:
            return await custom_output_extractor(output)

        result = agents.ItemHelpers.text_message_outputs(output.new_items)
        logger.info('=========================================')
        logger.info('convert_agent_to_tool.run_agent agent=%s, result=%s', agent.name, result)
 
        return result

    return run_agent


# ============================
# 
# ============================
def create_run_configs(tachikoma_list):
    run_configs = {}
    for agent_def in tachikoma_list:
        name = agent_def["name"]
        llm_info = agent_def["llm"]

        run_configs[name] = agents.RunConfig(
            model_provider=CustomModelProvider(
                agents.AsyncOpenAI(
                    base_url=llm_info["base_url"],
                    api_key=llm_info["api_key"]
                )
            )
        )
    return run_configs


# ============================
# 
# ============================
async def generate_mcp_based_agents(project_dir, tachikoma_list):
    mcp_servers = []
    agent_list = []

    for agent_def in tachikoma_list:
        agent, mcp_server = await create_mcp_based_agent(
            project_dir=project_dir,
            agent_name=agent_def["name"],
            model=agent_def["llm"]["model"],
            prompt_names=agent_def.get("prompts", []),
            resources=agent_def.get("resources", []),
            handoffs=[],
            tools=[],
            mcp_servers=agent_def["mcp_servers"]
        )

        agent_list.append(agent)
        mcp_servers.append(mcp_server)

    return agent_list, mcp_servers


# ============================
# 
# ============================
def wiring_agent_tools(agent_list, run_configs, session):
    agent_tools_map = {}
    para_tools = []
    for agent in agent_list:
        # tool_name = f"message_to_{agent.name}"
        tool_name = f"message_to_{agent.name}"
        tool_description = f"「{agent.name}」に問い合わせるツールである。"
        as_tool = convert_agent_to_tool(
            run_configs,
            session,
            agent,
            tool_name=tool_name,
            tool_description=tool_description
        )
        agent_tools_map[agent.name] = as_tool
        para_tools.append(as_tool) 

    for agent in agent_list:
        tools = []
        for other_name, other_tool in agent_tools_map.items():
            if other_name == agent.name:
                continue  # 自分自身は除外
            tools.append(other_tool)

        agent.tools.extend(tools)


    para_tool = create_parallel_merge_tool(
        tools=para_tools[1:],  # エントリープラグ(starting_agent)を除く
        tool_name="message_to_all_agent",
        tool_description=("すべてのエージェントに、同時に問い合わせるツールである。")
    )
    agent_list[0].tools.append(para_tool)

    return None


# ============================
# 
# ============================
def wiring_handoffs_agent(agent_list):
    entry_plag = agent_list[0]
    other_agents = agent_list[1:]
    entry_plag.handoffs = other_agents

    return None

