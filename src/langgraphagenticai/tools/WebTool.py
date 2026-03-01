# src/langgraphagenticai/tools/WebTool.py

import requests
from bs4 import BeautifulSoup
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document



def clean_web_text(text: str) -> str:
    import re
    text = re.sub(r"\s+", " ", text)  # collapse whitespace
    text = re.sub(r"(Archive|Tags|Search|FAQ|Lil'Log|Posts)+", "", text, flags=re.IGNORECASE)
    return text.strip()

class WebTool:
    def __init__(self, urls: list[str]):
        self.urls = urls
        self.embedding = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.vectorstore = None
        self.retriever = None
        self._prepare_urls()
    def _fetch_text_from_url(self, url: str) -> str:
        """Fetch and clean text from a single URL."""
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            # Remove script/style tags
            for script in soup(["script", "style"]):
                script.extract()

            raw_text = soup.get_text(separator=" ", strip=True)
            return clean_web_text(raw_text)   # ✅ clean before returning
        except Exception as e:
            return f"Failed to load {url}: {str(e)}"

    def _prepare_urls(self):
        docs_list = []
        for url in self.urls:
            text = self._fetch_text_from_url(url)
            docs_list.append(Document(page_content=text, metadata={"source": url}))

        # Merge text for chunking
        text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
            chunk_size=500,
            chunk_overlap=100,
            separators=["\n\n", "\n", " ", ""]
        )
        doc_splits = text_splitter.split_documents(docs_list)

        # Create FAISS vectorstore
        self.vectorstore = FAISS.from_documents(doc_splits, self.embedding)
        self.retriever = self.vectorstore.as_retriever()

    def get_retriever(self):
        if self.retriever is None:
            self._prepare_urls()
        return self.retriever
