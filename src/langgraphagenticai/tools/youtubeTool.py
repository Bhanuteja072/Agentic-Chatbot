# src/langgraphagenticai/tools/youtubeTool.py
import yt_dlp
from langchain_community.document_loaders import YoutubeLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
import os
import streamlit as st
import re


def get_video_info(url: str):
    """Return basic metadata for a single YouTube URL."""
    try:
        ydl_opts = {"quiet": True, "skip_download": True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
        return {
            "title": info.get("title"),
            "author": info.get("uploader"),
            "description": info.get("description"),
            "publish_date": info.get("upload_date"),
            "views": info.get("view_count"),
            "duration": info.get("duration"),
            "source": url,
        }
    except Exception:
        return {"source": url}
    
def extract_video_id(url: str) -> str | None:
    u = (url or "").strip()
    if not u:
        return None
    if not re.match(r"^https?://", u, re.I):
        u = "https://" + u
    # watch?v=ID
    m = re.search(r"[?&]v=([A-Za-z0-9_-]{6,})", u)
    if m:
        return m.group(1)
    # youtu.be/ID
    m = re.search(r"youtu\.be/([A-Za-z0-9_-]{6,})", u)
    if m:
        return m.group(1)
    # shorts/ID, embed/ID, /v/ID
    m = re.search(r"/(?:shorts|embed|v)/([A-Za-z0-9_-]{6,})", u)
    if m:
        return m.group(1)
    return None

def normalize_youtube_url(url: str) -> str:
    vid = extract_video_id(url)
    if not vid:
        # best-effort: add scheme and strip timestamp
        u = (url or "").strip()
        if not re.match(r"^https?://", u, re.I):
            u = "https://" + u
        u = u.split("&t=")[0].split("?t=")[0]
        return u
    return f"https://www.youtube.com/watch?v={vid}"



class YoutubeTool:
    def __init__(self, urls: list[str]):
        self.urls = urls
        self.embedding = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.vectorstore = None
        self.retriever = None
        self._prepare_urls()

    def _prepare_urls(self):
        all_docs = []
        for url in self.urls:
            # Load transcript for each URL
            url = normalize_youtube_url(url)
            loader = YoutubeLoader.from_youtube_url(
                url,
                add_video_info=False,
                language=["en", "es"],        # accept English or Spanish transcripts
                translation="en"              # auto-translate to English if needed
            )
            docs_list = loader.load()
            # Add video metadata to each doc
            meta = get_video_info(url)
            for doc in docs_list:
                doc.metadata.update(meta)
            all_docs.extend(docs_list)

        if not all_docs:
            raise ValueError("No transcripts loaded from the provided YouTube URL(s).")

        text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
            chunk_size=400, chunk_overlap=80, separators=["\n\n", "\n", " ", ""]
        )
        doc_splits = text_splitter.split_documents(all_docs)
        if not doc_splits:
            raise ValueError("Failed to split YouTube transcripts into chunks.")

        self.vectorstore = FAISS.from_documents(doc_splits, self.embedding)
        self.retriever = self.vectorstore.as_retriever()

    def get_retriever(self):
        if self.retriever is None:
            self._prepare_urls()
        return self.retriever

# Cache by a hashable key (tuple). Convert back to list inside.
@st.cache_resource
def build_yt_retriever(urls_key: tuple[str, ...]):
    return YoutubeTool(list(urls_key)).get_retriever()