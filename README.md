# LangGraph Agentic AI — Stateful Agentic Graphs with Streamlit

Build and run stateful, production-style AI workflows using LangGraph + LangChain and a Streamlit UI. This project includes multiple use cases (basic chat, tool-augmented chat, AI news summarization, and Chat-With-PDF RAG) wired as graphs with clear nodes, edges, and state.

Highlights
- Streamlit UI with selectable LLM provider and use cases
- Groq LLM integration with model selector
- Tools: Tavily web search, Wikipedia
- RAG pipeline for Chat-With-PDF (FAISS + HuggingFace embeddings)
- Graph-based orchestration powered by LangGraph
- Beginner-friendly setup and usage

--------------------------------------------------------------------------------

Project structure
- app.py — Streamlit entrypoint
- src/langgraphagenticai/
  - main.py — Streamlit app bootstrap: loads UI, builds graph, dispatches
  - graph/graph_builder.py — compiles graphs per use case
  - llms/groqllm.py — Groq LLM wrapper
  - Nodes/
    - basic_chatbot_node.py — simple LLM chat node
    - chatbot_with_toolnode.py — chat with tools node
    - ai_news_node.py — fetch + summarize AI news with Tavily + LLM
    - chatwithpdf_node.py — Chat-With-PDF graph node functions (RAG router/grader, etc.)
  - state/State.py — TypedDicts for State/GraphState and data models for structured outputs
  - tools/
    - basic_tool.py — tool definitions (TavilySearch + Wikipedia) and ToolNode
    - PDFtool.py — PDF loader/splitter, FAISS vectorstore and retriever
  - ui/streamlitui/
    - loadui.py — sidebar and input controls (LLM selection, keys, upload)
    - display_result.py — renders results per use case
  - ui/uiconfigfile.ini — UI options (LLM, models, use cases)

--------------------------------------------------------------------------------

Use cases
1) Basic Chatbot
- Stateless chat with the selected LLM.

2) Chatbot with web
- Uses tools to augment answers:
  - TavilySearch (live web)
  - WikipediaQueryRun
- LangGraph ToolNode handles tool invocation via the LLM.

3) AI News Summarizer
- Fetches recent AI news via Tavily (tavily client) and summarizes with the LLM.
- Writes a markdown summary to ./AINews/{daily|weekly|monthly}_summary.md.

4) ChatWithPdf (RAG + routing)
- Upload a PDF, it’s parsed and chunked, embedded with HuggingFace (all-MiniLM-L6-v2).
- FAISS vectorstore created in-memory; questions are routed:
  - vectorstore: retrieve top chunks, grade relevance, generate, grade hallucinations/answer
  - web_search: fetch via Tavily search when needed
- The UI shows the answer and up to 5 supporting chunks.

--------------------------------------------------------------------------------

Prerequisites
- OS: Windows (tested)
- Python: 3.10+ recommended
- Accounts/API keys:
  - Groq API key (required for LLM)
  - Tavily API key (required for web search, chatbot-with-web and AI News Summarizer; optional for Chat-With-PDF unless routing selects web_search)

--------------------------------------------------------------------------------

Setup

1) Clone
```powershell
git clone https://github.com/your-org/AgenticChatBot.git
cd AgenticChatBot
```

2) Create and activate a virtual environment (Windows PowerShell)
```powershell
python -m venv .venv
. .\.venv\Scripts\Activate.ps1
```

3) Install dependencies
```powershell
pip install --upgrade pip
pip install -r requirements.txt
# Optional: if you use AI News Summarizer (tavily client) and it's not installed
pip install tavily
```

Note: requirements.txt already includes:
- langchain, langgraph, langchain_community, langchain_core, langchain_groq
- langchain_tavily (for tools)
- langchain-huggingface
- faiss-cpu
- pypdf
- streamlit, wikipedia

4) Provide API keys

Option A — via environment variables (session only)
```powershell
$env:GROQ_API_KEY = 'your_groq_api_key'
$env:TAVILY_API_KEY = 'your_tavily_api_key'  # needed for web search features
```

Option B — permanently (user scope)
```powershell
setx GROQ_API_KEY "your_groq_api_key"
setx TAVILY_API_KEY "your_tavily_api_key"
# Open a new PowerShell after setx for the variables to load
```

Option C — via Streamlit UI
- In the sidebar, select Groq and paste your GROQ API key.
- For use cases using web search, paste your Tavily API key.

5) Run the app
```powershell
streamlit run app.py
```

--------------------------------------------------------------------------------

How to use

1) In the sidebar:
- Select LLM: Groq
- Choose a Groq model (e.g., qwen/qwen3-32b)
- Paste your GROQ API key
- Select a Use Case

2) For Chatbot with web or AI News Summarizer:
- Paste your Tavily API key

