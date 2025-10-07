# import sys, io
# import os
# import streamlit as st
# from src.langgraphagenticai.ui.streamlitui.loadui import LoadStreamlitUI
# from src.langgraphagenticai.llms.groqllm import GroqLlm
# from src.langgraphagenticai.graph.graph_builder import GraphBuilder
# from src.langgraphagenticai.ui.streamlitui.display_result import DisplayResultStreamlit
# # Force UTF-8 for stdout and stderr
# sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
# sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")


# # Also force default encoding for file writes
# os.environ["PYTHONIOENCODING"] = "utf-8"



# def load_langgraph_agenticai_app():
#     """
#     Loads and runs the LangGraph AgenticAI application with Streamlit UI.
#     This function initializes the UI, handles user input, configures the LLM model,
#     sets up the graph based on the selected use case, and displays the output while 
#     implementing exception handling for robustness.

#     """

#     #Load Ui
#     ui=LoadStreamlitUI()
#     user_input=ui.load_streamlit_ui()

#     if not user_input:
#         st.error("Error: Failed to load user input from the UI.")
#         return

#     # user_message=st.chat_input("Enter your message: ")
#     if st.session_state.IsFetchButtonClicked:
#         user_message = st.session_state.timeframe
#     else:
#         user_message = st.chat_input("Enter your message:")


#     if user_message:
#         try:
#             obj_llm_config=GroqLlm(user_controls_input=user_input)
#             model=obj_llm_config.get_llm_mode()
#             if not model:
#                 st.error ("Error :LLM Model could not Initilize")
#                 return
#             usecase=user_input.get("selected_usecase")
#             if not usecase:
#                 st.error("Error: Use Case is not fetched")
            
#             graph_builder=GraphBuilder(model)
#             try:
#                 graph=graph_builder.setup_graph(usecase,user_input)
#                 DisplayResultStreamlit(usecase,graph,user_message).display_result_on_ui()
#             except Exception as e:
#                 st.error(f"Error : Graph Setup Failed -{e}")
#                 return
#         except Exception as e:
#                 st.error(f"Error : Graph Setup Failed -{e}")
#                 return














import sys, io
import os
import streamlit as st
import json as _json

from src.langgraphagenticai.ui.streamlitui.loadui import LoadStreamlitUI
from src.langgraphagenticai.llms.groqllm import GroqLlm
from src.langgraphagenticai.graph.graph_builder import GraphBuilder
from src.langgraphagenticai.ui.streamlitui.display_result import DisplayResultStreamlit

# Force UTF-8 for all streams
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
os.environ["PYTHONIOENCODING"] = "utf-8"


def load_langgraph_agenticai_app():
    """
    Loads and runs the LangGraph AgenticAI application with Streamlit UI.
    Handles UI loading, model setup, graph initialization, and safe exception handling.
    """

    # Load UI controls
    ui = LoadStreamlitUI()
    user_input = ui.load_streamlit_ui()

    if not user_input:
        st.error("Error: Failed to load user input from the UI.")
        return

    usecase = user_input.get("selected_usecase", "")

    # === Handle user input depending on usecase ===
    user_message = None
    if st.session_state.IsFetchButtonClicked:
        # Special handling for AI News Summarizer (structured input)
        if usecase == "AI News Summarizer":
            frequency = user_input.get("frequency", st.session_state.timeframe)
            news_query = user_input.get("news_query", st.session_state.user_prompt)
            user_message = _json.dumps({"frequency": frequency, "news_query": news_query})
        else:
            user_message = st.session_state.timeframe
    else:
        # Default chat input for other use cases
        if usecase != "AI News Summarizer":
            user_message = st.chat_input("Enter your message:")

    # === Proceed only if message is entered ===
    if user_message:
        try:
            obj_llm_config = GroqLlm(user_controls_input=user_input)
            model = obj_llm_config.get_llm_mode()
            if not model:
                st.error("Error: LLM Model could not be initialized.")
                return

            graph_builder = GraphBuilder(model)
            try:
                graph = graph_builder.setup_graph(usecase, user_input)
                DisplayResultStreamlit(usecase, graph, user_message).display_result_on_ui()
            except Exception as e:
                st.error(f"Error: Graph setup failed - {e}")
                return

        except Exception as e:
            st.error(f"Error: LLM setup failed - {e}")
            return
