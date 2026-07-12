import os
import fitz  # PyMuPDF
from dotenv import load_dotenv

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma

load_dotenv()  


class RAGService:
    def __init__(self):
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="gemini-embedding-001",
            api_key=os.getenv("GEMINI_API_KEY")
        )

        self.vector_store = Chroma(
            embedding_function=self.embeddings,
            collection_name="contract",
            persist_directory="./contract_vector_db"
        )

    def process_and_create_embeddings(self,file_path: str = "./Assets/sample_contract.pdf") -> None:
        # Open PDF using PyMuPDF
        pdf = fitz.open(file_path)

        documents = []

        # Convert each page into a LangChain Document
        for page_num, page in enumerate(pdf):
            text = page.get_text()

            documents.append(Document(page_content=text,metadata={"page": page_num + 1,"source": file_path}))

        pdf.close()

        # Split into chunks
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=512,
            chunk_overlap=128
        )

        chunks = splitter.split_documents(documents)

        # Store embeddings
        self.vector_store.add_documents(chunks)

    def get_retriever(self):
        retriever = self.vector_store.as_retriever(
            search_kwargs={"k": 5}
        )

        return retriever


if __name__ == "__main__":
    rag_service = RAGService()

    # Uncomment only once to create the vector database
    rag_service.process_and_create_embeddings()
    # print("-------------- VECTOR DB IS READY --------------")

    retriever = rag_service.get_retriever()

    docs = retriever.invoke(
        "What are Payment in this contract ?"
    )

    for doc in docs:
        print("=" * 60)
        print(f"Page: {doc.metadata['page']}")
        print(doc.page_content)