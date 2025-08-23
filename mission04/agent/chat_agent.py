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
    provider = ollama_provider

    set_default_openai_api("chat_completions")
    set_tracing_disabled(True)
    # enable_verbose_stdout_logging()

    mcp_server = ExtendedMCPServerStdio(
        params={
            "command": "C:\\tools\\cabal\\bin\\pty-mcp-server.exe",
            "args": ["-y", "C:\\work\\lambda-tuber\\ai-trial\\mission04\\pty-mcp-server.yaml"],
        },
        client_session_timeout_seconds=30
    )

    await mcp_server.connect()

    linux_admin_prompt = await mcp_server.get_prompt("linux_admin_prompt", {})
    linux_prompt_text = "\n".join(m.content.text for m in linux_admin_prompt.messages if hasattr(m.content, "text"))
    spec_system = await mcp_server.get_resource("file:///spec_system.md")
    spec_text = "\n".join(item.text for item in spec_system)

    context_prompt = f"""
        (日本語で対応してください。)

        {linux_prompt_text}

        --- システム仕様書 ---
        {spec_text}

    """

    model_settings = ModelSettings(
        tool_choice="auto",
        extra_body={"num_ctx": 8000}
    )
    agent = Agent(
        name="Assistant",
        instructions=context_prompt,
        model="gpt-oss:20b",
        model_settings=model_settings,
        mcp_servers=[mcp_server]
    )

    session = SQLiteSession(session_id="conversation_123", db_path=":memory:")

    while True:
        user_input = input("You: ")

        if user_input.strip().lower() in ("exit", "q"):
            print("会話を終了します。")
            break

        run_config = RunConfig(model_provider=provider)
        result = await Runner.run(starting_agent=agent, input=user_input, session=session, max_turns=30, run_config=run_config)

        print("AI:", result.final_output)

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

    session.close()
    await mcp_server.cleanup()

#-----------------------------------------------------------------
asyncio.run(main())

