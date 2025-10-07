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
    - ai_news_node.py — AI news fetch + LLM summarization (Tavily client, JSON-friendly)
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

3) AI News Summarizer (enhanced)
- Fetches recent AI news using the official Tavily Python client and summarizes with the LLM.
- Accepts both free text and structured JSON input:
  - Example JSON: {"frequency":"weekly","news_query":"LLM regulation"}
  - Valid frequencies: daily, weekly, monthly, year
- Produces a clean markdown summary and saves it to:
  - ./AINews/{daily|weekly|monthly|year|custom}_summary.md

4) ChatWithPdf (RAG + routing)
- Upload a PDF, it’s parsed and chunked, embedded with HuggingFace (all-MiniLM-L6-v2).
- FAISS vectorstore created in-memory; questions are routed:
  - vectorstore: retrieve top chunks, grade relevance, generate, grade hallucinations/answer
  - web_search: fetch via Tavily search when needed (if TAVILY_API_KEY provided)
- The UI shows the answer and up to 5 supporting chunks.

--------------------------------------------------------------------------------

Prerequisites
- OS: Windows (tested)
- Python: 3.10+ recommended
- Accounts/API keys:
  - GROQ_API_KEY (required for LLM)
  - TAVILY_API_KEY (required for web search, “Chatbot with web”, and AI News Summarizer; optional for Chat-With-PDF unless routing selects web_search)

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
# AI News Summarizer uses the Tavily Python client:
pip install tavily
```

Note: requirements.txt includes:
- langchain, langgraph, langchain_community, langchain_core, langchain_groq
- langchain_tavily (for tools integration)
- langchain-huggingface, faiss-cpu, pypdf
- streamlit, wikipedia

4) Provide API keys

Option A — environment variables (current shell session)
```powershell
$env:GROQ_API_KEY = 'your_groq_api_key'
$env:TAVILY_API_KEY = 'your_tavily_api_key'
```

Option B — permanent (user scope)
```powershell
setx GROQ_API_KEY "your_groq_api_key"
setx TAVILY_API_KEY "your_tavily_api_key"
# Open a new PowerShell after setx for the variables to load
```

Option C — via Streamlit UI
- In the sidebar, select Groq and paste your GROQ API key.
- For web-enabled use cases (Chatbot with web, AI News Summarizer, some ChatWithPdf routes), paste your Tavily API key.

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

2) Chatbot with web
- Paste your TAVILY_API_KEY to enable live web results via tools.

3) AI News Summarizer
- Choose frequency (daily/weekly/monthly/year).
- Optionally provide a custom query in the UI or type JSON in the chat:
  - {"frequency":"weekly","news_query":"Generative AI startups funding"}
- After fetching/summarizing, the markdown is saved to ./AINews/<frequency>_summary.md.

4) ChatWithPdf
- Optionally paste your TAVILY_API_KEY (if routing to web_search is desired).
- Upload a PDF and ask your question.
- Terminal prints first few chunk previews for debugging.

--------------------------------------------------------------------------------

Architecture overview

- Streamlit UI (src/langgraphagenticai/ui/streamlitui):
  - loadui.py collects keys, model, use case, and PDF upload path
  - display_result.py renders outputs per use case (with safety checks)

- Graph Builder (src/langgraphagenticai/graph/graph_builder.py):
  - Builds graphs per use case on demand
  - ChatWithPdf wiring:
    - PDFTool(pdf_path) -> FAISS -> retriever
    - Router, graders, RAG prompt/chain
    - Edges:
      START
        -> route_question (vectorstore | web_search)
        -> retrieve -> grade_docs -> (transform_query | generate)
        -> generate -> grade_generation_v_documents_and_question -> (useful | not useful | not supported)
        -> END

- Nodes:
  - basic_chatbot_node.py — Basic chat
  - chatbot_with_toolnode.py — LLM with tools (Tavily + Wikipedia)
  - ai_news_node.py — TavilyClient fetch + LLM summarization, JSON-friendly inputs, writes markdown
  - chatwithpdf_node.py — RAG components: router, graders, generator, query rewriter, nodes

- Tools:
  - basic_tool.py — returns TavilySearch and Wikipedia tools + ToolNode
  - PDFtool.py — Unstructured/PyPDF loading, text splitting, FAISS, HuggingFace embeddings

- State:
  - State.py — Graph/Message state and structured outputs

--------------------------------------------------------------------------------

Environment variables

Required
- GROQ_API_KEY — Groq LLM key

Required for web-enabled flows
- TAVILY_API_KEY — used by “Chatbot with web”, “AI News Summarizer”, and web routes in “ChatWithPdf”

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

- AI News returns empty or errors
  - Ensure TAVILY_API_KEY is set and valid.
  - Try a simpler query or a different frequency.

- ChatWithPdf: list index out of range / no chunks
  - PDF may have no extractable text. Try another PDF or use a loader that supports your format (scanned PDFs may require OCR).
  - Check terminal logs for “[ChatWithPdf] Loaded X document(s)” and “Produced Y chunk(s)”.

- 'NoneType' object has no attribute 'invoke'
  - A component (retriever or tool) was None, but .invoke(...) was called.
  - Ensure a PDF is uploaded (to build the retriever) and provide TAVILY_API_KEY if routing to web_search.

- Error processing PDF: 'Document' object is not subscriptable
  - Caused by treating a single Document as a list.
  - The UI normalizes results to a list before slicing; keep returns consistent (prefer lists of Document).

- HuggingFace embeddings download errors (MaxRetryError / HTTPSConnectionPool)
  - Network/proxy blocking downloads. Use stable internet, set proxies/CA bundle, or pre-download the model and point embeddings to a local folder.

--------------------------------------------------------------------------------

Notes and limitations
- Embeddings: HuggingFace all-MiniLM-L6-v2 via langchain-huggingface.
- Vectorstore: In-memory FAISS; not persisted.
- PDF parsing: Unstructured/PyPDF; scanned PDFs may require OCR.
- LLMs: Groq first-class; OpenAI appears in UI config but is not wired.

--------------------------------------------------------------------------------

Development tips
- Reinstall dependencies when changing Python versions: pip install -r requirements.txt
- For debugging PDF splits, check terminal logs after uploading a PDF in ChatWithPdf.
- Keep directory casing consistent on Windows when committing paths (Git is case-sensitive; NTFS is not).

--------------------------------------------------------------------------------

Acknowledgements
- LangGraph, LangChain, FAISS, HuggingFace, Groq, Tavily, Wikipedia community tools.
