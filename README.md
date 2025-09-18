# LangGraph AgenticAI Chatbot

## Overview

**LangGraph AgenticAI** is an intelligent chatbot framework built using LangGraph and LangChain.  
It supports multiple usecases:

1. **Basic Chatbot** – A memory-enabled chatbot that remembers conversation context across messages.
2. **Chatbot with Web/Tools** – A chatbot integrated with external tools or web services for dynamic responses.

The application uses **Streamlit** as the frontend, allowing interactive chat with the AI.  
It leverages `MemorySaver` for persistent conversational memory in the Basic Chatbot usecase and supports multiple threads using `thread_id`.

---

## Features

- Memory-enabled conversation for Basic Chatbot.
- Tool-augmented responses for advanced chatbot usecases.
- Dynamic Streamlit chat UI with full chat history.
- Supports multiple user sessions with unique `thread_id`.
- Modular design: LLM nodes, tools, and graph builder separated for scalability.
- Easy integration of new LLMs or tools.
