# """
# LegalBrief - Unified Agent Workflow
# ====================================

# Single entry point that connects:

#     Upload      -> Validate (ValidationService) -> Ingest (RAGService)
#     Query/Chat  -> Retrieve -> Build Context -> Summary / Risk / Chat Agent

# Two LangGraph graphs are built:

# 1. `upload_workflow`  : validate_document -> (ingest_document | halt_for_confirmation)
# 2. `query_workflow`   : retrieve_documents -> prepare_context -> (summary | risk | chat)

# Both graphs share the same `WorkflowState` so state keys are consistent
# across the whole system, but they are compiled separately because they run
# at different times in the product flow (upload time vs. question time).
# """

from typing import TypedDict, List, Optional

from langgraph.graph import StateGraph, END

from App.Services.rag_service import RAGService
from App.Services.validation_service import ValidationService
from App.Agents.Summary_agent import SummaryAgent
from App.Agents.Chat_agent import ChatAgent
from App.Agents.Risk_agent import RiskAgent


# -------------------------
# Initialize services / agents (singletons, reused across requests)
# -------------------------
rag_service = RAGService()
validation_service = ValidationService()
summary_agent = SummaryAgent()
chat_agent = ChatAgent()
risk_agent = RiskAgent()


# -------------------------
# Shared Workflow State
# -------------------------
class WorkflowState(TypedDict, total=False):
    # -------- Query / retrieval related state --------
    query: str
    question: str
    mode: str
    documents: list
    context: str
    summary: str
    chat_response: str
    suggested_questions: List[str]
    risk_analysis: str

    # -------- Upload / validation related state --------
    file_path: str
    user_confirmed: bool
    validation_result: dict
    proceed: bool


# =========================================================
# UPLOAD WORKFLOW: validate -> ingest
# =========================================================

# -------------------------
# Node 0 : Validate Document
# -------------------------
def validate_document(state: WorkflowState):

    validation_result = validation_service.validate_document(state["file_path"])
    print(validation_result)
    return {
        "validation_result": validation_result
    }


# -------------------------
# Router : Valid vs Needs Confirmation
# -------------------------
def route_after_validation(state: WorkflowState):

    validation_result = state.get("validation_result", {})

    if validation_result.get("status") == "Valid":
        return "ingest_document"

    if state.get("user_confirmed"):
        return "ingest_document"

    # Document did not pass the similarity check and the user has not yet
    # confirmed they want to proceed anyway -> stop here and let the
    # frontend ask "This doesn't look like a supported legal document.
    # Continue anyway?"
    return "halt_for_confirmation"


# -------------------------
# Node : Halt (awaiting user confirmation)
# -------------------------
def halt_for_confirmation(state: WorkflowState):

    return {
        "proceed": False
    }


# -------------------------
# Node : Ingest Document (embed + persist into vector DB)
# -------------------------
def ingest_document(state: WorkflowState):

    rag_service.process_and_create_embeddings(state["file_path"])

    return {
        "proceed": True
    }


upload_builder = StateGraph(WorkflowState)

upload_builder.add_node("validate_document", validate_document)
upload_builder.add_node("ingest_document", ingest_document)
upload_builder.add_node("halt_for_confirmation", halt_for_confirmation)

upload_builder.set_entry_point("validate_document")

upload_builder.add_conditional_edges(
    "validate_document",
    route_after_validation,
    {
        "ingest_document": "ingest_document",
        "halt_for_confirmation": "halt_for_confirmation",
    }
)

upload_builder.add_edge("ingest_document", END)
upload_builder.add_edge("halt_for_confirmation", END)

upload_workflow = upload_builder.compile()


# =========================================================
# QUERY WORKFLOW: retrieve -> context -> summary / risk / chat
# =========================================================

# -------------------------
# Node 1 : Retrieve Chunks
# -------------------------
def retrieve_documents(state: WorkflowState):

    retriever = rag_service.get_retriever()

    documents = retriever.invoke(state["query"])

    return {
        "documents": documents
    }


# -------------------------
# Node 2 : Build Context
# -------------------------
def prepare_context(state: WorkflowState):

    context = "\n\n".join(
        document.page_content
        for document in state["documents"]
    )

    return {
        "context": context
    }


# -------------------------
# Node 3 : Generate Summary
# -------------------------
def generate_summary(state: WorkflowState):

    summary = summary_agent.summarize(state["context"])

    return {
        "summary": summary
    }


