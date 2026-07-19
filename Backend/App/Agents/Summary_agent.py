# # """
# # LegalBrief Agent — core building blocks only.

# # This file intentionally does NOT build or compile a LangGraph StateGraph.
# # It gives you:
# #     1. `get_legal_context` — a tool wrapping your existing RAGService.
# #     2. `LegalBriefAgent`   — a class holding the LLM + tools, with two
# #                              plain methods (`agent_node`, `tool_node`) that
# #                              you can plug into your own StateGraph nodes
# #                              exactly as-is (they already match LangGraph's
# #                              expected node signature: state dict in, dict out).

# # Wire them into your graph however you like, e.g.:

# #     from App.agents.legalbrief_agent import LegalBriefAgent

# #     agent = LegalBriefAgent()
# #     graph.add_node("agent", agent.agent_node)
# #     graph.add_node("tools", agent.tool_node)
# # """

# # import logging
# # import os

# # from dotenv import load_dotenv
# # from langchain_core.messages import SystemMessage, ToolMessage
# # from langchain_core.tools import tool
# # from langchain_google_genai import ChatGoogleGenerativeAI

# # from App.Services.rag_service import RAGService

# # load_dotenv()
# # logger = logging.getLogger(__name__)

# # NO_CONTEXT_MARKER = "NO_RELEVANT_CONTEXT"
# # RETRIEVAL_ERROR_MARKER = "RETRIEVAL_ERROR"


# # # --------------------------------------------------------------------------
# # # Tool: wraps your existing RAGService. No retrieval/chunking logic lives
# # # here — just calling your retriever and formatting the result.
# # # --------------------------------------------------------------------------
# # @tool
# # def get_legal_context(query: str) -> str:
# #     """
# #     Retrieve relevant excerpts from the uploaded legal document to help answer
# #     a user's question.

# #     Use this tool whenever you need factual grounding from the legal document
# #     before answering — for example questions about payment terms, obligations,
# #     termination clauses, liability, definitions, dates, or parties involved.

# #     Arguments:
# #     query -> A specific, self-contained question or topic to search for in the
# #              legal document (e.g. "What are the payment terms?",
# #              "What is the termination notice period?").
# #     """
# #     try:
# #         rag_service = RAGService()
# #         retriever = rag_service.get_retriever()
# #         docs = retriever.invoke(query)
# #     except Exception:
# #         logger.exception("Retrieval failed for query: %s", query)
# #         return (
# #             f"{RETRIEVAL_ERROR_MARKER}: The document search system is "
# #             "currently unavailable. Do not fabricate an answer; tell the "
# #             "user the document could not be searched right now."
# #         )

# #     if not docs:
# #         return (
# #             f"{NO_CONTEXT_MARKER}: No relevant excerpts were found in the "
# #             "document for this query. Tell the user the document does not "
# #             "appear to contain information on this topic."
# #         )

# #     formatted_chunks = []
# #     for i, doc in enumerate(docs, start=1):
# #         page = doc.metadata.get("page", "unknown")
# #         source = doc.metadata.get("source", "unknown")
# #         formatted_chunks.append(
# #             f"[Excerpt {i} | Page {page} | Source: {source}]\n"
# #             f"{doc.page_content.strip()}"
# #         )

# #     return "\n\n---\n\n".join(formatted_chunks)


# # SYSTEM_PROMPT = """You are LegalBrief Agent, a professional legal-document assistant.

# # Your strict operating rules:
# # 1. Before answering any substantive question about the document, use the
# #    `get_legal_context` tool to retrieve relevant excerpts. Do not answer from
# #    general knowledge or assumption when a document-specific fact is being asked.
# # 2. Base your answer ONLY on the retrieved excerpts. Do not invent clauses,
# #    dates, amounts, or obligations that are not present in the retrieved text.
# # 3. If the tool result contains "NO_RELEVANT_CONTEXT" or "RETRIEVAL_ERROR",
# #    clearly and plainly tell the user that the document does not appear to
# #    contain enough information to answer (or that the search is temporarily
# #    unavailable). Do not guess to fill the gap.
# # 4. When you do have relevant excerpts, write a concise, well-structured
# #    answer in plain, professional language a non-lawyer can understand.
# #    Reference the page number(s) the information came from when available.
# # 5. Maintain a neutral, professional tone. Do not give personal legal opinions
# #    or advice framed as "you should do X" — describe what the document
# #    states, not what the user's course of action should be.
# # 6. Never fabricate a page number, section, or quotation not present in the
# #    tool's returned excerpts.
# # """


# # class LegalBriefAgent:
# #     """
# #     Holds the LLM, bound tools, and the two node functions you'll wire into
# #     your own LangGraph StateGraph. Does not build or compile a graph itself.
# #     """

# #     def __init__(self, model: str = "gemini-2.0-flash", temperature: float = 0.1):
# #         self.llm = ChatGoogleGenerativeAI(
# #             model=model,
# #             temperature=temperature,
# #             api_key=os.getenv("GEMINI_API_KEY"),
# #         )

