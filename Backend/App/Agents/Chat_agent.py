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

        # -------- Prompt: Initial Suggested Questions --------
        self.initial_questions_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
You are an expert Legal AI Assistant.

Based on the legal document provided, generate exactly 4 short, useful
starter questions a normal user (non-lawyer) would want to ask about this
document, in simple Hinglish.

Rules:
- Output ONLY the 4 questions.
- One question per line.
- No numbering, no bullets, no extra text, no explanations.
"""
                ),
                (
                    "human",
                    """
Legal Document

{context}
"""
                )
            ]
        )

        # -------- Prompt: Follow-up Suggested Questions --------
        self.followup_questions_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
You are an expert Legal AI Assistant.

Based on the legal document, the user's last question, and the answer given
to them, generate exactly 3 short, relevant follow-up questions the user
might want to ask next, in simple Hinglish.

Rules:
- Output ONLY the 3 questions.
- One question per line.
- No numbering, no bullets, no extra text, no explanations.
- Do not repeat the question the user already asked.
"""
                ),
                (
                    "human",
                    """
Legal Document

{context}

Previous Question

{question}

Previous Answer

{answer}
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

    @staticmethod
    def _parse_questions(raw_text: str, expected_count: int):
        """
        Splits LLM output into a clean list of question strings.
        Falls back gracefully if the model returns fewer/more lines than
        requested, or adds stray numbering/bullets.
        """

        lines = [
            line.strip(" -*\u2022\t")
            for line in raw_text.strip().splitlines()
        ]

        # Strip leading numbering like "1.", "1)", "Q1:" if present
        cleaned = []
        for line in lines:
            if not line:
                continue

            for prefix_len in range(1, 4):
                if len(line) > prefix_len and line[:prefix_len].rstrip(".):").isdigit():
                    line = line[prefix_len:].lstrip(".):- ").strip()
                    break

            if line:
                cleaned.append(line)

        return cleaned[:expected_count] if cleaned else []

    def generate_initial_questions(self, context: str):
        """
        Generates a starter list of suggested questions right after a
        document has been ingested, so the frontend can show quick-start
        chips before the user types anything.
        """

        chain = self.initial_questions_prompt | self.llm

        response = chain.invoke(
            {
                "context": context
            }
        )

        return self._parse_questions(response.content, expected_count=4)

    def chat_with_suggestions(self, context: str, question: str):
        """
        Answers the user's question (via `chat`) and additionally returns a
        short list of relevant follow-up questions, so the frontend can
        surface "you might also want to ask..." chips after every answer.
        """

        answer = self.chat(context, question)

        followup_chain = self.followup_questions_prompt | self.llm

        followup_response = followup_chain.invoke(
            {
                "context": context,
                "question": question,
                "answer": answer
            }
        )

        suggested_questions = self._parse_questions(
            followup_response.content,
            expected_count=3
        )

        return {
            "answer": answer,
            "suggested_questions": suggested_questions
        }