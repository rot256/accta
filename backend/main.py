import asyncio
import argparse
import uvicorn
from agents import Runner
from agent import agent

async def run_cli():
    result = Runner.run_streamed(
        agent,
        input="Use the generate_haiku tool to write a haiku.",
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
