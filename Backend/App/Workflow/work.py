import os
import re
from typing import Optional, TypedDict, List

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
# Full-document text store
# -------------------------
# Summary and risk analysis need the ENTIRE contract, not a handful of
# similarity-retrieved chunks (a vector search over a vague query like
# "summarize the contract" only returns the top-k most similar chunks —
# most of the document, and whatever clause the search didn't rank
# highly, would otherwise never reach SummaryAgent / RiskAgent).
#
# NOTE: this is a simple in-memory, process-local store meant to make
# the behavior correct first. It resets on restart and won't work across
# multiple server instances. For production, replace with a real store
# (DB row, Redis, disk file, etc.) keyed by a document/session id from
# your API layer.
FULL_TEXT_STORE: dict = {}
LAST_INGESTED_FILE_PATH: Optional[str] = None


def extract_full_text(file_path: str) -> str:
    """
    Reads the entire document from disk, independent of the vector
    store, so downstream agents can see 100% of the contract text.
    """
    if file_path.lower().endswith(".pdf"):
        import fitz  # PyMuPDF, pip install pymupdf

        with fitz.open(file_path) as doc:
            return "\n\n".join(page.get_text() for page in doc)

    # Fallback for plain text / already-extracted documents.
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


# -------------------------
# Keyword-based intent classification
# -------------------------
SUMMARY_INTENT_PATTERN = re.compile(
    r"\b(summarize|summary|summarise|overview|tl;?dr|brief me|recap)\b",
    re.IGNORECASE,
)
RISK_INTENT_PATTERN = re.compile(
    r"\b(risk|risky|risks|liability|liabilities|red flag|red flags|"
    r"danger|dangerous|problematic|concern|concerns|concerning|"
    r"exposure|penalt(y|ies))\b",
    re.IGNORECASE,
)

VALID_INTENTS = ("summary", "risk", "chat")


def keyword_classify(question: str):
    """
    Deterministic, zero-cost classification. Returns "summary", "risk",
    or "chat" (default when neither pattern matches — no LLM fallback).
    """
    if SUMMARY_INTENT_PATTERN.search(question):
        return "summary"
    if RISK_INTENT_PATTERN.search(question):
        return "risk"
    return "chat"


# -------------------------
# Shared Workflow State
# -------------------------
class WorkflowState(TypedDict, total=False):
    # -------- Query / retrieval related state --------
    query: str
    question: str
    mode: str
    intent: str
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

    global LAST_INGESTED_FILE_PATH

    rag_service.process_and_create_embeddings(state["file_path"])

    # Also keep the full raw text around, independent of the vector
    # store, so summary/risk can use it later.
    full_text = extract_full_text(state["file_path"])
    FULL_TEXT_STORE[state["file_path"]] = full_text
    LAST_INGESTED_FILE_PATH = state["file_path"]

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
# QUERY WORKFLOW: intent -> (retrieve -> context) OR (full text) -> agent
# =========================================================

# -------------------------
# Node 1 : Determine Intent (runs first — decides how context is built)
# -------------------------
def determine_intent(state: WorkflowState):
    """
    Decides which downstream agent handles this request, and therefore
    which context-building path the graph should take next:

    - "chat"    -> similarity retrieval over the vector store (relevant
                   chunks only — appropriate for a specific question)
    - "summary" -> the full extracted document text
    - "risk"    -> the full extracted document text

    - If a free-text `question` was given (e.g. from chat_with_contract),
      classify it with a fast keyword check.
    - If no `question` was given (e.g. summarize_contract /
      analyze_contract_risk called directly with an explicit `mode`),
      honor that `mode` as before.
    """
    question = state.get("question", "")

    if question:
        intent = keyword_classify(question)
    else:
        intent = state.get("mode", "summary")

    if intent not in VALID_INTENTS:
        intent = "chat"

    return {
        "intent": intent
    }


# -------------------------
# Node : Retrieve Chunks (chat path only)
# -------------------------
def retrieve_documents(state: WorkflowState):

    retriever = rag_service.get_retriever()

    documents = retriever.invoke(state["query"])

    return {
        "documents": documents
    }


