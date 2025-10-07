# from tavily  import TavilyClient
# from langchain_core.prompts import ChatPromptTemplate


# class AINewsNode:
#     def __init__(self,llm):
#         """
#         Initialize the AINewsNode with API keys for Tavily and GROQ.
#         """
#         self.tavily = TavilyClient()
#         self.llm = llm
#         # this is used to capture various steps in this file so that later can be use for steps shown
#         self.state = {}

#     def fetch_news(self, state: dict) -> dict:
#         """
#         Fetch AI news based on the specified frequency.
        
#         Args:
#             state (dict): The state dictionary containing 'frequency'.
        
#         Returns:
#             dict: Updated state with 'news_data' key containing fetched news.
#         """

#         frequency = state['messages'][0].content.lower()
#         self.state['frequency'] = frequency
#         time_range_map = {'daily': 'd', 'weekly': 'w', 'monthly': 'm', 'year': 'y'}
#         days_map = {'daily': 1, 'weekly': 7, 'monthly': 30, 'year': 366}

#         response = self.tavily.search(
#             query="Top Artificial Intelligence (AI) technology news India and globally",
#             topic="news",
#             time_range=time_range_map[frequency],
#             include_answer="advanced",
#             max_results=20,
#             days=days_map[frequency],
#             # include_domains=["techcrunch.com", "venturebeat.com/ai", ...]  # Uncomment and add domains if needed
#         )

#         state['news_data'] = response.get('results', [])
#         self.state['news_data'] = state['news_data']
#         return state
    

#     def summarize_news(self, state: dict) -> dict:
#         """
#         Summarize the fetched news using an LLM.
        
#         Args:
#             state (dict): The state dictionary containing 'news_data'.
        
#         Returns:
#             dict: Updated state with 'summary' key containing the summarized news.
#         """

#         news_items = self.state['news_data']

#         prompt_template = ChatPromptTemplate.from_messages([
#             ("system", """Summarize AI news articles into markdown format. For each item include:
#             - Date in **YYYY-MM-DD** format in IST timezone
#             - Concise sentences summary from latest news
#             - Sort news by date wise (latest first)
#             - Source URL as link
#             Use format:
#             ### [Date]
#             - [Summary](URL)"""),
#             ("user", "Articles:\n{articles}")
#         ])

#         articles_str = "\n\n".join([
#             f"Content: {item.get('content', '')}\nURL: {item.get('url', '')}\nDate: {item.get('published_date', '')}"
#             for item in news_items
#         ])

#         response = self.llm.invoke(prompt_template.format(articles=articles_str))
#         state['summary'] = response.content
#         self.state['summary'] = state['summary']
#         return self.state
    
#     def save_result(self,state):
#         freq=self.state["frequency"]
#         summary=self.state["summary"]
#         file_name=f"./AINews/{freq}_summary.md"
#         with open (file_name,'w',encoding="utf-8", errors="replace")as f:
#             f.write(f"#{freq.capitalize()} AI News Summary\n\n")
#             f.write(summary)
#         self.state['filename']=file_name
#         return self.state







from tavily import TavilyClient
from langchain_core.prompts import ChatPromptTemplate
import json as _json
import re
import os


