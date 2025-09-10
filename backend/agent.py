from agents import Agent, function_tool

@function_tool
def generate_haiku():
    return "Recursion is a tool\nTo solve problems, it's cool\nProgramming is fun!"

agent = Agent(
    name="Assistant",
    instructions="You are a helpful assistant",
    tools=[generate_haiku],
)