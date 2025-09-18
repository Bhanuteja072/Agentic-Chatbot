from langchain_tavily  import TavilySearch
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from langgraph.prebuilt import ToolNode



def get_tools():
    """
        Return list of tools to be used in chatbot
    """
    tavily_tool = TavilySearch(max_results=2,description="Use this tool to search the live web for the latest or real-time information.")
    wikipedia_api = WikipediaAPIWrapper()
    wikipedia_tool = WikipediaQueryRun(api_wrapper=wikipedia_api,description="Use this tool to fetch factual and historical information from Wikipedia.")
    tools = [tavily_tool, wikipedia_tool]
    # for t in tools:
    #     print(f"Loaded tool: {t.name}")

    return tools

def create_tool_node(tools):
    """
        Creates and return tool node for grapph
    """
    return ToolNode(tools=tools)
