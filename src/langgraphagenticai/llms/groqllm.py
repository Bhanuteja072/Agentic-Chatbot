# import os
# import streamlit as st
# from langchain_groq import ChatGroq

# class GroqLlm:
#     def __init__(self,user_controls_input):
#         self.user_controls_input = user_controls_input
#     def get_llm_mode(self):
#         try:
#             groq_api_key=self.user_controls_input["GROQ_API_KEY"]
#             selected_llm_model=self.user_controls_input["selected_groq_model"]
            
#             if groq_api_key == "" and os.environ["GROQ_API_KEY"] == "":
#                 st.error("Please enter he groq API key")
#             llm = ChatGroq(api_key=groq_api_key,model=selected_llm_model)
#         except Exception as e:
#             raise ValueError(f"Error occured with: {e}")
#         return llm


    
# src/langgraphagenticai/llms/groqllm.py
import os
import streamlit as st
from langchain_groq import ChatGroq

class GroqLlm:
    def __init__(self, user_controls_input):
        self.user_controls_input = user_controls_input

    def get_llm_mode(self):
        """
        Return an initialized ChatGroq instance, or None if initialization failed
        (UI will display an error and abort).
        """
        try:
            # Ensure safe lookups
            selected_llm = self.user_controls_input.get("selected_llm")
            # We only initialize ChatGroq if Groq is selected
            if selected_llm != "Groq":
                return None

            groq_api_key = (
                self.user_controls_input.get("GROQ_API_KEY")
                or os.environ.get("GROQ_API_KEY", "")
            )
            selected_llm_model = self.user_controls_input.get("selected_groq_model") or os.environ.get("GROQ_MODEL")

            if not groq_api_key:
                # Show a helpful message in the UI and return None so main() aborts gracefully
                st.error("Please enter your GROQ API key in the sidebar (GROQ).")
                return None

            # Set env var too so other parts that expect it can read it
            os.environ["GROQ_API_KEY"] = groq_api_key

            # Instantiate ChatGroq with explicit api_key (this avoids relying only on env)
            llm = ChatGroq(api_key=groq_api_key, model=selected_llm_model)
            return llm

        except Exception as e:
            # Show friendly error and return None so main() can show a single error message
            st.error(f"Error initializing GROQ LLM: {e}")
            return None
