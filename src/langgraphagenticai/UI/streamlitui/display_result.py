import streamlit as st
from langchain_core.messages import HumanMessage,AIMessage,ToolMessage
import json
import uuid
from typing import Optional 
import unicodedata
from langchain_core.documents import Document
from fpdf import FPDF
import io
from src.langgraphagenticai import graph  # add this import

def normalize_text(text: str) -> str:
    """Convert text to safe ASCII/UTF-8 by removing unsupported characters."""
    if not isinstance(text, str):
        return str(text)
    # Keep UTF-8 if possible, fall back to ASCII for weird symbols
    return unicodedata.normalize("NFKD", text).encode("utf-8", "ignore").decode("utf-8")


def generate_conversation_pdf(chat_history: list) -> bytes:
    """Convert chat history to a downloadable PDF bytes object."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Title
    pdf.set_font("Arial", style="B", size=16)
    pdf.cell(0, 10, "Chat With PDF - Conversation History", ln=True, align="C")
    pdf.ln(5)
    pdf.set_font("Arial", size=11)
    pdf.cell(0, 8, f"Total Messages: {len(chat_history)}", ln=True, align="C")
    pdf.ln(8)

    # Messages
    for msg in chat_history:
        role = msg["role"]
        content = msg["content"]

        if role == "user":
            pdf.set_fill_color(220, 220, 220)
            pdf.set_font("Arial", style="B", size=11)
            pdf.cell(0, 8, "You:", ln=True, fill=True)
        else:
            pdf.set_fill_color(200, 230, 200)
            pdf.set_font("Arial", style="B", size=11)
            pdf.cell(0, 8, "Assistant:", ln=True, fill=True)

        pdf.set_font("Arial", size=10)
        # Handle long text with multi_cell
        safe_content = content.encode("latin-1", "replace").decode("latin-1")
        pdf.multi_cell(0, 7, safe_content)
        pdf.ln(4)

    return bytes(pdf.output())
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
            if "pdf_chat_history" not in st.session_state:
                st.session_state.pdf_chat_history = []
            # ✅ Check if user is asking for conversation download via text
            download_keywords = [
                "full conversation", "give me the conversation",
                "download conversation", "export conversation",
                "conversation history", "give me all questions",
                "give me above conversation"
            ]
            user_wants_download = any(
                    kw in user_message.lower() for kw in download_keywords
            )
            if user_wants_download and st.session_state.pdf_chat_history:
                # Just give them the PDF directly without invoking graph
                with st.chat_message("assistant"):
                    st.write("Here is your full conversation as a PDF. Click below to download")
                pdf_bytes = generate_conversation_pdf(st.session_state.pdf_chat_history)
                st.download_button(
                    label=" 📥 Download Conversation PDF",
                    data=pdf_bytes,
                    file_name="chat_with_pdf_conversation.pdf",
                    mime="application/pdf"
                )
                for msg in st.session_state.pdf_chat_history:
                    with st.chat_message(msg["role"]):
                        st.write(msg["content"])

            elif user_wants_download and not st.session_state.pdf_chat_history:
                with st.chat_message("assistant"):
                    st.write("There is no conversation history yet. Please ask some questions first.")

            else:
                with st.spinner("Analyzing PDF and generating answer... ⏳"):
                    try:
                        result = graph.invoke({"question": user_message,"chat_history": st.session_state.pdf_chat_history})
                        # Prefer "generation" but accept common alternates
                        def _extract_answer(res):
                            if isinstance(res, dict):
                                for k in ("generation", "answer", "output", "response", "result"):
                                    v = res.get(k)
                                    if isinstance(v, str) and v.strip():
                                        return v
                            return None
                        answer = _extract_answer(result)
                        docs = result.get("documents", []) if isinstance(result, dict) else []

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
                        st.session_state.pdf_chat_history.append({"role": "user", "content": user_message})
                        if answer:
                            st.session_state.pdf_chat_history.append({"role": "assistant", "content": answer})
                        # ✅ Step 2 — Render the FULL history once (includes current Q&A)
                        for msg in st.session_state.pdf_chat_history:
                            with st.chat_message(msg["role"]):
                                st.write(msg["content"])
                        # ✅ Download button always visible after conversation starts
                        if st.session_state.pdf_chat_history:
                            pdf_bytes = generate_conversation_pdf(st.session_state.pdf_chat_history)
                            st.download_button(
                                label="📥 Download Conversation as PDF",
                                data=pdf_bytes,
                                file_name="conversation.pdf",
                                mime="application/pdf"
                            )

                        if docs:
                            with st.expander("🔎 Supporting PDF Chunks"):
                                for i, d in enumerate(docs[:5]):  # show first 5 chunks
                                    st.markdown(f"**Chunk {i+1}:**")
                                    st.write(d.page_content)
                        if not answer and not docs:
                            st.info("No answer or supporting documents returned. Expand Debug to inspect state.")
                            with st.expander("Debug state"):
                                try:
                                    st.json(result if isinstance(result, dict) else {"result": str(result)})
                                except Exception:
                                    st.write(result)

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
            # Initialize website chat history in session state
            if "website_chat_history" not in st.session_state:
                st.session_state.website_chat_history = []
            
            # ✅ Check if user is asking for conversation download via text
            download_keywords = [
                "full conversation", "give me the conversation",
                "download conversation", "export conversation",
                "conversation history", "give me all questions",
                "give me above conversation"
            ]
            user_wants_download = any(
                    kw in user_message.lower() for kw in download_keywords
            )
            if user_wants_download and st.session_state.website_chat_history:
                # Just give them the PDF directly without invoking graph
                with st.chat_message("assistant"):
                    st.write("Here is your full conversation as a PDF. Click below to download")
                pdf_bytes = generate_conversation_pdf(st.session_state.website_chat_history)
                st.download_button(
                    label=" 📥 Download Conversation PDF",
                    data=pdf_bytes,
                    file_name="chat_with_website_conversation.pdf",
                    mime="application/pdf"
                )
                for msg in st.session_state.website_chat_history:
                    with st.chat_message(msg["role"]):
                        st.write(msg["content"])

            elif user_wants_download and not st.session_state.website_chat_history:
                with st.chat_message("assistant"):
                    st.write("There is no conversation history yet. Please ask some questions first.")

            else:
            
                with st.spinner("Fetching website(s) and generating answer... ⏳"):
                    try:
                        # Pass chat_history from session state into graph.invoke()
                        result = graph.invoke({"question": user_message, "chat_history": st.session_state.website_chat_history})
                        def _extract_answer(res):
                            if isinstance(res, dict):
                                for k in ("generation", "answer", "output", "response", "result"):
                                    v = res.get(k)
                                    if isinstance(v, str) and v.strip():
                                        return v
                            return None
                        answer = _extract_answer(result)
                        docs = result.get("documents", []) if isinstance(result, dict) else []

                        # Normalize to a list of Document
                        if docs is None:
                            docs = []
                        elif isinstance(docs, Document):
                            docs = [docs]
                        elif isinstance(docs, dict) and "page_content" in docs:
                            docs = [Document(page_content=docs["page_content"], metadata=docs.get("metadata", {}))]
                        elif not isinstance(docs, list):
                            docs = [Document(page_content=str(docs))]
                        st.session_state.website_chat_history.append({"role": "user", "content": user_message})
                        if answer:
                            st.session_state.website_chat_history.append({"role": "assistant", "content": answer})

                        for msg in st.session_state.website_chat_history:
                            with st.chat_message(msg["role"]):
                                st.write(msg["content"])
                        # ✅ Download button always visible after conversation starts
                        if st.session_state.website_chat_history:
                            pdf_bytes = generate_conversation_pdf(st.session_state.website_chat_history)
                            st.download_button(
                                label="📥 Download Conversation as PDF",
                                data=pdf_bytes,
                                file_name="website_conversation.pdf",
                                mime="application/pdf"
                            )

                        # Show supporting chunks grouped by URL
                        if docs:
                            # Group chunks by source Ud)
                            with st.expander("🔎 Supporting Website Chunks"):
                                    for i, d in enumerate(docs[:5]):  # show first 5 chunks
                                        st.markdown(f"**Chunk {i+1}:**")
                                        st.write(d.page_content)

                        if not answer and not docs:
                            st.info("No answer or supporting documents returned. Expand Debug to inspect state.")
                            with st.expander("Debug state"):
                                try:
                                    st.json(result if isinstance(result, dict) else {"result": str(result)})
                                except Exception:
                                    st.write(result)

                    except Exception as e:
                        st.error(f"Error processing website(s): {str(e)}")

        elif usecase == "ChatWithYoutube":
            with st.spinner("Fetching YouTube transcript and generating answer... ⏳"):
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
                            st.subheader("▶️ Answer")
                            st.write(answer)

                    # Show supporting chunks
                    if docs:
                        with st.expander("🔎 Supporting YouTube Transcript Chunks"):
                            for i, d in enumerate(docs[:5]):  # limit to first 5 chunks
                                st.markdown(f"**Chunk {i+1}:**")
                                st.write(d.page_content)

                except Exception as e:
                    st.error(f"Error processing YouTube transcript: {str(e)}")