# -------------------------
# Node : Build Context from retrieved chunks (chat path only)
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
# Node : Load Full Document Context (summary/risk path only)
# -------------------------
def load_full_context(state: WorkflowState):

    file_path = state.get("file_path") or LAST_INGESTED_FILE_PATH
    context = FULL_TEXT_STORE.get(file_path, "")

    return {
        "context": context
    }


# -------------------------
# Node : Generate Summary
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
# Router : reads the classified intent (used twice — once to pick the
# context-building path, once to pick the final agent after full text
# has been loaded)
# -------------------------
def route_after_intent(state: WorkflowState):
    return state.get("intent", "chat")


query_builder = StateGraph(WorkflowState)

query_builder.add_node("determine_intent", determine_intent)
query_builder.add_node("retrieve_documents", retrieve_documents)
query_builder.add_node("prepare_context", prepare_context)
query_builder.add_node("load_full_context", load_full_context)
query_builder.add_node("generate_summary", generate_summary)
query_builder.add_node("generate_chat_response", generate_chat_response)
query_builder.add_node("generate_risk_analysis", generate_risk_analysis)

query_builder.set_entry_point("determine_intent")

# First branch: does this request need retrieval (chat) or the full
# document (summary/risk)?
query_builder.add_conditional_edges(
    "determine_intent",
    route_after_intent,
    {
        "chat": "retrieve_documents",
        "summary": "load_full_context",
        "risk": "load_full_context",
    }
)

query_builder.add_edge("retrieve_documents", "prepare_context")
query_builder.add_edge("prepare_context", "generate_chat_response")

