# LangGraph Agentic AI — Stateful Agentic Graphs with Streamlit

Build and run stateful, production-style AI workflows using LangGraph + LangChain with a Streamlit UI. This project ships multiple use cases (basic chat, tool-augmented chat, AI news summarization, Chat-With-PDF RAG, Chat-With-Website RAG, and AI Blog Generator) wired as graphs with clear nodes, edges, and state.

Highlights
- Streamlit UI with selectable LLM provider and use cases
- Groq LLM integration with model selector
- Tools: Tavily web search (optional), Wikipedia
- RAG pipelines for PDF and Website content (FAISS + HuggingFace embeddings)
- AI Blog Generator with topic and optional translation flows (Hindi/French)
- Graph-based orchestration powered by LangGraph
- Beginner-friendly setup and usage on Windows

--------------------------------------------------------------------------------

Project structure
- app.py — Streamlit entrypoint
- src/langgraphagenticai/
  - main.py — Streamlit bootstrap
  - graph/graph_builder.py — compiles graphs per use case
  - llms/groqllm.py — Groq LLM wrapper
  - Nodes/
    - basic_chatbot_node.py — basic chat
    - chatbot_with_toolnode.py — chat with tools
    - ai_news_node.py — AI news fetch + LLM summarization
    - chatwithpdf_node.py — RAG nodes (router/graders/generator/query rewriter)
    - blog_node.py — blog title/content generation, routing, translation
  - state/
    - State.py — TypedDicts for State/GraphState and structured output models
    - blog_state.py — BlogState for blog generator graph
  - tools/
    - basic_tool.py — TavilySearch + Wikipedia tools and ToolNode
    - PDFtool.py — PDF loading/splitting, FAISS retriever
    - WebTool.py — URL fetching (requests + BeautifulSoup), splitting, FAISS retriever
  - ui/
    - uiconfigfile.ini — UI options (LLM, models, use cases)
    - streamlitui/
      - loadui.py — sidebar, inputs (keys, uploads, URLs)
      - display_result.py — renders results per use case

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
- Fetches recent AI news using the Tavily Python client and summarizes with the LLM.
- Accepts natural language or JSON input:
  - Example JSON: {"frequency":"weekly","news_query":"LLM regulation"}
  - Frequencies: daily, weekly, monthly, year
- Writes a markdown summary to ./AINews/{daily|weekly|monthly|year|custom}_summary.md.

4) ChatWithPdf (RAG + routing)
- Upload a PDF; it’s parsed and chunked, embedded with HuggingFace (all-MiniLM-L6-v2).
- FAISS vectorstore created in-memory; questions can be routed to:
  - vectorstore: retrieve → grade → generate → grade
  - web_search: Tavily (optional, if TAVILY_API_KEY set)
- UI shows answer and up to 5 supporting chunks.

5) ChatWithWebsite (RAG over URLs)
- Enter one or multiple website URLs (comma separated) in the sidebar.
- The app fetches pages via requests + BeautifulSoup, cleans text, chunks, embeds, and builds a FAISS retriever.
- Same RAG flow used as ChatWithPdf; optional web_search routing via Tavily if key provided.
- UI shows answer and supporting chunks grouped by source URL.

6) AI Blog Generator
- Generate long-form, SEO-friendly blogs from a topic.
- Flow A (Topic): H1 title → full Markdown blog (intro, TOC, 8–12 sections, conclusion).
- Flow B (Language): Title → content → route → optional translation (Hindi/French).
- Renders on the main page (not sidebar). Supports large outputs; tune token limits via env.

--------------------------------------------------------------------------------

