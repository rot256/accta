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
    async for event in result.stream_events():
        print(f"Event: {type(event).__name__}")
        print(f"Data: {event}")
        print("-" * 50)

asyncio.run(main())
