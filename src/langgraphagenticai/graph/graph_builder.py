from langgraph.graph import StateGraph
from langgraph.prebuilt import tools_condition
from langgraph.graph import START,END
from src.langgraphagenticai.state.State import State
from src.langgraphagenticai.Nodes.basic_chatbot_node import BasicChatbotNode
from src.langgraphagenticai.tools.basic_tool import get_tools,create_tool_node
from src.langgraphagenticai.Nodes.chatbot_with_toolnode import ChatbotWithTool
from langgraph.checkpoint.memory import MemorySaver
from src.langgraphagenticai.Nodes.ai_news_node import AINewsNode

class GraphBuilder:
    def __init__(self,model):
        self.llm=model
        self.memory = MemorySaver()

        # self.graph_builder=StateGraph(State)

    def basic_chatbot_build_graph(self):
        """
        Builds a basic chatbot graph using LangGraph.
        """

        self.basic_chatbot_node = BasicChatbotNode(self.llm)
        self.graph_builder.add_node("chatbot",self.basic_chatbot_node.process)
        self.graph_builder.add_edge(START,"chatbot")
        self.graph_builder.add_edge("chatbot",END)


    def chatbot_with_tool_build_graph(self):
        """
        Builds an advanced chatbot graph with tool integration.
        This method creates a chatbot graph that includes both a chatbot node 
        and a tool node. It defines tools, initializes the chatbot with tool 
        capabilities, and sets up conditional and direct edges between nodes. 
        The chatbot node is set as the entry point.
        """

        tools=get_tools()
        tool_node=create_tool_node(tools)

        llm=self.llm

        obj_with_toolnode=ChatbotWithTool(llm)
        chatbot_node=obj_with_toolnode.create_chatbot(tools)


        self.graph_builder.add_node("chatbot",chatbot_node)
        self.graph_builder.add_node("tools",tool_node)
        self.graph_builder.add_edge(START,"chatbot")
        self.graph_builder.add_conditional_edges(
            "chatbot",
            tools_condition
        )
        self.graph_builder.add_edge("tools","chatbot")
        self.graph_builder.add_edge("chatbot",END)

    
    def ai_news_graph(self):

        ai_news_node=AINewsNode(self.llm)

        self.graph_builder.add_node("Fetch_news",ai_news_node.fetch_news)
        self.graph_builder.add_node("Summarize",ai_news_node.summarize_news)
        self.graph_builder.add_node("save_result",ai_news_node.save_result)


        self.graph_builder.add_edge(START,"Fetch_news")
        self.graph_builder.add_edge("Fetch_news","Summarize")
        self.graph_builder.add_edge("Summarize","save_result")
        self.graph_builder.add_edge("save_result",END)







    def setup_graph(self,usecase : str):
        """
            Sets up graph for selected usecase.
            Only Basic Chatbot uses memory; other usecases compile normally.
        """

        self.graph_builder = StateGraph(State)

        if usecase == "Basic Chatbot":
            self.basic_chatbot_build_graph()
            return self.graph_builder.compile(checkpointer=self.memory)
        elif usecase == "Chatbot with web":
            self.chatbot_with_tool_build_graph()
            return self.graph_builder.compile()
        # default fallback
        return self.graph_builder.compile()


        
