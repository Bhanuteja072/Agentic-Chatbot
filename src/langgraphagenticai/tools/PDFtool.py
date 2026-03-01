import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
# from langchain.document_loaders import PyPDFLoader
from langchain_core.documents import Document
# from langchain.document_loaders import UnstructuredPDFLoader
from langchain_community.document_loaders import UnstructuredPDFLoader
import streamlit as st

class PDFTool:
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.embedding = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.vectorstore = None
        self.retriever = None
        self._prepare_pdf()

    # def _prepare_pdf(self):
    #     loader = PyPDFLoader(self.pdf_path)
    #     docs_list = loader.load()
    #     text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
    #         chunk_size=500, chunk_overlap=50
    #     )
    #     doc_splits = text_splitter.split_documents(docs_list)
    #     self.vectorstore = FAISS.from_documents(doc_splits, self.embedding)
    #     self.retriever = self.vectorstore.as_retriever()
    
    def _prepare_pdf(self):
        os.environ.setdefault("OCR_AGENT", "tesseract")
        loader = UnstructuredPDFLoader(self.pdf_path)
        try:
            docs_list = loader.load()
        except IndexError:
            raise ValueError(
                "Unstructured failed to OCR this PDF (image-only, unreadable scan). "
                "Please upload an OCR-processed or higher-quality PDF."
            )
        if not docs_list:
            raise ValueError(
                "OCR produced no text. Please upload a higher-quality or OCR-processed PDF."
            )
        def clean_page_text(txt: str) -> str:
            # tweak to remove repeated page headers/footers, common line patterns, or "Page X of Y"
            import re
            txt = re.sub(r"Page\s*\d+\s*(of\s*\d+)?", "", txt, flags=re.IGNORECASE)
            txt = re.sub(r"^\s*-+\s*$", "", txt, flags=re.MULTILINE)
            return txt.strip()
        for d in docs_list:
            d.page_content = clean_page_text(d.page_content)
        full_text = "\n\n".join(d.page_content for d in docs_list)
        merged = Document(page_content=full_text, metadata={"source": self.pdf_path, "total_pages": len(docs_list)})
        text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
            chunk_size=500,     # recommended default
            chunk_overlap=100,  # recommended default
            separators=["\n\n", "\n", " ", ""]
        )
        doc_splits = text_splitter.split_documents(docs_list)
        self.vectorstore = FAISS.from_documents(doc_splits, self.embedding)
        self.retriever = self.vectorstore.as_retriever()
    def get_retriever(self):
        if self.retriever is None:
            self._prepare_pdf()
        return self.retriever
# ...existing code...
@st.cache_resource
def build_pdf_retriever(pdf_path: str):
    return PDFTool(pdf_path).get_retriever()