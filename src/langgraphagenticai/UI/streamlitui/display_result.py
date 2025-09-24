import streamlit as st
from langchain_core.messages import HumanMessage,AIMessage,ToolMessage
import json
import uuid
import unicodedata
def normalize_text(text: str) -> str:
    """Convert text to safe ASCII/UTF-8 by removing unsupported characters."""
    if not isinstance(text, str):
        return str(text)
    # Keep UTF-8 if possible, fall back to ASCII for weird symbols
    return unicodedata.normalize("NFKD", text).encode("utf-8", "ignore").decode("utf-8")



class DisplayResultStreamlit:
    def __init__(self,usecase,graph,user_message):
        self.usecase= usecase
        self.graph = graph
        self.user_message = user_message

        
        # # ensure each Streamlit session has a persistent thread_id
        # if "thread_id" not in st.session_state:
        #     st.session_state.thread_id = str(uuid.uuid4())


    def display_result_on_ui(self):
        usecase= self.usecase
        graph = self.graph
        user_message = self.user_message
        if usecase == "Basic Chatbot":
                  # ensure each Streamlit session has a persistent thread_id
            if "thread_id" not in st.session_state:
                st.session_state.thread_id = str(uuid.uuid4())
                # Initialize UI chat history
            if "chat_history" not in st.session_state:
                st.session_state.chat_history = []
            st.session_state.chat_history.append(("user", user_message))

            # state_input = {"messages": [("user", user_message)]}
            # Wrap user message as HumanMessage so MemorySaver works
            state_input = {"messages": [HumanMessage(content=user_message)]}



            # Stream response from the graph
            for event in graph.stream(state_input,config={"configurable": {"thread_id": st.session_state.thread_id}}):
                for value in event.values():
                    assistant_message = value["messages"][0][1]
                    # Append assistant reply to chat history
              
                    st.session_state.chat_history.append(("assistant", assistant_message))
            
    # Render the full chat history
            for role, msg in st.session_state.chat_history:
                with st.chat_message(role):
                    st.write(msg)





        elif usecase=="Chatbot with web":
             # Prepare state and invoke the graph
            initial_state = {"messages": [user_message]}
            res = graph.invoke(initial_state)
            for message in res['messages']:
                if type(message) == HumanMessage:
                    with st.chat_message("user"):
                        st.write(message.content)
                elif type(message)==ToolMessage:
                    with st.chat_message("ai"):
                        st.write("Tool Call Start")
                        st.write(message.content)
                        st.write("Tool Call End")
                elif type(message)==AIMessage and message.content:
                    with st.chat_message("assistant"):
                        st.write(message.content)
        elif usecase == "AI News Summarizer":
            frequency = self.user_message
            with st.spinner("Fetching and summarizing news... ⏳"):
                result = graph.invoke({"messages": frequency})
                try:
                    # Read the markdown file
                    AI_NEWS_PATH = f"./AINews/{frequency.lower()}_summary.md"
                    with open(AI_NEWS_PATH, "r",encoding="utf-8", errors="replace") as file:
                        markdown_content = file.read()

                    # safe_markdown = normalize_text(markdown_content)

                    # Display the markdown content in Streamlit
                    st.markdown(markdown_content, unsafe_allow_html=True)
                except FileNotFoundError:
                    st.error(f"News Not Generated or File not found: {AI_NEWS_PATH}")
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")