# #         self.tools = [get_legal_context]
# #         self.tools_by_name = {t.name: t for t in self.tools}
# #         self.llm_with_tools = self.llm.bind_tools(self.tools)

# #     def agent_node(self, state: dict) -> dict:
# #         """
# #         Reasoning step. Expects `state["messages"]` (a list of LangChain
# #         message objects). Returns {"messages": [<new AI message>]}.
# #         Plug directly into a LangGraph node.
# #         """
# #         messages = state["messages"]
# #         full_messages = [SystemMessage(content=SYSTEM_PROMPT)] + list(messages)

# #         try:
# #             response = self.llm_with_tools.invoke(full_messages)
# #         except Exception:
# #             logger.exception("LLM invocation failed in agent_node")
# #             response = SystemMessage(
# #                 content=(
# #                     "I'm sorry, I encountered an error while processing your "
# #                     "question. Please try again in a moment."
# #                 )
# #             )

# #         return {"messages": [response]}

# #     def tool_node(self, state: dict) -> dict:
# #         """
# #         Acting step. Executes any tool calls requested by the last AI
# #         message in `state["messages"]`. Returns {"messages": [<ToolMessage>, ...]}.
# #         Plug directly into a LangGraph node.
# #         """
# #         messages = state["messages"]
# #         last_message = messages[-1]
# #         tool_outputs = []

# #         tool_calls = getattr(last_message, "tool_calls", None) or []
# #         for tool_call in tool_calls:
# #             tool_name = tool_call["name"]
# #             tool_args = tool_call["args"]
# #             tool_id = tool_call["id"]

# #             tool_function = self.tools_by_name.get(tool_name)
# #             if tool_function is None:
# #                 tool_result = f"TOOL_ERROR: Tool `{tool_name}` not found."
# #                 logger.error(tool_result)
# #             else:
# #                 try:
# #                     # LangChain tool interface compatibility: use `run` with kwargs.
# #                     tool_result = tool_function.run(**tool_args)
# #                 except Exception:
# #                     logger.exception("Tool `%s` raised an exception", tool_name)
# #                     tool_result = (
# #                         f"TOOL_ERROR: `{tool_name}` failed to execute. "
# #                         "Inform the user the document could not be searched."
# #                     )

# #             tool_outputs.append(
# #                 ToolMessage(
# #                     content=str(tool_result),
# #                     tool_call_id=tool_id,
# #                     name=tool_name,
# #                 )
# #             )

# #         return {"messages": tool_outputs}

# #     @staticmethod
# #     def should_continue(state: dict) -> str:
# #         """
# #         Optional helper for your conditional edge. Returns "tools" if the
# #         last AI message requested a tool call, else "end".
# #         """
# #         last_message = state["messages"][-1]
# #         if getattr(last_message, "tool_calls", None):
# #             return "tools"
# #         return "end"

# # if __name__ == "__main__":
# #     logging.basicConfig(level=logging.INFO)

# #     agent = LegalBriefAgent()
# #     answer = agent.get_legal_context("What are the payment terms in this contract?")
# #     print("\n=== LegalBrief Agent Answer ===")
# #     print(answer)

# """
# LegalBrief Agent: a LangGraph-based agent that answers questions about an
# uploaded legal document using the existing RAGService, via the
# `get_legal_context` tool.

# Architecture (mirrors the reasoning/acting split from the reference Job
# Search Agent, adapted for grounded legal Q&A):

#     START -> agent (reasoning) --tool_calls?--> tools (acting) -> agent -> ...
#                                 --no tool_calls?--> END

# - `agent_node`  : the LLM reasons about the question and either answers
#                   directly or emits a tool call to fetch document context.
# - `tool_node`   : executes any requested tool calls and returns their
#                   results as ToolMessages.
# - `should_continue`: routes to `tools` if the last AI message requested a
#                   tool call, otherwise ends the graph.

# Note: this step is single-turn (no persisted memory across `.ask()` calls).
# Memory will be added in a later step.
# """

# import logging
# import os

# from dotenv import load_dotenv
# from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
# from langchain_google_genai import ChatGoogleGenerativeAI
# from langgraph.graph import END, StateGraph

# from App.agents.state import AgentState
# from App.agents.tools import get_legal_context

# load_dotenv()
# logger = logging.getLogger(__name__)


# SYSTEM_PROMPT = """You are LegalBrief Agent, a professional legal-document assistant.

