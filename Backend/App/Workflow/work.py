from typing import TypedDict

from langgraph.graph import StateGraph, END

from App.Services.rag_service import RAGService
from App.Agents.Summary_agent import SummaryAgent
from App.Agents.Chat_agent import ChatAgent


# Initialize services
rag_service = RAGService()
summary_agent = SummaryAgent()
chat_agent = ChatAgent()


class WorkflowState(TypedDict):
    query: str
    question: str
    documents: list
    context: str
    summary: str
    chat_response: str


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

    summary = summary_agent.summarize(
        state["context"]
    )

    return {
        "summary": summary
    }


# -------------------------
# Node : Generate Chat Response
# -------------------------
def generate_chat_response(state: WorkflowState):

    chat_response = chat_agent.chat(
        state["context"],
        state["question"]
    )

    return {
        "chat_response": chat_response
    }


# -------------------------
# Router : Summary vs Chat
# -------------------------
def route_after_context(state: WorkflowState):

    if state.get("question"):
        return "generate_chat_response"

    return "generate_summary"


# -------------------------
# Build LangGraph
# -------------------------
builder = StateGraph(WorkflowState)

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
    generate_summary
)

builder.add_node(
    "generate_chat_response",
    generate_chat_response
)


builder.set_entry_point(
    "retrieve_documents"
)

builder.add_edge(
    "retrieve_documents",
    "prepare_context"
)

builder.add_conditional_edges(
    "prepare_context",
    route_after_context,
    {
        "generate_summary": "generate_summary",
        "generate_chat_response": "generate_chat_response",
    }
)

builder.add_edge(
    "generate_summary",
    END
)

builder.add_edge(
    "generate_chat_response",
    END
)

workflow = builder.compile()


# -------------------------
# Public Function
# -------------------------
def summarize_contract(query: str):

    result = workflow.invoke(
        {
            "query": query,
            "question": ""
        }
    )

    return result["summary"]


# -------------------------
# Public Function
# -------------------------
def chat_with_contract(question: str):

    result = workflow.invoke(
        {
            "query": question,
            "question": question
        }
    )

    return result["chat_response"]


# -------------------------
# Testing
# -------------------------
if __name__ == "__main__":

    summary = summarize_contract(
        "Summarize the payment legal contract only ."
    )

    print(summary)

    chat_response = chat_with_contract(
        "What if I did not pay on time?"
    )

    print(chat_response)

# from typing import TypedDict

# from langgraph.graph import StateGraph, END

# from App.Services.rag_service import RAGService
# from App.Agents.Summary_agent import SummaryAgent
# from App.Agents.Chat_agent import ChatAgent


# # Initialize services
# rag_service = RAGService()
# summary_agent = SummaryAgent()
# chat_agent = ChatAgent()


# class SummaryState(TypedDict):
#     query: str
#     documents: list
#     context: str
#     summary: str


# class ChatState(TypedDict):
#     query: str
#     question: str
#     documents: list
#     context: str
#     chat_response: str


# # -------------------------
# # Node 1 : Retrieve Chunks
# # -------------------------
# def retrieve_documents(state: SummaryState):

#     retriever = rag_service.get_retriever()

#     documents = retriever.invoke(state["query"])

#     return {
#         "documents": documents
#     }


# # -------------------------
# # Node 2 : Build Context
# # -------------------------
# def prepare_context(state: SummaryState):

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
# def generate_summary(state: SummaryState):

#     summary = summary_agent.summarize(
#         state["context"]
#     )

#     return {
#         "summary": summary
#     }


# # -------------------------
# # Node : Generate Chat Response
# # -------------------------
# def generate_chat_response(state: ChatState):

#     chat_response = chat_agent.chat(
#         state["context"],
#         state["question"]
#     )

#     return {
#         "chat_response": chat_response
#     }


# # -------------------------
# # Build LangGraph
# # -------------------------
# builder = StateGraph(SummaryState)

# builder.add_node(
#     "retrieve_documents",
#     retrieve_documents
# )

# builder.add_node(
#     "prepare_context",
#     prepare_context
# )

