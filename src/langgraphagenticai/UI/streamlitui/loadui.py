import streamlit as st
import os
from src.langgraphagenticai.ui.uiconfigfile import Config

class LoadStreamlitUI:
    def __init__(self):
        self.config = Config()
        self.user_controls = {}

    def load_streamlit_ui(self):
        st.set_page_config(page_title="🤖 " + self.config.get_page_title(), layout="wide")

        st.header("🤖 " + self.config.get_page_title())
        st.session_state.timeframe = ""
        st.session_state.IsFetchButtonClicked = False

        with st.sidebar:
            # Get options from config
            llm_options = self.config.get_llm_options()
            usecase_options = self.config.get_usecase_options()

            # LLM selection
            self.user_controls["selected_llm"] = st.selectbox("Select LLM", llm_options)

            if self.user_controls["selected_llm"] == "Groq":
                # Model selection
                model_options = self.config.get_groq_model_options()
                self.user_controls["selected_groq_model"] = st.selectbox("Select Model", model_options)
                self.user_controls["GROQ_API_KEY"] = st.session_state["GROQ_API_KEY"] = st.text_input("API Key", type="password")

                # Validate API key
                if not self.user_controls["GROQ_API_KEY"]:
                    st.warning("⚠️ Please enter your GROQ API key to proceed. Don't have? refer : https://console.groq.com/keys ")

            # Usecase selection
            self.user_controls["selected_usecase"] = st.selectbox("Select Usecases", usecase_options)

            # === AI News Summarizer ===
            if self.user_controls["selected_usecase"] == "Chatbot with web" or self.user_controls["selected_usecase"] == "AI News Summarizer":
                os.environ["TAVILY_API_KEY"] = self.user_controls["TAVILY_API_KEY"] = st.session_state["TAVILY_API_KEY"] = st.text_input("Tavily Key", type="password")
                if not self.user_controls["TAVILY_API_KEY"]:
                    st.warning("⚠️ Please enter your Tavily API key to proceed. Don't have? refer : https://app.tavily.com/home")

            if self.user_controls["selected_usecase"] == "AI News Summarizer":
                st.subheader("📰 AI News Explorer ")
                with st.sidebar:
                    time_frame = st.selectbox(
                        "📅 Select Time Frame",
                        ["Daily", "Weekly", "Monthly"],
                        index=0
                    )
                if st.button("🔍 Fetch Latest AI News", use_container_width=True):
                    st.session_state.IsFetchButtonClicked = True
                    st.session_state.timeframe = time_frame

            # === Chat With PDF ===
            if self.user_controls["selected_usecase"] == "ChatWithPdf":
                os.environ["TAVILY_API_KEY"] = self.user_controls["TAVILY_API_KEY"] = st.session_state["TAVILY_API_KEY"] = st.text_input("Tavily Key", type="password")
                if not self.user_controls["TAVILY_API_KEY"]:
                    st.warning("⚠️ Please enter your Tavily API key to proceed. Don't have? refer : https://app.tavily.com/home")

                uploaded_file = st.file_uploader("📄 Upload a PDF", type="pdf")
                if uploaded_file:
                    pdf_dir = "./uploaded_pdfs"
                    os.makedirs(pdf_dir, exist_ok=True)
                    pdf_path = os.path.join(pdf_dir, uploaded_file.name)
                    with open(pdf_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    self.user_controls["pdf_path"] = pdf_path
                else:
                    self.user_controls["pdf_path"] = None
                    st.info("Upload a PDF to start chatting with it.")

        return self.user_controls
