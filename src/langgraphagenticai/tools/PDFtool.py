
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
# from langchain.document_loaders import PyPDFLoader
from langchain.schema import Document
# from langchain.document_loaders import UnstructuredPDFLoader
from langchain_community.document_loaders import UnstructuredPDFLoader

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
        loader = UnstructuredPDFLoader(self.pdf_path)
        docs_list = loader.load()
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
            chunk_size=700,     # recommended default
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
