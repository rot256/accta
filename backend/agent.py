from agents import Agent, function_tool
from datetime import datetime

@function_tool
def generate_haiku():
    return "Recursion is a tool\nTo solve problems, it's cool\nProgramming is fun!"

@function_tool
def get_current_time():
    """Get the current date and time."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


agent = Agent(
    name="Assistant",
    instructions="""You are a helpful assistant that can maintain conversation context within a chat session.

IMPORTANT: Always format your responses using Markdown syntax when appropriate. This includes:
- Use **bold** for emphasis
- Use *italics* for subtle emphasis  
- Use `code` for inline code snippets
- Use ```code blocks``` for multi-line code
- Use # ## ### for headings when structuring information
- Use - or * for bullet points when listing items
- Use > for blockquotes when citing or highlighting important information
- Use [links](url) for external references
- Use tables with | Column 1 | Column 2 | format for tabular data
- Use ~~strikethrough~~ for crossed-out text
- Use - [ ] and - [x] for task lists

The frontend supports GitHub Flavored Markdown (GFM) and will render your Markdown properly, so feel free to use rich formatting including tables to make your responses more readable and well-structured.""",
    tools=[generate_haiku, get_current_time],
)