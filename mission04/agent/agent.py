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
    HostedMCPTool,
    MCPToolApprovalFunctionResult,
    MCPToolApprovalRequest,
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

def approval_callback(request: MCPToolApprovalRequest) -> MCPToolApprovalFunctionResult:
    answer = input(f"Approve running the tool `{request.data.name}`? (y/n) ")
    result: MCPToolApprovalFunctionResult = {"approve": answer == "y"}
    if not result["approve"]:
        result["reason"] = "User denied"
    return result

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
    set_default_openai_key(key="lmstudio", use_for_tracing=False)
    # enable_verbose_stdout_logging()

    mcp_server = ExtendedMCPServerStdio(
        params={
            "command": "C:\\tools\\cabal\\bin\\pty-mcp-server.exe",
            "args": ["-y", "C:\\work\\lambda-tuber\\ai-trial\\mission04\\pty-mcp-server.yaml"],
            "timeout":30,
        },
        client_session_timeout_seconds=30
    )

    # 
    # https://github.com/openai/openai-agents-python/issues/1008
    #  HostedMCPTool は ChatCompletions API ではサポートされていません。
    #    set_default_openai_api("chat_completions")
    #
    hosted_tool = HostedMCPTool(
        tool_config=mcp_server,
        on_approval_request=approval_callback
    )

    await mcp_server.connect()

    logger.info("=========================================")
    logger.info("list_resources()")
    logger.info("=========================================")
    resources_list = await mcp_server.list_resources()
    logger.info(resources_list)
    logger.info("")

    logger.info("=========================================")
    logger.info('get_resource("file:///spec_system.md")')
    logger.info("=========================================")
    spec_system = await mcp_server.get_resource("file:///spec_system.md")
    logger.info(spec_system)
    spec_text = "\n".join(item.text for item in spec_system)
    logger.info(spec_text)
    logger.info("")

    logger.info("=========================================")
    logger.info("list_prompts()")
    logger.info("=========================================")
    prompts_list = await mcp_server.list_prompts()
    logger.info(prompts_list)
    logger.info("")

    logger.info('=========================================')
    logger.info('get_prompt("linux_admin_prompt", {})')
    logger.info('=========================================')
    linux_admin_prompt = await mcp_server.get_prompt("linux_admin_prompt", {})
    logger.info(linux_admin_prompt)
    linux_prompt_text = "\n".join(m.content.text for m in linux_admin_prompt.messages if hasattr(m.content, "text"))
    logger.info(linux_prompt_text)
    logger.info("")

    context_prompt = f"""
        (必ず日本語で回答してください。)

        {linux_prompt_text}

        --- システム仕様書 ---
        {spec_text}

    """
    logger.info('=========================================')
    logger.info('context_prompt')
    logger.info('=========================================')
    logger.info(context_prompt)
    logger.info("")
    
    instruction_prompt = f"""
      現状のサーバが、仕様書通りの設定になってるかサーバに接続して確認してください。その際、設定変更は絶対しないでください。
      proc-sshでサーバに接続し、proc-messageで情報収集コマンドを発行してください。"
    """
    logger.info('=========================================')
    logger.info('instruction_prompt')
    logger.info('=========================================')
    logger.info(instruction_prompt)
    logger.info("")

    agent = Agent(
        name="Assistant",
        instructions=context_prompt,
        #model="gpt-oss-20b",
        model="gpt-oss:20b",
        # model="gemma3:12b",
        model_settings=ModelSettings(tool_choice="auto", extra_body={"num_ctx": 8000}),
        mcp_servers=[mcp_server],
        # tools=[hosted_tool]
    )

    run_config = RunConfig(model_provider=provider)
    result = await Runner.run(starting_agent=agent, input=instruction_prompt, max_turns=30, run_config=run_config)
    print(result.final_output)

    await mcp_server.cleanup()

#-----------------------------------------------------------------
asyncio.run(main())

# MEMO
#
# Measure-Command { python .\agent.py | Out-Default }
#
# set OLLAMA_CONTEXT_LENGTH=8000
#