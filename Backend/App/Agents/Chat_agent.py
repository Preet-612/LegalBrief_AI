import os
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()


class ChatAgent:

    def __init__(self):

        self.llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            groq_api_key=os.getenv("GROQ_API_KEY"),
            temperature=0.2
        )

        self.prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
You are an expert Legal AI Assistant.

Your task is to answer the user's question strictly based on the provided legal document context, in simple Hinglish.



Keep the answer concise and accurate.
"""
                ),
                (
                    "human",
                    """
Legal Document

{context}

Question

{question}
"""
                )
            ]
        )

    def chat(self, context: str, question: str):

        chain = self.prompt | self.llm

        response = chain.invoke(
            {
                "context": context,
                "question": question
            }
        )

        return response.content