class AINewsNode:
    def __init__(self, llm):
        """
        Initialize AINewsNode with Tavily client and provided LLM.
        """
        self.tavily = TavilyClient()
        self.llm = llm
        self.state = {}

    # -------------------------------------------------------------------------
    def fetch_news(self, state: dict) -> dict:
        """
        Fetch AI news based on the specified frequency and optional query/prompt.
        Supports both legacy string and new JSON message inputs.
        """
        default_query = "Top Artificial Intelligence (AI) technology news India and globally"

        msg = state["messages"][0]
        # Extract raw content
        if isinstance(msg, dict) and "content" in msg:
            msg_content = msg["content"]
        else:
            msg_content = getattr(msg, "content", msg)

        # Try parsing JSON if available
        frequency = None
        query = None
        if isinstance(msg_content, str):
            try:
                parsed = _json.loads(msg_content)
                frequency = parsed.get("frequency", "").lower()
                query = parsed.get("news_query", "") or parsed.get("query", "")
            except Exception:
                frequency = str(msg_content).lower()
                query = None
        elif isinstance(msg_content, dict):
            frequency = msg_content.get("frequency", "").lower()
            query = msg_content.get("news_query", "") or msg_content.get("query", "")
        else:
            frequency = str(msg_content).lower()
            query = None

        valid_freqs = ["daily", "weekly", "monthly", "year"]
        if frequency not in valid_freqs:
            frequency = "daily"

        self.state["frequency"] = frequency

        # Map to Tavily params
        time_range_map = {"daily": "d", "weekly": "w", "monthly": "m", "year": "y"}
        days_map = {"daily": 1, "weekly": 7, "monthly": 30, "year": 366}

        # Construct query string
        if query and str(query).strip():
            if frequency in str(query).lower():
                search_query = str(query).strip()
            else:
                search_query = f"{frequency} {query.strip()} news"
        else:
            search_query = default_query

        response = self.tavily.search(
            query=search_query,
            topic="news",
            time_range=time_range_map.get(frequency, "d"),
            include_answer="advanced",
            max_results=20,
            days=days_map.get(frequency, 1),
        )

        state["news_data"] = response.get("results", [])
        self.state["news_data"] = state["news_data"]
        return state

    # -------------------------------------------------------------------------
    def summarize_news(self, state: dict) -> dict:
        """Summarize fetched news using the LLM and return markdown summary."""
        news_items = self.state.get("news_data", [])

        prompt_template = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """Summarize AI news articles into markdown format. For each item include:
                    - Date in **YYYY-MM-DD** format (IST timezone)
                    - Concise sentences summary from latest news
                    - Sort by latest first
                    - Source URL as clickable link
                    Format:
                    ### [Date]
                    - [Summary](URL)""",
                ),
                ("user", "Articles:\n{articles}"),
            ]
        )

        articles_str = "\n\n".join(
            [
                f"Content: {item.get('content', '')}\nURL: {item.get('url', '')}\nDate: {item.get('published_date', '')}"
                for item in news_items
            ]
        )

        response = self.llm.invoke(prompt_template.format(articles=articles_str))
        summary_text = getattr(response, "content", str(response))
        state["summary"] = summary_text
        self.state["summary"] = summary_text
        return self.state

    # -------------------------------------------------------------------------
    def save_result(self, state):
        """
        Save summarized news to ./AINews/{frequency}_summary.md
        Handles both legacy and JSON inputs safely.
        """
        freq = self.state.get("frequency")

        # Defensive decoding if JSON-like
        if isinstance(freq, str):
            f_strip = freq.strip()
            if f_strip.startswith("{") or f_strip.startswith("["):
                try:
                    parsed = _json.loads(f_strip)
                    if isinstance(parsed, dict):
                        freq = parsed.get("frequency") or parsed.get("timeframe")
                except Exception:
                    freq = None

        # Try extracting frequency from messages if still missing
        if not freq:
            try:
                msg = state.get("messages", [None])[0]
                content = msg.get("content") if isinstance(msg, dict) else str(msg)
                parsed = _json.loads(content)
                if isinstance(parsed, dict):
                    freq = parsed.get("frequency") or parsed.get("timeframe")
            except Exception:
                freq = None

        # Validate/normalize
        valid = ["daily", "weekly", "monthly", "year"]
        if isinstance(freq, str):
            m = re.search(r"(daily|weekly|monthly|year)", freq, flags=re.I)
            freq = m.group(1).lower() if m else freq.strip().lower()
        else:
            freq = "custom"

        if freq not in valid:
            freq_clean = "custom"
        else:
            freq_clean = freq

        # Write markdown
        summary = self.state.get("summary", "")
        os.makedirs("./AINews", exist_ok=True)
        file_name = f"./AINews/{freq_clean}_summary.md"
        with open(file_name, "w", encoding="utf-8", errors="replace") as f:
            f.write(f"#{freq_clean.capitalize()} AI News Summary\n\n")
            f.write(summary)
        self.state["filename"] = file_name
        return self.state
