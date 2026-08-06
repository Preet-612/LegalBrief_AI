# import os
# from dotenv import load_dotenv

# from langchain_groq import ChatGroq
# from langchain_core.prompts import ChatPromptTemplate

# load_dotenv()


# class SummaryAgent:

#     def __init__(self):

#         self.llm = ChatGroq(
#             model="llama-3.3-70b-versatile",   
#             groq_api_key=os.getenv("GROQ_API_KEY"),
#             temperature=0.2
#         )

#         self.prompt = ChatPromptTemplate.from_messages(
#             [
#                 (
#                     "system",
#                     """
# You are an expert Legal AI Assistant.

# Your task is to summarize legal documents into simple Hinglish.

# The summary MUST contain these sections:

# 1. Document Type
# 2. Parties Involved
# 3. Purpose
# 4. Effective Date
# 5. Duration / Termination
# 6. Financial Obligations
# 7. Responsibilities of Each Party
# 8. Confidentiality Clauses
# 9. Liability / Indemnity
# 10. Important Deadlines
# 11. Risks Found
# 12. Final Summary

# If any information is unavailable write:
# 'Not Mentioned'

# Keep the summary concise but complete.
# """
#                 ),
#                 (
#                     "human",
#                     """
# Legal Document

# {context}
# """
#                 )
#             ]
#         )

#     def summarize(self, context: str):

#         chain = self.prompt | self.llm

#         response = chain.invoke(
#             {
#                 "context": context
#             }
#         )

#         return response.content


import os
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()


class SummaryAgent:

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

Your task is to summarize legal documents into simple Hinglish.

The summary MUST contain these sections:

1. Document Type
2. Parties Involved
3. Purpose
4. Effective Date
5. Duration / Termination
6. Financial Obligations
7. Responsibilities of Each Party
8. Confidentiality Clauses
9. Liability / Indemnity
10. Important Deadlines
11. Risks Found
12. Final Summary

If any information is unavailable write:
'Not Mentioned'

Keep the summary concise but complete.
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

    def summarize(self, context: str):

        chain = self.prompt | self.llm

        response = chain.invoke(
            {
                "context": context
            }
        )

        return response.content