# -------------------------
# Node : Generate Chat Response (+ suggested follow-ups)
# -------------------------
def generate_chat_response(state: WorkflowState):

    result = chat_agent.chat_with_suggestions(
        state["context"],
        state["question"]
    )

    return {
        "chat_response": result["answer"],
        "suggested_questions": result["suggested_questions"]
    }


# -------------------------
# Node : Generate Risk Analysis
# -------------------------
def generate_risk_analysis(state: WorkflowState):

    risk_analysis = risk_agent.analyze_risk(state["context"])

    return {
        "risk_analysis": risk_analysis
    }


# -------------------------
# Router : Summary vs Chat vs Risk
# -------------------------
def route_after_context(state: WorkflowState):

    if state.get("question"):
        return "generate_chat_response"

    if state.get("mode") == "risk":
        return "generate_risk_analysis"

    return "generate_summary"


query_builder = StateGraph(WorkflowState)

query_builder.add_node("retrieve_documents", retrieve_documents)
query_builder.add_node("prepare_context", prepare_context)
query_builder.add_node("generate_summary", generate_summary)
query_builder.add_node("generate_chat_response", generate_chat_response)
query_builder.add_node("generate_risk_analysis", generate_risk_analysis)

query_builder.set_entry_point("retrieve_documents")

query_builder.add_edge("retrieve_documents", "prepare_context")

query_builder.add_conditional_edges(
    "prepare_context",
    route_after_context,
    {
        "generate_summary": "generate_summary",
        "generate_chat_response": "generate_chat_response",
        "generate_risk_analysis": "generate_risk_analysis",
    }
)

query_builder.add_edge("generate_summary", END)
query_builder.add_edge("generate_chat_response", END)
query_builder.add_edge("generate_risk_analysis", END)

query_workflow = query_builder.compile()


# =========================================================
# PUBLIC ENTRY POINTS
# =========================================================

def validate_and_ingest_document(file_path: str, user_confirmed: bool = False) -> dict:
    """
    Entry point for the upload step.

    Runs ValidationService against the uploaded file. If it passes the
    similarity check (or the user already confirmed they want to proceed
    despite a low match), the document is embedded and persisted into the
    vector DB via RAGService.

    If not, ingestion is skipped and the validation result is returned so
    the frontend can ask "This doesn't look like a supported legal
    document. Continue anyway?".
    """

    result = upload_workflow.invoke(
        {
            "file_path": file_path,
            "user_confirmed": user_confirmed,
        }
    )

    return {
        "proceed": result.get("proceed", False),
        "validation": result.get("validation_result", {})
    }


def summarize_contract(query: str) -> str:

    result = query_workflow.invoke(
        {
            "query": query,
            "question": "",
            "mode": "summary"
        }
    )

    return result["summary"]


def chat_with_contract(question: str) -> dict:
    """
    Returns both the answer and suggested follow-up questions so the
    frontend can render "you might also want to ask..." chips.
    """

    result = query_workflow.invoke(
        {
            "query": question,
            "question": question,
            "mode": "chat"
        }
    )

    return {
        "answer": result["chat_response"],
        "suggested_questions": result.get("suggested_questions", [])
    }


def analyze_contract_risk(query: str) -> str:

    result = query_workflow.invoke(
        {
            "query": query,
            "question": "",
            "mode": "risk"
        }
    )

    return result["risk_analysis"]


def get_initial_questions(query: str = "overview of the contract") -> List[str]:
    """
    Call right after a document is ingested, so the frontend can show a
    handful of quick-start question chips before the user types anything.
    Reuses the same retrieval path as the rest of the query workflow.
    """

    retriever = rag_service.get_retriever()
    documents = retriever.invoke(query)
    context = "\n\n".join(doc.page_content for doc in documents)

    return chat_agent.generate_initial_questions(context)


# -------------------------
# Manual Testing
# -------------------------
if __name__ == "__main__":

    # 1. Upload + validate + ingest
    upload_result = validate_and_ingest_document("./Assets/Agreement.pdf")
    # print(upload_result)

    if upload_result["proceed"]:
        # 2. Quick-start suggestions
        starters = get_initial_questions()
        # print(starters)
        print("Nothing")
        # # 3. Summary
        # print(summarize_contract("Summarize the overall contract."))

        # # 4. Risk analysis
        # print(analyze_contract_risk("Analyze the overall contract risk."))

        # 5. Chat with follow-ups
        chat_result = chat_with_contract("what is agreement")
        print(chat_result["answer"])
        print(chat_result["suggested_questions"])
    else:
        print("Validation did not pass:", upload_result["validation"])
