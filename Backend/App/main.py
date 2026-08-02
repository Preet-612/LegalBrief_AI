from fastapi import FastAPI
from pydantic import BaseModel

from App.Workflow.work import summarize_contract, chat_with_contract

app = FastAPI()


@app.get("/")
def root():
    return {"status": "LegalBrief API is running"}


class SummaryRequest(BaseModel):
    query: str


class ChatRequest(BaseModel):
    question: str


@app.post("/summarize")
def summarize(request: SummaryRequest):

    summary = summarize_contract(request.query)

    return {"summary": summary}


@app.post("/chat")
def chat(request: ChatRequest):

    answer = chat_with_contract(request.question)

    return {"answer": answer}
# from fastapi import FastAPI
# from pydantic import BaseModel

# from App.Workflow.work import summarize_contract, chat_with_contract

# app = FastAPI()


# class SummaryRequest(BaseModel):
#     query: str


# class ChatRequest(BaseModel):
#     question: str


# @app.post("/summarize")
# def summarize(request: SummaryRequest):

#     summary = summarize_contract(request.query)

#     return {"summary": summary}


# @app.post("/chat")
# def chat(request: ChatRequest):

#     answer = chat_with_contract(request.question)

#     return {"answer": answer}