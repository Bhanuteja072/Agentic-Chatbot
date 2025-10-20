import streamlit as st
from langchain_core.messages import HumanMessage,AIMessage,ToolMessage
import json
import uuid
from typing import Optional 
import unicodedata
from langchain.schema import Document

from src.langgraphagenticai import graph  # add this import

def normalize_text(text: str) -> str:
    """Convert text to safe ASCII/UTF-8 by removing unsupported characters."""
    if not isinstance(text, str):
        return str(text)
    # Keep UTF-8 if possible, fall back to ASCII for weird symbols
    return unicodedata.normalize("NFKD", text).encode("utf-8", "ignore").decode("utf-8")



class DisplayResultStreamlit:
    def __init__(self,usecase,graph,user_message,language : Optional[str]=None):
        self.usecase= usecase
        self.graph = graph
        self.user_message = user_message
        if language:
            self.language = language

        self.language = language or ""



        
        # # ensure each Streamlit session has a persistent thread_id
        # if "thread_id" not in st.session_state:
        #     st.session_state.thread_id = str(uuid.uuid4())


    def display_result_on_ui(self):

        usecase= self.usecase
        graph = self.graph
        user_message = self.user_message
        if usecase == "Basic Chatbot":
            # Each Streamlit session gets its own thread_id
            if "thread_id" not in st.session_state:
                import uuid
                st.session_state.thread_id = str(uuid.uuid4())

            if "chat_history" not in st.session_state:
                st.session_state.chat_history = []

            st.session_state.chat_history.append(("user", user_message))

            # Pass session_id to BasicChatbotNode
            state_input = {
                "messages": [HumanMessage(content=user_message)],
                "session_id": st.session_state.thread_id
            }

            # Stream response
            for event in graph.stream(state_input):
                for value in event.values():
                    assistant_message = value["messages"][0][1]
                    st.session_state.chat_history.append(("assistant", assistant_message))

            # Render full chat history
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
            import json as _json

            # Handle both legacy string and new JSON message forms
            frequency = None
            news_query = None

            user_msg = self.user_message
            if isinstance(user_msg, str):
                try:
                    parsed = _json.loads(user_msg)
                    frequency = parsed.get("frequency", "Daily")
                    news_query = parsed.get("news_query", "")
                except Exception:
                    frequency = user_msg
                    news_query = ""
            elif isinstance(user_msg, dict):
                frequency = user_msg.get("frequency", "Daily")
                news_query = user_msg.get("news_query", "")
            else:
                frequency = str(user_msg)
                news_query = ""

            # Normalize frequency for safe file naming
            freq_str = (frequency or "Daily").lower()
            if freq_str not in ["daily", "weekly", "monthly", "year"]:
                freq_str = "daily"

            # Build the message payload for graph.invoke()
            content_str = _json.dumps({"frequency": freq_str, "news_query": news_query})
            message_content = {"role": "user", "content": content_str}

            with st.spinner("Fetching and summarizing news... ⏳"):
                # Graph expects list of message dicts
                result = graph.invoke({"messages": [message_content]})
                try:
                    AI_NEWS_PATH = f"./AINews/{freq_str}_summary.md"
                    with open(AI_NEWS_PATH, "r", encoding="utf-8", errors="replace") as file:
                        markdown_content = file.read()
                    st.markdown(markdown_content, unsafe_allow_html=True)
                except FileNotFoundError:
                    st.error(f"News Not Generated or File not found: {AI_NEWS_PATH}")
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")

        elif usecase == "ChatWithPdf":
            with st.spinner("Analyzing PDF and generating answer... ⏳"):
                try:
                    result = graph.invoke({"question": user_message})
                    answer = result.get("generation")
                    docs = result.get("documents", [])


                    # Normalize to a list of Document to avoid "'Document' object is not subscriptable"
                    if docs is None:
                        docs = []
                    elif isinstance(docs, Document):
                        docs = [docs]
                    elif isinstance(docs, dict) and "page_content" in docs:
                        docs = [Document(page_content=docs["page_content"])]
                    elif not isinstance(docs, list):
                        # Fallback: wrap unknown type as string
                        docs = [Document(page_content=str(docs))]

                    with st.chat_message("user"):
                        st.write(user_message)

                    if answer:
                        with st.chat_message("assistant"):
                            st.subheader("📖 Answer")
                            st.write(answer)

                    if docs:
                        with st.expander("🔎 Supporting PDF Chunks"):
                            for i, d in enumerate(docs[:5]):  # show first 5 chunks
                                st.markdown(f"**Chunk {i+1}:**")
                                st.write(d.page_content)

                except Exception as e:
                    st.error(f"Error processing PDF: {str(e)}")

        elif usecase == "AI Blog Generator":
            with st.spinner("Generating blog... ⏳"):

                try:
                    if self.language:
                        state = graph.invoke({"topic": user_message, "current_language": self.language})
                    else:
                        state = graph.invoke({"topic": user_message})

                    # === Display structured results ===
                    blog = state.get("blog") if isinstance(state, dict) else getattr(state, "blog", None)
                    if blog:
                        title = blog.get("title") if isinstance(blog, dict) else None
                        content = blog.get("content") if isinstance(blog, dict) else None
                        if title:
                            st.markdown(f"## {title}")
                        if content:
                            st.markdown(content, unsafe_allow_html=True)
                    else:
                        st.info("No structured 'blog' field found. Showing raw state below.")
                        st.json(state)

                    st.subheader("📦 Raw State")
                    st.json(state)

                except Exception as e:
                    st.error(f"Error: {e}")
                    st.exception(e)

        elif usecase == "ChatWithWebsite":
            with st.spinner("Fetching website(s) and generating answer... ⏳"):
                try:
                    result = graph.invoke({"question": user_message})
                    answer = result.get("generation")
                    docs = result.get("documents", [])

                    # Normalize to a list of Document
                    if docs is None:
                        docs = []
                    elif isinstance(docs, Document):
                        docs = [docs]
                    elif isinstance(docs, dict) and "page_content" in docs:
                        docs = [Document(page_content=docs["page_content"], metadata=docs.get("metadata", {}))]
                    elif not isinstance(docs, list):
                        docs = [Document(page_content=str(docs))]

                    # Show user message
                    with st.chat_message("user"):
                        st.write(user_message)

                    # Show assistant answer
                    if answer:
                        with st.chat_message("assistant"):
                            st.subheader("🌐 Answer")
                            st.write(answer)

                    # Show supporting chunks grouped by URL
                    if docs:
                        # Group chunks by source URL
                        from collections import defaultdict
                        grouped_docs = defaultdict(list)
                        for d in docs:
                            src = d.metadata.get("source", "Unknown source")
                            grouped_docs[src].append(d)

                        st.subheader("🔎 Supporting Website Chunks")
                        for source, source_docs in grouped_docs.items():
                            with st.expander(f"Source: {source}"):
                                for i, d in enumerate(source_docs[:5]):  # limit 5 per site
                                    st.markdown(f"**Chunk {i+1}:**")
                                    st.write(d.page_content)

                except Exception as e:
                    st.error(f"Error processing website(s): {str(e)}")
