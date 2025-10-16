from langgraph.graph import StateGraph
from langgraph.prebuilt import tools_condition
from langgraph.graph import START,END
from typing import Optional
import os
from langchain.schema import Document
from src.langgraphagenticai.state.State import State
from src.langgraphagenticai.state.State import GraphState
from src.langgraphagenticai.Nodes.basic_chatbot_node import BasicChatbotNode
from src.langgraphagenticai.tools.basic_tool import get_tools,create_tool_node
from src.langgraphagenticai.Nodes.chatbot_with_toolnode import ChatbotWithTool
from langgraph.checkpoint.memory import MemorySaver
from src.langgraphagenticai.Nodes.ai_news_node import AINewsNode
from src.langgraphagenticai.Nodes.chatwithpdf_node import retrieve , generate , grade_docs , transform_query , route_question, decide_to_generate , grade_generation_v_documents_and_question
# from src.langgraphagenticai.tools.PDFtool import PDFTool
from src.langgraphagenticai.tools.PDFtool import build_pdf_retriever

from src.langgraphagenticai.tools.WebTool import WebTool
from langchain_tavily  import TavilySearch
from src.langgraphagenticai.Nodes.chatwithpdf_node import init_components

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
        """Builds graph for AI News Summarizer (Fetch → Summarize → Save)."""


        ai_news_node=AINewsNode(self.llm)

        self.graph_builder.add_node("Fetch_news",ai_news_node.fetch_news)
        self.graph_builder.add_node("Summarize",ai_news_node.summarize_news)
        self.graph_builder.add_node("save_result",ai_news_node.save_result)


        self.graph_builder.add_edge(START,"Fetch_news")
        self.graph_builder.add_edge("Fetch_news","Summarize")
        self.graph_builder.add_edge("Summarize","save_result")
        self.graph_builder.add_edge("save_result",END)


    def chat_with_pdf_graph(self , pdf_path: Optional[str] = None , urls: list[str] = None,tavily_key : Optional[str] = None ,user_input: dict = None):
        """
        Build the nodes for chat-with-pdf. This function DOES NOT run websearch or retriever
        at graph build time; it registers functions (wrappers) that will run when the graph executes.
        """
        if urls:
            web_tool = WebTool(urls)
            retriever = web_tool.get_retriever()
        else:   
            retriever = build_pdf_retriever(pdf_path)
            # pdf_tool = PDFTool(pdf_path)
            # retriever = pdf_tool.get_retriever()
        if tavily_key:  
            os.environ["TAVILY_API_KEY"] = tavily_key
        web_search_tool = TavilySearch(k=3) if os.environ.get("TAVILY_API_KEY") else None

        def websearch(state : GraphState):
            """
                Web search based on the re-phrased question.

                Args:
                    state (dict): The current graph state

                Returns:
                    state (dict): Updates documents key with appended web results
            """
            print("---WEB SEARCH---")
            question = state["question"]
            #   web_search_tool = TavilySearch(k=3)
            docs = web_search_tool.invoke({"query": question})
            # print(docs)
            results = docs.get("results", [])
            web_results_text = "\n\n".join([r["content"] for r in results if r.get("content")])
            web_results = Document(page_content=web_results_text)
            return {"documents": web_results, "question": question}
        

        # Initialize components with the LLM
        (question_router, retrieval_grader, rag_chain,
        hallucination_grader, answer_grader, question_rewriter) = init_components(user_input)



  




        # chat_with_pdf_node=ChatWithPdfNode()

        # self.graph_builder.add_node("web_search",websearch)
        self.graph_builder.add_node("retrieve",lambda s: retrieve(s, retriever))
        self.graph_builder.add_node("transform_query",lambda s: transform_query(s, question_rewriter))
        self.graph_builder.add_node("grade_docs",lambda s: grade_docs(s, retrieval_grader))
        self.graph_builder.add_node("generate",lambda s: generate(s, rag_chain))

        # self.graph_builder.add_conditional_edges(
        #     START,
        #     lambda s : route_question(s , question_router),
        #     {
        #         "web_search": "web_search",
        #         "vectorstore": "retrieve",
        #     }
        # )
        self.graph_builder.add_edge(START,"retrieve")
        # self.graph_builder.add_edge("web_search","generate")
        self.graph_builder.add_edge("retrieve", "grade_docs")
        self.graph_builder.add_conditional_edges(
            "grade_docs",
            decide_to_generate,
                {
                    "transform_query": "transform_query",
                    "generate": "generate",
                },
        )

        self.graph_builder.add_edge("transform_query", "retrieve")
        self.graph_builder.add_conditional_edges(
            "generate",
            lambda s : grade_generation_v_documents_and_question(s, hallucination_grader, answer_grader),
                {
                    "not supported": "generate",
                    "useful": END,
                    "not useful": "transform_query",
                },
        )

 



    def setup_graph(self,usecase : str, user_input: dict = None ,**kwargs ):
        """
            Sets up graph for selected usecase.
            Only Basic Chatbot uses memory; other usecases compile normally.
            user_input: the dictionary returned by LoadStreamlitUI() (so we can read pdf_path/TAVILY_API_KEY)

        """

        self.graph_builder = StateGraph(State)

        if usecase == "Basic Chatbot":
            self.basic_chatbot_build_graph()
            return self.graph_builder.compile()
        elif usecase == "Chatbot with web":
            self.chatbot_with_tool_build_graph()
            return self.graph_builder.compile()
        elif usecase == "AI News Summarizer":
            self.ai_news_graph()
            return self.graph_builder.compile()
        elif usecase == "ChatWithPdf":
            tavily_key = None
            pdf_path = None
            if user_input:
                tavily_key = user_input.get("TAVILY_API_KEY")
                pdf_path = user_input.get("pdf_path")

            if not pdf_path:
                pdf_path = kwargs.get("pdf_path") or "./default.pdf"
              # verify pdf exists before proceeding
            if not pdf_path or not os.path.isfile(pdf_path):
                raise ValueError("No PDF uploaded or PDF file not found. Please upload a PDF in the UI before selecting Chat With PDF.")

            self.graph_builder = StateGraph(GraphState)
            self.chat_with_pdf_graph(pdf_path= pdf_path ,tavily_key=tavily_key,user_input=user_input)
            return self.graph_builder.compile()
        elif usecase == "ChatWithWebsite":
            urls = None
            if user_input:
                urls = user_input.get("urls")
            if not urls:
                raise ValueError("No URLs provided. Please enter at least one URL.")
            self.graph_builder = StateGraph(GraphState)
            self.chat_with_pdf_graph(urls=urls, user_input=user_input)
            return self.graph_builder.compile()
        # default fallback
        return self.graph_builder.compile()


        
