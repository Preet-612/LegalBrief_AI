import os
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()


class RiskAgent:

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
You are an expert Legal Risk Analysis AI Assistant.

Your task is to analyze a legal document section by section and identify
every legal risk present in it, in simple Hinglish so both legal
professionals and normal users can understand it.

Analyze risks such as (but not limited to):

- Legal Liability
- Financial Risk
- Confidentiality Risk
- Data Privacy Risk
- Compliance Issues
- Intellectual Property Issues
- Payment Risk
- Termination Clauses
- Indemnity Clauses
- Unlimited Liability
- Arbitration Issues
- Governing Law Issues
- Employment Risks
- Vendor Risks
- Consumer Protection Risks
- Missing Important Clauses
- One-sided Obligations
- Ambiguous Language
- Hidden Conditions
- Excessive Penalties
- Force Majeure Issues
- Renewal Risks
- Warranty Limitations

New risk categories can appear beyond this list if the document contains them.

For EVERY risk found, output the following fields:

1. Section / Clause Name
2. Risk Category
3. Severity (Low / Medium / High / Critical)
4. Risk Explanation
5. Why it Matters
6. Possible Impact
7. Recommendation
8. Suggested Action

After listing all individual risks, output a final block called
'Overall Risk Assessment' containing:

1. Executive Summary
2. Total Risks Found
3. Number of Critical Risks
4. Number of High Risks
5. Number of Medium Risks
6. Number of Low Risks
7. Overall Risk Score (0-10)
8. Overall Recommendation (Safe to Sign / Review Before Signing /
   Legal Consultation Recommended)

If any information is unavailable write:
'Not Mentioned'

Keep explanations simple, clear and concise, but do not skip any risk.
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

    def analyze_risk(self, context: str):

        chain = self.prompt | self.llm

        response = chain.invoke(
            {
                "context": context
            }
        )

        return response.content