3) For AI News Summarizer:
- Pick Daily/Weekly/Monthly and click “Fetch Latest AI News”, then ask follow-ups in the chat input

4) For ChatWithPdf:
- Optionally paste your Tavily API key (recommended if questions might route to web_search)
- Upload a PDF
- Ask your question in the chat input
- The terminal will print debug info about PDF chunks (first few splits)

--------------------------------------------------------------------------------

Architecture overview

- Streamlit UI (src/langgraphagenticai/ui/streamlitui):
  - loadui.py collects keys, model, use case, and pdf upload path
  - display_result.py renders outputs per use case (with safety checks)

- Graph Builder (src/langgraphagenticai/graph/graph_builder.py):
  - Builds different graphs per use case on demand
  - For ChatWithPdf:
    - Creates PDFTool(pdf_path) -> FAISS -> retriever
    - Initializes RAG components (router, graders, rag prompt/chain)
    - Wires nodes and conditional edges:
      START
        -> route_question (vectorstore | web_search)
        -> retrieve -> grade_docs -> (transform_query | generate)
        -> generate -> grade_generation_v_documents_and_question -> (useful | not useful | not supported)
        -> END

- Nodes:
  - basic_chatbot_node.py — Basic chat
  - chatbot_with_toolnode.py — LLM with tools (Tavily + Wikipedia)
  - ai_news_node.py — Tavily client fetch + LLM summarization + write markdown
  - chatwithpdf_node.py — RAG components: router, graders, generator, query rewriter, and node functions

- Tools:
  - basic_tool.py — returns TavilySearch and Wikipedia tools + ToolNode
  - PDFtool.py — UnstructuredPDFLoader/TextSplitter/FAISS/HuggingFace embeddings; returns retriever

- State:
  - State.py — State/GraphState TypedDict and Pydantic models for structured outputs

--------------------------------------------------------------------------------

Environment variables

Required
- GROQ_API_KEY — Groq LLM key

Optional, recommended for web-enabled flows
- TAVILY_API_KEY — for Tavily web search (used by “Chatbot with web”, “AI News Summarizer”, and routing in “ChatWithPdf”)

Set in Windows PowerShell (temporary)
```powershell
$env:GROQ_API_KEY = 'your_groq_api_key'
$env:TAVILY_API_KEY = 'your_tavily_api_key'
```

--------------------------------------------------------------------------------

Troubleshooting

- groq.GroqError: The api_key client option must be set…
  - Cause: GROQ_API_KEY missing when creating the Groq client.
  - Fix: Set GROQ_API_KEY via environment variable or the sidebar and retry.

- Error: ChatWithPdf flow failed — list index out of range
  - Cause: Attempted to access an empty list of documents/chunks.
  - Fix: Ensure the uploaded PDF has extractable text. The app prints how many chunks were generated. For scanned PDFs, try a different loader or OCR before upload.

- 'NoneType' object has no attribute 'invoke'
  - Cause: A component like retriever or a tool was None and .invoke(...) was called.
  - Fix: Ensure a PDF is uploaded (so retriever is built) and supply TAVILY_API_KEY if using web search paths.

- Error processing PDF: 'Document' object is not subscriptable
  - Cause: Code assumed a list of Document(s) but received a single Document.
  - Fix: The UI normalizes results to a list before slicing (already handled in display_result.py). If you changed return shapes, ensure you always pass a list for documents.

- Web search returns empty or errors
  - Ensure TAVILY_API_KEY is set
  - Ask questions that are better answered by the PDF to remain in vectorstore path

- Windows encoding issues in terminal
  - The app enforces UTF-8 for stdout/stderr and file writes in main.py

--------------------------------------------------------------------------------

Notes and limitations
- Embeddings: Uses HuggingFace all-MiniLM-L6-v2 via langchain-huggingface.
- Vectorstore: In-memory FAISS; not persisted to disk.
- PDF parsing: Uses UnstructuredPDFLoader by default; if your PDF is image-only/scanned, text extraction may be limited.
- LLMs: UI lists Groq as primary. OpenAI appears in UI config but is not wired in this codebase.
- Internet tools: Tavily is used both via langchain_tavily (tools) and tavily client (AI News Summarizer).

--------------------------------------------------------------------------------

Development tips
- Reinstall dependencies when changing Python versions: pip install -r requirements.txt
- For debugging PDF splits, check terminal logs after uploading a PDF in ChatWithPdf.
- If you need to test without internet keys, stick to “Basic Chatbot” and PDF-only questions that route to “vectorstore”.

--------------------------------------------------------------------------------

Acknowledgements
- LangGraph, LangChain, FAISS, HuggingFace, Groq, Tavily, Wikipedia community tools.
