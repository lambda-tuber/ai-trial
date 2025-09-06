import asyncio
import agents
import logging
import sys
import utility


#-----------------------------------------------------------------
# ユーザ設定
#-----------------------------------------------------------------
project_dir = "C:\\work\\lambda-tuber\\ai-trial\\mission08"
pty_mcp_server = "C:\\tools\\cabal\\bin\\pty-mcp-server.exe"

global_session_db = ":memory:"
tachikoma_list = [
    {
        "name": "misato",                                      # 注：1件目がエントリープラグ(starting_agent)になる。
        "description": "MAGIシステムの三賢者を束ねるミサト",
        "llm": {
            "model": "gemma-3-27b",
            "base_url": "http://172.16.0.198:1234/v1",
            "api_key": "lmstudio"
        },
        "mcp_servers": [],
        "prompts": [],                                         # デフォルトプロンプトに追加があれば記載する。
        "resources": ["file:///MAGI_system_definition.md"],    # デフォルトリソースに追加があれば記載する。
    },
    {
        "name": "melchior",
        "description": "MAGIシステムの三賢者の一人メルキオール",
        "llm": {
            "model": "gemma-3-12b",
            "base_url": "http://172.16.0.100:1234/v1",
            "api_key": "lmstudio"
        },
        "mcp_servers": [],
    },
    {
        "name": "balthasar",
        "description": "MAGIシステムの三賢者の一人バルタザール",
        "llm": {
            "model": "gpt-oss-20b",
            "base_url": "http://172.16.0.43:1234/v1",
            "api_key": "lmstudio"
        },
        "mcp_servers": [],
    },
    {
        "name": "casper",
        "description": "MAGIシステムの三賢者の一人カスパー",
        "llm": {
            "model": "gemma-3-27b",
            "base_url": "http://172.16.0.198:1234/v1",
            "api_key": "lmstudio"
        },
        "mcp_servers": [],
    }
]

#-----------------------------------------------------------------
# システム設定
#-----------------------------------------------------------------
logger = logging.getLogger(__name__)
# agents.enable_verbose_stdout_logging()
agents.set_default_openai_api("chat_completions")
agents.set_tracing_disabled(True)


#-----------------------------------------------------------------
async def main():

    session = agents.SQLiteSession(session_id="conversation_global", db_path=global_session_db)
    run_configs = utility.create_run_configs(tachikoma_list)
    # run_config = utility.create_run_config(tachikoma_list) # for handoffs.
    
    mba_list, mcp_servers = await utility.generate_mcp_based_agents(project_dir, pty_mcp_server, tachikoma_list)
    utility.wiring_agent_tools(mba_list, run_configs, session)
    # utility.wiring_handoffs_agent(mba_list)

    starting_agent = mba_list[0]
    while True:
        user_input = input("You: ")

        if user_input.strip().lower() in ("exit", "q", "ｑ"):
            print("会話を終了します。")
            break

        if "" == user_input.strip():
            continue

        result = await agents.Runner.run(
            starting_agent=starting_agent,
            input=user_input,
            session=session,
            max_turns=100,
            run_config=run_configs[starting_agent.name]
        )

        print("AI:", result.final_output)

        await utility.update_memory(session, starting_agent, run_configs[starting_agent.name])

    session.close()
    for server in list(reversed(mcp_servers)):
        await server.cleanup()


#-----------------------------------------------------------------
asyncio.run(main())

