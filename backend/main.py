import asyncio
import argparse
import uvicorn
import uuid
from agents import Runner, SQLiteSession
from agent import create_agent

# Single global session and agent for the CLI
_cli_session = None
_cli_agent = None

def get_cli_session():
    """Get the global CLI session."""
    global _cli_session
    if _cli_session is None:
        _cli_session = SQLiteSession(session_id="cli", db_path=":memory:")
    return _cli_session

def get_cli_agent():
    """Get the global CLI agent with fresh state."""
    global _cli_agent
    if _cli_agent is None:
        _cli_agent = create_agent()
    return _cli_agent

async def run_single_message(user_input: str):
    """Process a single message in the conversation."""
    session = get_cli_session()
    agent = get_cli_agent()

    result = Runner.run_streamed(
        agent,
        input=user_input,
        session=session,
    )

    print("Assistant is thinking...\n")

    async for event in result.stream_events():
        if event.type == 'run_item_stream_event':
            if event.name == 'tool_called':
                tool_name = event.item.raw_item.name
                tool_args = event.item.raw_item.arguments
                print(f"Calling tool: {tool_name}")
                if tool_args and tool_args != '{}':
                    print(f"   Arguments: {tool_args}")
                print()

            elif event.name == 'tool_output':
                output = event.item.output
                print(f"Tool output: {output}")
                print()

        elif event.type == 'raw_response_event':
            if event.data.type == 'response.output_text.delta':
                print(event.data.delta, end='', flush=True)

            elif event.data.type == 'response.output_text.done':
                print("\n")  # Add newline when text is complete

async def run_cli():
    print("=== ACCTA Agent Chat ===")
    print("Type 'exit' to quit, 'clear' to clear conversation history\n")

    # Interactive mode
    while True:
        try:
            user_input = input("You: ").strip()
            if user_input.lower() == 'exit':
                break
            elif user_input.lower() == 'clear':
                global _cli_session, _cli_agent
                session = get_cli_session()
                await session.clear_session()
                # Reset agent to get fresh state (let old one be garbage collected)
                _cli_agent = None
                print("Conversation history and state cleared.\n")
                continue
            elif not user_input:
                continue

            print()
            await run_single_message(user_input)

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except EOFError:
            print("\nGoodbye!")
            break

def run_server(host: str = "0.0.0.0", port: int = 8000):
    uvicorn.run("api:app", host=host, port=port, reload=True)

def main():
    parser = argparse.ArgumentParser(description="ACCTA Agent")
    parser.add_argument("--mode", choices=["cli", "server"], default="cli", help="Run mode")
    parser.add_argument("--host", default="0.0.0.0", help="Server host")
    parser.add_argument("--port", type=int, default=8000, help="Server port")

    args = parser.parse_args()

    if args.mode == "cli":
        asyncio.run(run_cli())
    elif args.mode == "server":
        run_server(args.host, args.port)

if __name__ == "__main__":
    main()
