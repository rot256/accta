import asyncio
from agents import Agent, Runner, function_tool

@function_tool
def generate_haiku():
    return "Recursion is a tool\nTo solve problems, it's cool\nProgramming is fun!"

agent = Agent(
    name="Assistant",
    instructions="You are a helpful assistant",
    tools=[generate_haiku],
)

async def main():
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

asyncio.run(main())
