import os
import fitz  # PyMuPDF
from dotenv import load_dotenv

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
load_dotenv()


class ValidationService:
    def __init__(self):
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="gemini-embedding-001",
            api_key=os.getenv("GEMINI_API_KEY")
        )

        self.reference_store = Chroma(
            embedding_function=self.embeddings,
            collection_name="contract",
            persist_directory="./contract_vector_db",
            collection_metadata={"hnsw:space": "cosine"}
        )

        self.similarity_threshold = float(os.getenv("VALIDATION_SIMILARITY_THRESHOLD", 0.6))

    def extract_text(self, file_path: str) -> str:
        pdf = fitz.open(file_path)

        text = ""
        for page in pdf:
            text += page.get_text()

        pdf.close()

        return text

    def validate_document(self, file_path: str) -> dict:
        try:
            text = self.extract_text(file_path)

            if not text.strip():
                return {"status": "Invalid"}

            splitter = RecursiveCharacterTextSplitter(
                chunk_size=512,
                chunk_overlap=128
            )
            query_chunks = splitter.split_text(text)
            # self.reference_store.add_documents(query_chunks)

            if not query_chunks:
                return {"status": "Invalid"}

            sample_chunks = query_chunks[:5] + query_chunks[len(query_chunks) // 2:len(query_chunks) // 2 + 5]

            best_scores = []

            for chunk in sample_chunks:
                results = self.reference_store.similarity_search_with_relevance_scores(chunk, k=3)

                if not results:
                    continue

                chunk_scores = []
                for result in results:
                    # result is expected to be (Document, score) — take the
                    # score explicitly by index and force it to a plain float.
                    score = result[1]
                    chunk_scores.append(float(score))

                if chunk_scores:
                    best_scores.append(max(chunk_scores))

            if not best_scores:
                return {"status": "Invalid"}

            avg_score = sum(best_scores) / len(best_scores)

            # print("Individual chunk scores:", best_scores)
            # print("Average score:", avg_score)
            # print("Threshold:", self.similarity_threshold)

            if avg_score >= self.similarity_threshold:
                return {"status": "Valid"}

            return {"status": "Invalid"}

        except Exception as e:
            import traceback
            traceback.print_exc()
            return {"status": "Invalid"}

    

if __name__ == "__main__":
    validation_service = ValidationService()
    # validation_service.process_and_create_embeddings()
    # res = validation_service.get_retriever()
    # docs = res.invoke("what is payment plan?")
    # print(docs)
    result = validation_service.validate_document("./Assets/Resume.pdf")
    print(result)