# builder.add_node(
#     "generate_summary",
#     generate_summary)


# builder.set_entry_point(
#     "retrieve_documents"
# )

# builder.add_edge(
#     "retrieve_documents",
#     "prepare_context"
# )

# builder.add_edge(
#     "prepare_context",
#     "generate_summary"
# )

# builder.add_edge(
#     "generate_summary",
#     END
# )

# summary_workflow = builder.compile()


# # -------------------------
# # Build Chat LangGraph
# # -------------------------
# chat_builder = StateGraph(ChatState)

# chat_builder.add_node(
#     "retrieve_documents",
#     retrieve_documents
# )

# chat_builder.add_node(
#     "prepare_context",
#     prepare_context
# )

# chat_builder.add_node(
#     "generate_chat_response",
#     generate_chat_response
# )

# chat_builder.set_entry_point(
#     "retrieve_documents"
# )

# chat_builder.add_edge(
#     "retrieve_documents",
#     "prepare_context"
# )

# chat_builder.add_edge(
#     "prepare_context",
#     "generate_chat_response"
# )

# chat_builder.add_edge(
#     "generate_chat_response",
#     END
# )

# chat_workflow = chat_builder.compile()


# # -------------------------
# # Public Function
# # -------------------------
# def summarize_contract(query: str):

#     result = summary_workflow.invoke(
#         {
#             "query": query
#         }
#     )

#     return result["summary"]


# # -------------------------
# # Public Function
# # -------------------------
# def chat_with_contract(query: str, question: str):

#     result = chat_workflow.invoke(
#         {
#             "query": query,
#             "question": question
#         }
#     )

#     return result["chat_response"]


# # -------------------------
# # Testing
# # -------------------------
# if __name__ == "__main__":

#     # summary = chat_with_contract(
#     #     "Summarize the payment legal contract only ."
#     # )
#     chat_response = chat_with_contract(
#         "Summarize the overall contract only .",
#         "Tell me something about yourself?"
#     )

#     print(chat_response)
    # print(summary)



# from typing import TypedDict

# from langgraph.graph import StateGraph, END

# from App.Services.rag_service import RAGService
# from App.Agents.Summary_agent import SummaryAgent


# # Initialize services
# rag_service = RAGService()
# summary_agent = SummaryAgent()


# class SummaryState(TypedDict):
#     query: str
#     documents: list
#     context: str
#     summary: str


# # -------------------------
# # Node 1 : Retrieve Chunks
# # -------------------------
# def retrieve_documents(state: SummaryState):

#     retriever = rag_service.get_retriever()

#     documents = retriever.invoke(state["query"])

#     return {
#         "documents": documents
#     }


# # -------------------------
# # Node 2 : Build Context
# # -------------------------
# def prepare_context(state: SummaryState):

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
# def generate_summary(state: SummaryState):

#     summary = summary_agent.summarize(
#         state["context"]
#     )

#     return {
#         "summary": summary
#     }


# # -------------------------
# # Build LangGraph
# # -------------------------
# builder = StateGraph(SummaryState)

# builder.add_node(
#     "retrieve_documents",
#     retrieve_documents
# )

# builder.add_node(
#     "prepare_context",
#     prepare_context
# )

# builder.add_node(
#     "generate_summary",
#     generate_summary)


# builder.set_entry_point(
#     "retrieve_documents"
# )

# builder.add_edge(
#     "retrieve_documents",
#     "prepare_context"
# )

# builder.add_edge(
#     "prepare_context",
#     "generate_summary"
# )

# builder.add_edge(
#     "generate_summary",
#     END
# )

# summary_workflow = builder.compile()


# # -------------------------
# # Public Function
# # -------------------------
# def summarize_contract(query: str):

#     result = summary_workflow.invoke(
#         {
#             "query": query
#         }
#     )

#     return result["summary"]


# # -------------------------
# # Testing
# # -------------------------
# if __name__ == "__main__":

#     summary = summarize_contract(
#         "Summarize the payment legal contract only ."
#     )

#     print(summary)