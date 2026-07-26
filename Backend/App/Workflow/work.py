
from typing import TypedDict

from langgraph.graph import StateGraph, END

from App.Services.rag_service import RAGService
from App.Agents.Summary_agent import SummaryAgent


# Initialize services
rag_service = RAGService()
summary_agent = SummaryAgent()


class SummaryState(TypedDict):
    query: str
    documents: list
    context: str
    summary: str


# -------------------------
# Node 1 : Retrieve Chunks
# -------------------------
def retrieve_documents(state: SummaryState):

    retriever = rag_service.get_retriever()

    documents = retriever.invoke(state["query"])

    return {
        "documents": documents
    }


# -------------------------
# Node 2 : Build Context
# -------------------------
def prepare_context(state: SummaryState):

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
def generate_summary(state: SummaryState):

    summary = summary_agent.summarize(
        state["context"]
    )

    return {
        "summary": summary
    }


# -------------------------
# Build LangGraph
# -------------------------
builder = StateGraph(SummaryState)

builder.add_node(
    "retrieve_documents",
    retrieve_documents
)

builder.add_node(
    "prepare_context",
    prepare_context
)

builder.add_node(
    "generate_summary",
    generate_summary)


builder.set_entry_point(
    "retrieve_documents"
)

builder.add_edge(
    "retrieve_documents",
    "prepare_context"
)

builder.add_edge(
    "prepare_context",
    "generate_summary"
)

builder.add_edge(
    "generate_summary",
    END
)

summary_workflow = builder.compile()


# -------------------------
# Public Function
# -------------------------
def summarize_contract(query: str):

    result = summary_workflow.invoke(
        {
            "query": query
        }
    )

    return result["summary"]


# -------------------------
# Testing
# -------------------------
if __name__ == "__main__":

    summary = summarize_contract(
        "Summarize the payment legal contract."
    )

    print(summary)