import sys, io
import os
import streamlit as st
from src.langgraphagenticai.ui.streamlitui.loadui import LoadStreamlitUI
from src.langgraphagenticai.llms.groqllm import GroqLlm
from src.langgraphagenticai.graph.graph_builder import GraphBuilder
from src.langgraphagenticai.ui.streamlitui.display_result import DisplayResultStreamlit
# Force UTF-8 for stdout and stderr
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")


# Also force default encoding for file writes
os.environ["PYTHONIOENCODING"] = "utf-8"



def load_langgraph_agenticai_app():
    """
    Loads and runs the LangGraph AgenticAI application with Streamlit UI.
    This function initializes the UI, handles user input, configures the LLM model,
    sets up the graph based on the selected use case, and displays the output while 
    implementing exception handling for robustness.

    """

    #Load Ui
    ui=LoadStreamlitUI()
    user_input=ui.load_streamlit_ui()

    if not user_input:
        st.error("Error: Failed to load user input from the UI.")
        return

    # user_message=st.chat_input("Enter your message: ")
    if st.session_state.IsFetchButtonClicked:
        user_message = st.session_state.timeframe
    else:
        user_message = st.chat_input("Enter your message:")


    if user_message:
        try:
            obj_llm_config=GroqLlm(user_controls_input=user_input)
            model=obj_llm_config.get_llm_mode()
            if not model:
                st.error ("Error :LLM Model could not Initilize")
                return
            usecase=user_input.get("selected_usecase")
            if not usecase:
                st.error("Error: Use Case is not fetched")
            
            graph_builder=GraphBuilder(model)
            try:
                graph=graph_builder.setup_graph(usecase)
                DisplayResultStreamlit(usecase,graph,user_message).display_result_on_ui()
            except Exception as e:
                st.error(f"Error : Graph Setup Failed -{e}")
                return
        except Exception as e:
                st.error(f"Error : Graph Setup Failed -{e}")
                return