Prerequisites
- OS: Windows (tested)
- Python: 3.10+ recommended
- API keys:
  - GROQ_API_KEY (required for LLM)
  - TAVILY_API_KEY (required for web tools, AI News, and optional web routing in RAG use cases)

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
# AI News uses Tavily Python client (if not already installed):
pip install tavily
```

4) Provide API keys

Option A — environment variables (current shell)
```powershell
$env:GROQ_API_KEY = 'your_groq_api_key'
$env:TAVILY_API_KEY = 'your_tavily_api_key'
```

Option B — permanent (user scope)
```powershell
setx GROQ_API_KEY "your_groq_api_key"
setx TAVILY_API_KEY "your_tavily_api_key"
# Open a new PowerShell after setx for variables to load
```

Option C — via Streamlit UI
- In the sidebar, select Groq and paste your GROQ key.
- For web-enabled flows, paste your Tavily key.

5) Run
```powershell
streamlit run app.py
```

--------------------------------------------------------------------------------

How to use

1) In the sidebar
- Select LLM: Groq
- Choose a model (e.g., qwen/qwen3-32b)
- Paste your GROQ API key
- Select a Use Case

2) Chatbot with web
- Paste TAVILY_API_KEY to enable live web search.

3) AI News Summarizer
- Type a prompt (e.g., “weekly ai funding news”) or send JSON: {"frequency":"weekly","news_query":"Generative AI funding"}
- Or choose frequency and click “Fetch Latest AI News”
- Summary is saved to ./AINews/<frequency>_summary.md and displayed in the UI.

4) ChatWithPdf
- Optionally set TAVILY_API_KEY (for web routing).
- Upload a PDF and ask a question.
- Terminal prints chunk counts/previews for debugging.

5) ChatWithWebsite
- Enter one or more website URLs (comma separated) in the sidebar.
- Ask your question; the app builds a retriever from those pages.
- Optional web routing via Tavily if TAVILY_API_KEY is set.

6) AI Blog Generator
- Enter a topic in the main page and click Generate.
- Optional: select a translation target (Hindi or French) to run the language flow.
- If outputs truncate, raise token limits (see Troubleshooting).

--------------------------------------------------------------------------------

Architecture overview

- UI (src/langgraphagenticai/ui/streamlitui)
  - loadui.py: collects keys, model, use case, PDF upload, URLs; renders Blog Generator header on main page
  - display_result.py: renders per-use case outputs; normalizes docs/blog outputs and shows debug state in an expander

- Graph builder (src/langgraphagenticai/graph/graph_builder.py)
  - Builds graphs per use case
  - ChatWithPdf/ChatWithWebsite share the same RAG wiring:
    - Retriever source: PDFTool (pdf path) or WebTool (urls)
    - Router, graders, RAG prompt/chain
    - Edges:
      START
        -> route_question (vectorstore | web_search)
        -> retrieve -> grade_docs -> (transform_query | generate)
        -> generate -> grade_generation_v_documents_and_question -> (useful | not useful | not supported)
        -> END
  - AI Blog Generator:
    - Topic graph: START -> title -> content -> END
    - Language graph: START -> title -> content -> route -> (hindi|french) -> END

- Nodes
  - basic_chatbot_node.py — basic chat
  - chatbot_with_toolnode.py — LLM with tools (Tavily + Wikipedia)
  - ai_news_node.py — Tavily client fetch + LLM summarization, JSON-friendly
  - chatwithpdf_node.py — router/graders/generator/query rewriter + node functions
  - blog_node.py — title/content generation, routing, translation

- Tools
  - basic_tool.py — TavilySearch, Wikipedia tools + ToolNode
  - PDFtool.py — Unstructured/PyPDF, splitting, FAISS, embeddings
  - WebTool.py — requests + BeautifulSoup scraping, splitting, FAISS, embeddings

- State
  - State.py — graph state definitions and Pydantic models for structured outputs
  - blog_state.py — BlogState typed state for blog graphs

--------------------------------------------------------------------------------

Environment variables

Required
- GROQ_API_KEY — Groq LLM key

For web-enabled flows (recommended)
- TAVILY_API_KEY — used by “Chatbot with web”, “AI News Summarizer”, and web routes in RAG

Optional (Blog Generator, long-form)
- GROQ_MAX_TOKENS — override max tokens (e.g., 3000–4096) for long content

Set in Windows PowerShell (temporary)
```powershell
$env:GROQ_API_KEY = 'your_groq_api_key'
$env:TAVILY_API_KEY = 'your_tavily_api_key'
$env:GROQ_MAX_TOKENS = '3000'
```

--------------------------------------------------------------------------------

Performance tips

- Cache heavy objects (embeddings, vectorstores, LLMs, compiled graphs) with st.cache_resource.
- Persist FAISS per PDF/URL set (hash input) to avoid rebuilding on reruns.
- Prefer PyPDFLoader; fallback to Unstructured for tricky PDFs.
- Pre-download HuggingFace model locally and set HF_EMBEDDINGS_LOCAL_DIR.

--------------------------------------------------------------------------------

Troubleshooting

- groq.GroqError: The api_key client option must be set…
  - Provide GROQ_API_KEY via env or sidebar.

- ChatWithPdf/ChatWithWebsite: 'NoneType' object has no attribute 'invoke'
  - Ensure a PDF is uploaded or URLs are provided; set TAVILY_API_KEY if you expect web routing.

- Error processing PDF: 'Document' object is not subscriptable
  - Occurs when code assumes list but receives a single Document. UI normalizes results to lists.

- HuggingFace download errors (MaxRetryError / HTTPSConnectionPool)
  - Network/proxy issue. Use stable internet, set proxies/CA bundle, or pre-download the model and point embeddings to a local folder.

- Windows symlink warning from huggingface_hub
  - Enable Developer Mode (Settings > Privacy & Security > For developers) or ignore (warning only). To avoid symlinks, pre-download with local_dir_use_symlinks=False.

- Blog content truncates
  - Raise token limit via $env:GROQ_MAX_TOKENS (e.g., 3000–4096) or bind higher max_tokens for the content node.

--------------------------------------------------------------------------------

Acknowledgements
- LangGraph, LangChain, FAISS, HuggingFace, Groq, Tavily, BeautifulSoup, Wikipedia community tools.