# Second branch: after loading the full document, pick summary vs risk.
query_builder.add_conditional_edges(
    "load_full_context",
    route_after_intent,
    {
        "summary": "generate_summary",
        "risk": "generate_risk_analysis",
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
    vector DB via RAGService, and its full text is cached for
    summary/risk use.

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


def summarize_contract(query: str, file_path: Optional[str] = None) -> str:
    """
    file_path defaults to the most recently ingested document. Pass it
    explicitly if your app ever handles more than one document at a time.
    """

    result = query_workflow.invoke(
        {
            "query": query,
            "question": "",
            "mode": "summary",
            "file_path": file_path or LAST_INGESTED_FILE_PATH,
        }
    )

    return result["summary"]


def chat_with_contract(question: str, file_path: Optional[str] = None) -> dict:
    """
    Free-text entry point. The workflow itself decides whether this
    question should be answered by ChatAgent (retrieved chunks), or
    should instead trigger SummaryAgent or RiskAgent (full document
    text), based on determine_intent().

    Always returns the same three keys so the caller doesn't need to know
    which agent actually handled the request.
    """

    result = query_workflow.invoke(
        {
            "query": question,
            "question": question,
            "mode": "chat",
            "file_path": file_path or LAST_INGESTED_FILE_PATH,
        }
    )

    return {
        "intent": result.get("intent", "chat"),
        "answer": (
            result.get("chat_response")
            or result.get("summary")
            or result.get("risk_analysis")
        ),
        "suggested_questions": result.get("suggested_questions")
    }


def upload_document(file_path: str, user_confirmed: bool = False) -> str:
    """
    API-friendly wrapper around the existing upload_workflow.

    Reuses validate_and_ingest_document() exactly as implemented (same
    validate_document -> route_after_validation -> ingest_document graph,
    same RAGService embedding + FULL_TEXT_STORE caching, same
    LAST_INGESTED_FILE_PATH bookkeeping). Only difference: instead of
    returning the full {"proceed", "validation"} dict, it collapses the
    result down to a single string so an API layer can return it directly.

    Returns "Valid" if the document passed validation (or was force-
    confirmed) and was ingested. Returns "Invalid" otherwise — the
    document was NOT ingested in that case, so a subsequent ask_question()
    call will still be operating on whatever was ingested before (or
    nothing, if this was the first upload).
    """

    upload_result = validate_and_ingest_document(file_path, user_confirmed=user_confirmed)
    return "Valid" if upload_result["proceed"] else "Invalid"


def ask_question(
    question: str,
    file_path: Optional[str] = None,
    user_confirmed: bool = False,
) -> str:
    """
    Single entry point that runs a free-text question through the
    COMPLETE existing LegalBrief workflow — upload workflow AND query
    workflow — and returns only the final answer text.

    - If `file_path` is given, the document is first run through the
      existing upload_workflow via validate_and_ingest_document() (the
      same function/graph used elsewhere in this file: validate_document
      -> route_after_validation -> ingest_document, which embeds the doc
      via RAGService AND caches its full text in FULL_TEXT_STORE). If
      validation fails and user_confirmed is False, this raises instead
      of silently answering against a stale/no document.
    - If `file_path` is omitted, it falls back to whatever document was
      most recently ingested (LAST_INGESTED_FILE_PATH), same convention
      as summarize_contract() / chat_with_contract() / analyze_contract_risk().

    The question itself is then passed into the existing query_workflow
    graph exactly as chat_with_contract() does (query_workflow.invoke with
    query/question/mode/file_path) — no new workflow, no new state schema.
    determine_intent() still classifies the question and the graph still
    branches into the retrieval path (ChatAgent) or the full-text path
    (SummaryAgent / RiskAgent) exactly as before; this function just
    unwraps the final state down to a single answer string instead of a
    dict.

    Raises RuntimeError if ingestion fails (and wasn't confirmed) or if
    the query workflow completes without producing an answer.
    """

    if file_path:
        upload_result = validate_and_ingest_document(
            file_path, user_confirmed=user_confirmed
        )
        if not upload_result["proceed"]:
            raise RuntimeError(
                "Document failed validation and was not ingested: "
                f"{upload_result['validation']}. Pass user_confirmed=True "
                "to ask_question() to ingest it anyway."
            )
        # ingest_document() already set LAST_INGESTED_FILE_PATH; use the
        # file we were just given so this call targets that document.
        target_file_path = file_path
    else:
        target_file_path = LAST_INGESTED_FILE_PATH

    result = query_workflow.invoke(
        {
            "query": question,
            "question": question,
            "mode": "chat",
            "file_path": target_file_path,
        }
    )

    answer = (
        result.get("chat_response")
        or result.get("summary")
        or result.get("risk_analysis")
    )

    if not answer:
        raise RuntimeError(
            "LegalBrief workflow completed but produced no answer "
            f"(intent classified as '{result.get('intent')}'). Make sure a "
            "document has been ingested (pass file_path= to ask_question(), "
            "or call validate_and_ingest_document() beforehand)."
        )

    return answer


def analyze_contract_risk(query: str, file_path: Optional[str] = None) -> str:
    """
    file_path defaults to the most recently ingested document. Pass it
    explicitly if your app ever handles more than one document at a time.
    """

    result = query_workflow.invoke(
        {
            "query": query,
            "question": "",
            "mode": "risk",
            "file_path": file_path or LAST_INGESTED_FILE_PATH,
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

# import os
# import re
# from typing import Optional, TypedDict, List

# from langgraph.graph import StateGraph, END

# from App.Services.rag_service import RAGService
# from App.Services.validation_service import ValidationService
# from App.Agents.Summary_agent import SummaryAgent
# from App.Agents.Chat_agent import ChatAgent
# from App.Agents.Risk_agent import RiskAgent


# # -------------------------
# # Initialize services / agents (singletons, reused across requests)
# # -------------------------
# rag_service = RAGService()
# validation_service = ValidationService()
# summary_agent = SummaryAgent()
# chat_agent = ChatAgent()
# risk_agent = RiskAgent()


# # -------------------------
# # Full-document text store
# # -------------------------
# # Summary and risk analysis need the ENTIRE contract, not a handful of
# # similarity-retrieved chunks (a vector search over a vague query like
# # "summarize the contract" only returns the top-k most similar chunks —
# # most of the document, and whatever clause the search didn't rank
# # highly, would otherwise never reach SummaryAgent / RiskAgent).
# #
# # NOTE: this is a simple in-memory, process-local store meant to make
# # the behavior correct first. It resets on restart and won't work across
# # multiple server instances. For production, replace with a real store
# # (DB row, Redis, disk file, etc.) keyed by a document/session id from
# # your API layer.
# FULL_TEXT_STORE: dict = {}
# LAST_INGESTED_FILE_PATH: Optional[str] = None


# def extract_full_text(file_path: str) -> str:
#     """
#     Reads the entire document from disk, independent of the vector
#     store, so downstream agents can see 100% of the contract text.
#     """
#     if file_path.lower().endswith(".pdf"):
#         import fitz  # PyMuPDF, pip install pymupdf

#         with fitz.open(file_path) as doc:
#             return "\n\n".join(page.get_text() for page in doc)

#     # Fallback for plain text / already-extracted documents.
#     with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
#         return f.read()


# # -------------------------
# # Keyword-based intent classification
# # -------------------------
# SUMMARY_INTENT_PATTERN = re.compile(
#     r"\b(summarize|summary|summarise|overview|tl;?dr|brief me|recap)\b",
#     re.IGNORECASE,
# )
# RISK_INTENT_PATTERN = re.compile(
#     r"\b(risk|risky|risks|liability|liabilities|red flag|red flags|"
#     r"danger|dangerous|problematic|concern|concerns|concerning|"
#     r"exposure|penalt(y|ies))\b",
#     re.IGNORECASE,
# )

# VALID_INTENTS = ("summary", "risk", "chat")


# def keyword_classify(question: str):
#     """
#     Deterministic, zero-cost classification. Returns "summary", "risk",
#     or "chat" (default when neither pattern matches — no LLM fallback).
#     """
#     if SUMMARY_INTENT_PATTERN.search(question):
#         return "summary"
#     if RISK_INTENT_PATTERN.search(question):
#         return "risk"
#     return "chat"


# # -------------------------
# # Shared Workflow State
# # -------------------------
# class WorkflowState(TypedDict, total=False):
#     # -------- Query / retrieval related state --------
#     query: str
#     question: str
#     mode: str
#     intent: str
#     documents: list
#     context: str
#     summary: str
#     chat_response: str
#     suggested_questions: List[str]
#     risk_analysis: str

#     # -------- Upload / validation related state --------
#     file_path: str
#     user_confirmed: bool
#     validation_result: dict
#     proceed: bool


# # =========================================================
# # UPLOAD WORKFLOW: validate -> ingest
# # =========================================================

# # -------------------------
# # Node 0 : Validate Document
# # -------------------------
# def validate_document(state: WorkflowState):

#     validation_result = validation_service.validate_document(state["file_path"])
#     print(validation_result)
#     return {
#         "validation_result": validation_result
#     }


# # -------------------------
# # Router : Valid vs Needs Confirmation
# # -------------------------
# def route_after_validation(state: WorkflowState):

#     validation_result = state.get("validation_result", {})

#     if validation_result.get("status") == "Valid":
#         return "ingest_document"

#     if state.get("user_confirmed"):
#         return "ingest_document"

#     # Document did not pass the similarity check and the user has not yet
#     # confirmed they want to proceed anyway -> stop here and let the
#     # frontend ask "This doesn't look like a supported legal document.
#     # Continue anyway?"
#     return "halt_for_confirmation"


# # -------------------------
# # Node : Halt (awaiting user confirmation)
# # -------------------------
# def halt_for_confirmation(state: WorkflowState):

#     return {
#         "proceed": False
#     }


# # -------------------------
# # Node : Ingest Document (embed + persist into vector DB)
# # -------------------------
# def ingest_document(state: WorkflowState):

#     global LAST_INGESTED_FILE_PATH

#     rag_service.process_and_create_embeddings(state["file_path"])

#     # Also keep the full raw text around, independent of the vector
#     # store, so summary/risk can use it later.
#     full_text = extract_full_text(state["file_path"])
#     FULL_TEXT_STORE[state["file_path"]] = full_text
#     LAST_INGESTED_FILE_PATH = state["file_path"]

#     return {
#         "proceed": True
#     }


# upload_builder = StateGraph(WorkflowState)

# upload_builder.add_node("validate_document", validate_document)
# upload_builder.add_node("ingest_document", ingest_document)
# upload_builder.add_node("halt_for_confirmation", halt_for_confirmation)

# upload_builder.set_entry_point("validate_document")

# upload_builder.add_conditional_edges(
#     "validate_document",
#     route_after_validation,
#     {
#         "ingest_document": "ingest_document",
#         "halt_for_confirmation": "halt_for_confirmation",
#     }
# )

# upload_builder.add_edge("ingest_document", END)
# upload_builder.add_edge("halt_for_confirmation", END)

# upload_workflow = upload_builder.compile()


# # =========================================================
# # QUERY WORKFLOW: intent -> (retrieve -> context) OR (full text) -> agent
# # =========================================================

# # -------------------------
# # Node 1 : Determine Intent (runs first — decides how context is built)
# # -------------------------
# def determine_intent(state: WorkflowState):
#     """
#     Decides which downstream agent handles this request, and therefore
#     which context-building path the graph should take next:

#     - "chat"    -> similarity retrieval over the vector store (relevant
#                    chunks only — appropriate for a specific question)
#     - "summary" -> the full extracted document text
#     - "risk"    -> the full extracted document text

#     - If a free-text `question` was given (e.g. from chat_with_contract),
#       classify it with a fast keyword check.
#     - If no `question` was given (e.g. summarize_contract /
#       analyze_contract_risk called directly with an explicit `mode`),
#       honor that `mode` as before.
#     """
#     question = state.get("question", "")

#     if question:
#         intent = keyword_classify(question)
#     else:
#         intent = state.get("mode", "summary")

#     if intent not in VALID_INTENTS:
#         intent = "chat"

#     return {
#         "intent": intent
#     }


# # -------------------------
# # Node : Retrieve Chunks (chat path only)
# # -------------------------
# def retrieve_documents(state: WorkflowState):

#     retriever = rag_service.get_retriever()

#     documents = retriever.invoke(state["query"])

#     return {
#         "documents": documents
#     }


# # -------------------------
# # Node : Build Context from retrieved chunks (chat path only)
# # -------------------------
# def prepare_context(state: WorkflowState):

#     context = "\n\n".join(
#         document.page_content
#         for document in state["documents"]
#     )

#     return {
#         "context": context
#     }


# # -------------------------
# # Node : Load Full Document Context (summary/risk path only)
# # -------------------------
# def load_full_context(state: WorkflowState):

#     file_path = state.get("file_path") or LAST_INGESTED_FILE_PATH
#     context = FULL_TEXT_STORE.get(file_path, "")

#     return {
#         "context": context
#     }


# # -------------------------
# # Node : Generate Summary
# # -------------------------
# def generate_summary(state: WorkflowState):

#     summary = summary_agent.summarize(state["context"])

#     return {
#         "summary": summary
#     }


# # -------------------------
# # Node : Generate Chat Response (+ suggested follow-ups)
# # -------------------------
# def generate_chat_response(state: WorkflowState):

#     result = chat_agent.chat_with_suggestions(
#         state["context"],
#         state["question"]
#     )

#     return {
#         "chat_response": result["answer"],
#         "suggested_questions": result["suggested_questions"]
#     }


# # -------------------------
# # Node : Generate Risk Analysis
# # -------------------------
# def generate_risk_analysis(state: WorkflowState):

#     risk_analysis = risk_agent.analyze_risk(state["context"])

#     return {
#         "risk_analysis": risk_analysis
#     }


# # -------------------------
# # Router : reads the classified intent (used twice — once to pick the
# # context-building path, once to pick the final agent after full text
# # has been loaded)
# # -------------------------
# def route_after_intent(state: WorkflowState):
#     return state.get("intent", "chat")


# query_builder = StateGraph(WorkflowState)

# query_builder.add_node("determine_intent", determine_intent)
# query_builder.add_node("retrieve_documents", retrieve_documents)
# query_builder.add_node("prepare_context", prepare_context)
# query_builder.add_node("load_full_context", load_full_context)
# query_builder.add_node("generate_summary", generate_summary)
# query_builder.add_node("generate_chat_response", generate_chat_response)
# query_builder.add_node("generate_risk_analysis", generate_risk_analysis)

# query_builder.set_entry_point("determine_intent")

# # First branch: does this request need retrieval (chat) or the full
# # document (summary/risk)?
# query_builder.add_conditional_edges(
#     "determine_intent",
#     route_after_intent,
#     {
#         "chat": "retrieve_documents",
#         "summary": "load_full_context",
#         "risk": "load_full_context",
#     }
# )

# query_builder.add_edge("retrieve_documents", "prepare_context")
# query_builder.add_edge("prepare_context", "generate_chat_response")

# # Second branch: after loading the full document, pick summary vs risk.
# query_builder.add_conditional_edges(
#     "load_full_context",
#     route_after_intent,
#     {
#         "summary": "generate_summary",
#         "risk": "generate_risk_analysis",
#     }
# )

# query_builder.add_edge("generate_summary", END)
# query_builder.add_edge("generate_chat_response", END)
# query_builder.add_edge("generate_risk_analysis", END)

# query_workflow = query_builder.compile()


# # =========================================================
# # PUBLIC ENTRY POINTS
# # =========================================================

# def validate_and_ingest_document(file_path: str, user_confirmed: bool = False) -> dict:
#     """
#     Entry point for the upload step.

#     Runs ValidationService against the uploaded file. If it passes the
#     similarity check (or the user already confirmed they want to proceed
#     despite a low match), the document is embedded and persisted into the
#     vector DB via RAGService, and its full text is cached for
#     summary/risk use.

#     If not, ingestion is skipped and the validation result is returned so
#     the frontend can ask "This doesn't look like a supported legal
#     document. Continue anyway?".
#     """

#     result = upload_workflow.invoke(
#         {
#             "file_path": file_path,
#             "user_confirmed": user_confirmed,
#         }
#     )

#     return {
#         "proceed": result.get("proceed", False),
#         "validation": result.get("validation_result", {})
#     }


# def summarize_contract(query: str, file_path: Optional[str] = None) -> str:
#     """
#     file_path defaults to the most recently ingested document. Pass it
#     explicitly if your app ever handles more than one document at a time.
#     """

#     result = query_workflow.invoke(
#         {
#             "query": query,
#             "question": "",
#             "mode": "summary",
#             "file_path": file_path or LAST_INGESTED_FILE_PATH,
#         }
#     )

#     return result["summary"]


# def chat_with_contract(question: str, file_path: Optional[str] = None) -> dict:
#     """
#     Free-text entry point. The workflow itself decides whether this
#     question should be answered by ChatAgent (retrieved chunks), or
#     should instead trigger SummaryAgent or RiskAgent (full document
#     text), based on determine_intent().

#     Always returns the same three keys so the caller doesn't need to know
#     which agent actually handled the request.
#     """

#     result = query_workflow.invoke(
#         {
#             "query": question,
#             "question": question,
#             "mode": "chat",
#             "file_path": file_path or LAST_INGESTED_FILE_PATH,
#         }
#     )

#     return {
#         "intent": result.get("intent", "chat"),
#         "answer": (
#             result.get("chat_response")
#             or result.get("summary")
#             or result.get("risk_analysis")
#         ),
#         "suggested_questions": result.get("suggested_questions", [])
#     }


# def analyze_contract_risk(query: str, file_path: Optional[str] = None) -> str:
#     """
#     file_path defaults to the most recently ingested document. Pass it
#     explicitly if your app ever handles more than one document at a time.
#     """

#     result = query_workflow.invoke(
#         {
#             "query": query,
#             "question": "",
#             "mode": "risk",
#             "file_path": file_path or LAST_INGESTED_FILE_PATH,
#         }
#     )

#     return result["risk_analysis"]


# def get_initial_questions(query: str = "overview of the contract") -> List[str]:
#     """
#     Call right after a document is ingested, so the frontend can show a
#     handful of quick-start question chips before the user types anything.
#     Reuses the same retrieval path as the rest of the query workflow.
#     """

#     retriever = rag_service.get_retriever()
#     documents = retriever.invoke(query)
#     context = "\n\n".join(doc.page_content for doc in documents)

#     return chat_agent.generate_initial_questions(context)

# def ask_question(question: str) -> str:
    
 
#     result = query_workflow.invoke(
#         {
#             "query": question,
#             "question": question,
#             "mode": "chat",
#             "file_path": "./Assets/Agreement.pdf"
#         }
#     )
 
#     answer = (
#         result.get("chat_response")
#         or result.get("summary")
#         or result.get("risk_analysis")
#     )
 
    
 
#     return answer


# # -------------------------
# # Manual Testing
# # -------------------------
# if __name__ == "__main__":

#     # 1. Upload + validate + ingest
#     upload_result = ask_question("Summarize the risk")
#     print(upload_result)


# from typing import TypedDict, List

# from langgraph.graph import StateGraph, END

# from App.Services.rag_service import RAGService
# from App.Services.validation_service import ValidationService
# from App.Agents.Summary_agent import SummaryAgent
# from App.Agents.Chat_agent import ChatAgent
# from App.Agents.Risk_agent import RiskAgent


# # -------------------------
# # Initialize services / agents (singletons, reused across requests)
# # -------------------------
# rag_service = RAGService()
# validation_service = ValidationService()
# summary_agent = SummaryAgent()
# chat_agent = ChatAgent()
# risk_agent = RiskAgent()


# # -------------------------
# # Shared Workflow State
# # -------------------------
# class WorkflowState(TypedDict, total=False):
#     # -------- Query / retrieval related state --------
#     query: str
#     question: str
#     mode: str
#     documents: list
#     context: str
#     summary: str
#     chat_response: str
#     suggested_questions: List[str]
#     risk_analysis: str

#     # -------- Upload / validation related state --------
#     file_path: str
#     user_confirmed: bool
#     validation_result: dict
#     proceed: bool


# # =========================================================
# # UPLOAD WORKFLOW: validate -> ingest
# # =========================================================

# # -------------------------
# # Node 0 : Validate Document
# # -------------------------
# def validate_document(state: WorkflowState):

#     validation_result = validation_service.validate_document(state["file_path"])
#     print(validation_result)
#     return {
#         "validation_result": validation_result
#     }


# # -------------------------
# # Router : Valid vs Needs Confirmation
# # -------------------------
# def route_after_validation(state: WorkflowState):

#     validation_result = state.get("validation_result", {})

#     if validation_result.get("status") == "Valid":
#         return "ingest_document"

#     if state.get("user_confirmed"):
#         return "ingest_document"

#     # Document did not pass the similarity check and the user has not yet
#     # confirmed they want to proceed anyway -> stop here and let the
#     # frontend ask "This doesn't look like a supported legal document.
#     # Continue anyway?"
#     return "halt_for_confirmation"


# # -------------------------
# # Node : Halt (awaiting user confirmation)
# # -------------------------
# def halt_for_confirmation(state: WorkflowState):

#     return {
#         "proceed": False
#     }


# # -------------------------
# # Node : Ingest Document (embed + persist into vector DB)
# # -------------------------
# def ingest_document(state: WorkflowState):

#     rag_service.process_and_create_embeddings(state["file_path"])

#     return {
#         "proceed": True
#     }


# upload_builder = StateGraph(WorkflowState)

# upload_builder.add_node("validate_document", validate_document)
# upload_builder.add_node("ingest_document", ingest_document)
# upload_builder.add_node("halt_for_confirmation", halt_for_confirmation)

# upload_builder.set_entry_point("validate_document")

# upload_builder.add_conditional_edges(
#     "validate_document",
#     route_after_validation,
#     {
#         "ingest_document": "ingest_document",
#         "halt_for_confirmation": "halt_for_confirmation",
#     }
# )

# upload_builder.add_edge("ingest_document", END)
# upload_builder.add_edge("halt_for_confirmation", END)

# upload_workflow = upload_builder.compile()


# # =========================================================
# # QUERY WORKFLOW: retrieve -> context -> summary / risk / chat
# # =========================================================

# # -------------------------
# # Node 1 : Retrieve Chunks
# # -------------------------
# def retrieve_documents(state: WorkflowState):

#     retriever = rag_service.get_retriever()

#     documents = retriever.invoke(state["query"])

#     return {
#         "documents": documents
#     }


# # -------------------------
# # Node 2 : Build Context
# # -------------------------
# def prepare_context(state: WorkflowState):

#     context = "\n\n".join(
#         document.page_content
#         for document in state["documents"]
#     )

#     return {
#         "context": context
#     }


# # -------------------------
# # Node 3 : Generate Summary
# # -------------------------
# def generate_summary(state: WorkflowState):

#     summary = summary_agent.summarize(state["context"])

#     return {
#         "summary": summary
#     }


# # -------------------------
# # Node : Generate Chat Response (+ suggested follow-ups)
# # -------------------------
# def generate_chat_response(state: WorkflowState):

#     result = chat_agent.chat_with_suggestions(
#         state["context"],
#         state["question"]
#     )

#     return {
#         "chat_response": result["answer"],
#         "suggested_questions": result["suggested_questions"]
#     }


# # -------------------------
# # Node : Generate Risk Analysis
# # -------------------------
# def generate_risk_analysis(state: WorkflowState):

#     risk_analysis = risk_agent.analyze_risk(state["context"])

#     return {
#         "risk_analysis": risk_analysis
#     }


# # -------------------------
# # Router : Summary vs Chat vs Risk
# # -------------------------
# def route_after_context(state: WorkflowState):

#     if state.get("question"):
#         return "generate_chat_response"

#     if state.get("mode") == "risk":
#         return "generate_risk_analysis"

#     return "generate_summary"


# query_builder = StateGraph(WorkflowState)

# query_builder.add_node("retrieve_documents", retrieve_documents)
# query_builder.add_node("prepare_context", prepare_context)
# query_builder.add_node("generate_summary", generate_summary)
# query_builder.add_node("generate_chat_response", generate_chat_response)
# query_builder.add_node("generate_risk_analysis", generate_risk_analysis)

# query_builder.set_entry_point("retrieve_documents")

# query_builder.add_edge("retrieve_documents", "prepare_context")

# query_builder.add_conditional_edges(
#     "prepare_context",
#     route_after_context,
#     {
#         "generate_summary": "generate_summary",
#         "generate_chat_response": "generate_chat_response",
#         "generate_risk_analysis": "generate_risk_analysis",
#     }
# )

# query_builder.add_edge("generate_summary", END)
# query_builder.add_edge("generate_chat_response", END)
# query_builder.add_edge("generate_risk_analysis", END)

# query_workflow = query_builder.compile()


# # =========================================================
# # PUBLIC ENTRY POINTS
# # =========================================================

# def validate_and_ingest_document(file_path: str, user_confirmed: bool = False) -> dict:
#     """
#     Entry point for the upload step.

#     Runs ValidationService against the uploaded file. If it passes the
#     similarity check (or the user already confirmed they want to proceed
#     despite a low match), the document is embedded and persisted into the
#     vector DB via RAGService.

#     If not, ingestion is skipped and the validation result is returned so
#     the frontend can ask "This doesn't look like a supported legal
#     document. Continue anyway?".
#     """

#     result = upload_workflow.invoke(
#         {
#             "file_path": file_path,
#             "user_confirmed": user_confirmed,
#         }
#     )

#     return {
#         "proceed": result.get("proceed", False),
#         "validation": result.get("validation_result", {})
#     }


# def summarize_contract(query: str) -> str:

#     result = query_workflow.invoke(
#         {
#             "query": query,
#             "question": "",
#             "mode": "summary"
#         }
#     )

#     return result["summary"]


# def chat_with_contract(question: str) -> dict:
#     """
#     Returns both the answer and suggested follow-up questions so the
#     frontend can render "you might also want to ask..." chips.
#     """

#     result = query_workflow.invoke(
#         {
#             "query": question,
#             "question": question,
#             "mode": "chat"
#         }
#     )

#     return {
#         "answer": result["chat_response"],
#         "suggested_questions": result.get("suggested_questions", [])
#     }


# def analyze_contract_risk(query: str) -> str:

#     result = query_workflow.invoke(
#         {
#             "query": query,
#             "question": "",
#             "mode": "risk"
#         }
#     )

#     return result["risk_analysis"]


# def get_initial_questions(query: str = "overview of the contract") -> List[str]:
#     """
#     Call right after a document is ingested, so the frontend can show a
#     handful of quick-start question chips before the user types anything.
#     Reuses the same retrieval path as the rest of the query workflow.
#     """

#     retriever = rag_service.get_retriever()
#     documents = retriever.invoke(query)
#     context = "\n\n".join(doc.page_content for doc in documents)

#     return chat_agent.generate_initial_questions(context)


# # -------------------------
# # Manual Testing
# # -------------------------
# if __name__ == "__main__":

#     # 1. Upload + validate + ingest
#     upload_result = validate_and_ingest_document("./Assets/Agreement.pdf")
#     # print(upload_result)
#     if upload_result["proceed"]:
#         for i in range(5):
#             query = input("Chat with me")
#             chat_result = chat_with_contract(query)
#             print(chat_result["answer"])
#             print(chat_result["suggested_questions"])
#         # 2. Quick-start suggestions
#         # starters = get_initial_questions()
#         # print(starters)
#         # # 3. Summary
#         # print(summarize_contract("Summarize the overall contract."))

#         # # 4. Risk analysis
#         # print(analyze_contract_risk("Analyze the overall contract risk."))

#         # 5. Chat with follow-ups
#     else:
#         print("Validation did not pass:", upload_result["validation"])
