import os
import streamlit as st
from langchain_groq import ChatGroq

class GroqLlm:
    def __init__(self,user_controls_input):
        self.user_controls_input = user_controls_input
    def get_llm_mode(self):
        try:
            groq_api_key=self.user_controls_input["GROQ_API_KEY"]
            selected_llm_model=self.user_controls_input["selected_groq_model"]
            
            if groq_api_key == "" and os.environ["GROQ_API_KEY"] == "":
                st.error("Please enter he groq API key")
            llm = ChatGroq(api_key=groq_api_key,model=selected_llm_model)
        except Exception as e:
            raise ValueError(f"Error occured with: {e}")
        return llm


    
        