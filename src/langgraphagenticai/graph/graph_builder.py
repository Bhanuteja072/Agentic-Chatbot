from langgraph.graph import StateGraph
from langgraph.prebuilt import tools_condition
from langgraph.graph import START,END
from src.langgraphagenticai.state.State import State
from src.langgraphagenticai.Nodes.basic_chatbot_node import BasicChatbotNode
from src.langgraphagenticai.tools.basic_tool import get_tools,create_tool_node
class GraphBuilder:
    def __init__(self,model):
        self.llm=model
        self.graph_builder=StateGraph(State)

    def basic_chatbot_build_graph(self):
        """
        Builds a basic chatbot graph using LangGraph.
        This method initializes a chatbot node using the `BasicChatbotNode` class 
        and integrates it into the graph. The chatbot node is set as both the 
        entry and exit point of the graph.
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








        self.graph_builder.add_node("chatbot","")
        self.graph_builder.add_node("tools",tool_node)
        self.graph_builder.add_edge(START,"chatbot")
        self.graph_builder.add_conditional_edges(
            "chatbot",
            tools_condition
        )
        self.graph_builder.add_edge("tools","chatbot")
        self.graph_builder.add_edge("chatbot",END)



    def setup_graph(self,usecase : str):
        """
            Sets up graph for selected usecase
        """
        if usecase == "Basic Chatbot":
            self.basic_chatbot_build_graph()
        if usecase == "Chatbot with web":
            self.chatbot_with_tool_build_graph()
        return self.graph_builder.compile()

        
