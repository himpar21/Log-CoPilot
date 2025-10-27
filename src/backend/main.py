from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
import uvicorn

from schemas import QueryRequest, QueryResponse
from llm_loader import load_local_llm
from rag_pipeline import RAGPipeline
from config import LOGS_DIRECTORY
import os

app = FastAPI(
    title="Log Analysis Copilot API",
    description="API for querying logs using a local LLM with RAG.",
    version="1.0.0",
)

# This dictionary will hold our initialized RAG pipeline
app.state.rag_pipeline = None

@app.on_event("startup")
def startup_event():
    """
    On application startup, load the LLM and initialize the RAG pipeline.
    This makes the first API call much faster.
    """
    print("Application startup...")
    if not os.path.exists(LOGS_DIRECTORY) or not os.listdir(LOGS_DIRECTORY):
        print(f"WARNING: Log directory '{LOGS_DIRECTORY}' is empty or does not exist.")
        print("Please create it and add log files before querying.")
        # We can still start the server, but queries might fail until logs are added
        # and the vector store is built (which happens on the first query if the store is missing).
    
    llm = load_local_llm()
    app.state.rag_pipeline = RAGPipeline(llm=llm)
    print("RAG pipeline initialized.")

@app.post("/api/query", response_model=QueryResponse)
async def handle_query(request: QueryRequest):
    """
    Handles a user query by passing it to the RAG pipeline.
    """
    if app.state.rag_pipeline is None:
        raise HTTPException(status_code=503, detail="RAG pipeline is not initialized. Please wait and try again.")
    
    try:
        result = app.state.rag_pipeline.query(request.query)
        return JSONResponse(content=result)
    except Exception as e:
        print(f"An error occurred during query processing: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
def health_check():
    """Simple health check endpoint."""
    return {"status": "ok", "rag_pipeline_initialized": app.state.rag_pipeline is not None}

if __name__ == "__main__":
    # To run: uvicorn main:app --host 0.0.0.0 --port 8000 --reload
    uvicorn.run(app, host="0.0.0.0", port=8000)