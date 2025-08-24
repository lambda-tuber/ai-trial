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
    OpenAIChatCompletionsModel
)
from agents.mcp import MCPServerStdio
from openai import AsyncOpenAI
import logging
import sys

#-----------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s [%(levelname)s] %(message)s",
    stream=sys.stderr
)
logger = logging.getLogger(__name__)


#-----------------------------------------------------------------
class CustomModelProvider(ModelProvider):
    def __init__(self, client: AsyncOpenAI):
        self.client = client

    def get_model(self, model_name: str | None) -> OpenAIChatCompletionsModel:
        return OpenAIChatCompletionsModel(model=model_name, openai_client=self.client)


class ExtendedMCPServerStdio(MCPServerStdio):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    async def list_resources(self):
        response = await self.session.list_resources()
        return response.resources

    async def get_resource(self, uri):
        response = await self.session.read_resource(uri)
        return response.contents


def get_role_content(item):
    # 属性アクセスがあれば属性、なければ辞書キー
    role = getattr(item, "role", None) or item.get("role", "")
    content = getattr(item, "content", None) or item.get("content", "")
    return role, content


async def summarize_memory(session, agent, run_config, max_memory_items=10, max_summary_length=500):
    """
    SQLiteSession 内の古い履歴をまとめて要約する。

    Args:
        runner: Runner インスタンス
        session: SQLiteSession
        agent: Assistant または Agent
        run_config: RunConfig
        max_memory_items: メモリに保持する最大件数
        max_summary_length: 要約の最大文字数
    Returns:
        conversation_summary: 生成された要約（str）または None
    """
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


async def create_mcp_based_agent(agent_name: str, sub_agent_list: [Agent]):
    """
    MCPサーバを起動して、プロンプト・リソースを取得し、Agentを生成する。
    引数は yaml_path のみで、他の設定は固定。
    """
    
    yaml_path = f"C:\\work\\lambda-tuber\\ai-trial\\mission05\\{agent_name}-mcp-server.yaml"
    logger.info(yaml_path)
    # MCPサーバの初期化
    mcp_server = ExtendedMCPServerStdio(
        params={
            "command": "C:\\tools\\cabal\\bin\\pty-mcp-server.exe",
            "args": ["-y", yaml_path],
        },
        client_session_timeout_seconds=30
    )
    await mcp_server.connect()

    # プロンプト取得
    core_prompt = await mcp_server.get_prompt("agent_core_prompt", {})
    core_prompt_text = "\n".join(
        m.content.text for m in core_prompt.messages if hasattr(m.content, "text")
    )

    # リソース取得
    core_spec = await mcp_server.get_resource("file:///agent_core_specification.md")
    core_spec_text = "\n".join(item.text for item in core_spec)
    logger.info('=========================================')
    logger.info(core_spec)

    # コンテキスト作成
    context_prompt = f"""
{core_prompt_text}
{core_spec_text}
"""

    # モデル設定（固定）
    model_settings = ModelSettings(
        tool_choice="auto",
        extra_body={"max_tokens": 8000, "num_ctx": 8000}
    )
    
    logger.info('=========================================')
    logger.info('context_prompt')
    logger.info('=========================================')
    logger.info(context_prompt)

    # Agent作成
    agent = Agent(
        name=agent_name,
        instructions=context_prompt,
        model="gpt-oss-20b",
        model_settings=model_settings,
        mcp_servers=[mcp_server],
        handoffs=sub_agent_list
    )

    return agent, mcp_server

#-----------------------------------------------------------------
async def main():
    lm_studio_provider = CustomModelProvider(client = AsyncOpenAI(
        base_url="http://localhost:1234/v1",
        api_key="dummy"
    ))

    ollama_provider = CustomModelProvider(client = AsyncOpenAI(
        base_url="http://localhost:11434/v1",
        api_key="dummy"
    ))
    provider = lm_studio_provider

    set_default_openai_api("chat_completions")
    set_tracing_disabled(True)
    # enable_verbose_stdout_logging()

    #------------------------------------------------------------
    # Aagent
    #------------------------------------------------------------
    www_agent, www_agent_mcp_server = await create_mcp_based_agent("www-admin-agent", [])
    system_admin_agent, system_admin_agent_mcp_server = await create_mcp_based_agent("system-admin-agent", [www_agent])

    #------------------------------------------------------------
    session = SQLiteSession(session_id="conversation_123", db_path=":memory:")

    while True:
        user_input = input("You: ")

        if user_input.strip().lower() in ("exit", "q"):
            print("会話を終了します。")
            break

        run_config = RunConfig(model_provider=provider)
        result = await Runner.run(starting_agent=system_admin_agent, input=user_input, session=session, max_turns=30, run_config=run_config)

        print("AI:", result.final_output)

        max_memory_items = 50
        max_summary_length = 500
        chat_size = len(await session.get_items())
        logger.info('chat size:%d', chat_size)
        if chat_size > max_memory_items:
            await summarize_memory(
                session=session,
                agent=system_admin_agent,
                run_config=run_config,
                max_memory_items=max_memory_items,
                max_summary_length=max_summary_length
            )

    session.close()
    await system_admin_agent_mcp_server.cleanup()
    await www_agent_mcp_server.cleanup()

#-----------------------------------------------------------------
asyncio.run(main())