# Your strict operating rules:
# 1. Before answering any substantive question about the document, use the
#    `get_legal_context` tool to retrieve relevant excerpts. Do not answer from
#    general knowledge or assumption when a document-specific fact is being asked.
# 2. Base your answer ONLY on the retrieved excerpts. Do not invent clauses,
#    dates, amounts, or obligations that are not present in the retrieved text.
# 3. If the tool result contains "NO_RELEVANT_CONTEXT" or "RETRIEVAL_ERROR",
#    clearly and plainly tell the user that the document does not appear to
#    contain enough information to answer (or that the search is temporarily
#    unavailable). Do not guess to fill the gap.
# 4. When you do have relevant excerpts, write a concise, well-structured
#    answer in plain, professional language a non-lawyer can understand.
#    Reference the page number(s) the information came from when available.
# 5. Maintain a neutral, professional tone at all times. Do not provide
#    personal legal opinions, predictions about legal outcomes, or advice
#    framed as "you should do X" — describe what the document states, not
#    what the user's course of action should be.
# 6. If a question is ambiguous, answer using the most reasonable
#    interpretation based on the retrieved context rather than asking the
#    user to clarify, but note the assumption you made if it materially
#    affects the answer.
# 7. Never fabricate a page number, section, or quotation that did not appear
#    in the tool's returned excerpts.
# """


# class LegalBriefAgent:
#     """Encapsulates the LLM, tools, and compiled LangGraph for LegalBrief."""

#     def __init__(self, model: str = "gemini-2.0-flash", temperature: float = 0.1):
#         self.llm = ChatGoogleGenerativeAI(
#             model=model,
#             temperature=temperature,
#             api_key=os.getenv("GEMINI_API_KEY"),
#         )

#         self.tools = [get_legal_context]
#         self.tools_by_name = {t.name: t for t in self.tools}
#         self.llm_with_tools = self.llm.bind_tools(self.tools)

#         self.graph = self._build_graph()

#     # ---- Nodes ---------------------------------------------------------

#     def agent_node(self, state: AgentState) -> dict:
#         """Reasoning step: LLM decides to answer directly or call a tool."""
#         messages = state["messages"]
#         full_messages = [SystemMessage(content=SYSTEM_PROMPT)] + list(messages)

#         try:
#             response = self.llm_with_tools.invoke(full_messages)
#         except Exception:
#             logger.exception("LLM invocation failed in agent_node")
#             response = SystemMessage(
#                 content=(
#                     "I'm sorry, I encountered an error while processing your "
#                     "question. Please try again in a moment."
#                 )
#             )

#         return {"messages": [response]}

#     def tool_node(self, state: AgentState) -> dict:
#         """Acting step: execute any tool calls requested by the last AI message."""
#         messages = state["messages"]
#         last_message = messages[-1]
#         tool_outputs = []

#         tool_calls = getattr(last_message, "tool_calls", None) or []
#         for tool_call in tool_calls:
#             tool_name = tool_call["name"]
#             tool_args = tool_call["args"]
#             tool_id = tool_call["id"]

#             tool_function = self.tools_by_name.get(tool_name)
#             if tool_function is None:
#                 tool_result = f"TOOL_ERROR: Tool `{tool_name}` not found."
#                 logger.error(tool_result)
#             else:
#                 try:
#                     tool_result = tool_function.invoke(tool_args)
#                 except Exception:
#                     logger.exception("Tool `%s` raised an exception", tool_name)
#                     tool_result = (
#                         f"TOOL_ERROR: `{tool_name}` failed to execute. "
#                         "Inform the user the document could not be searched."
#                     )

#             tool_outputs.append(
#                 ToolMessage(
#                     content=str(tool_result),
#                     tool_call_id=tool_id,
#                     name=tool_name,
#                 )
#             )

#         return {"messages": tool_outputs}

#     # ---- Routing ---------------------------------------------------------

#     @staticmethod
#     def should_continue(state: AgentState) -> str:
#         """Route to `tools` if the last AI message requested a tool call."""
#         last_message = state["messages"][-1]
#         if getattr(last_message, "tool_calls", None):
#             return "tools"
#         return "end"

#     # ---- Graph assembly ---------------------------------------------------

#     def _build_graph(self):
#         graph = StateGraph(AgentState)
#         graph.add_node("agent", self.agent_node)
#         graph.add_node("tools", self.tool_node)

#         graph.set_entry_point("agent")
#         graph.add_conditional_edges(
#             "agent",
#             self.should_continue,
#             {"tools": "tools", "end": END},
#         )
#         graph.add_edge("tools", "agent")

#         return graph.compile()

#     # ---- Public API ---------------------------------------------------------

#     def ask(self, question: str) -> str:
#         """
#         Run a single question through the agent graph and return the final
#         answer text. Single-turn only in this step — no memory is retained
#         between calls.
#         """
#         result = self.graph.invoke({"messages": [HumanMessage(content=question)]})
#         final_message = result["messages"][-1]
#         return final_message.content


# if __name__ == "__main__":
#     logging.basicConfig(level=logging.INFO)

#     agent = LegalBriefAgent()
#     answer = agent.ask("What are the payment terms in this contract?")
#     print("\n=== LegalBrief Agent Answer ===")
#     print(answer)