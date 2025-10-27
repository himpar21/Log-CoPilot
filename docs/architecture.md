# Log Analysis Copilot - Architecture

This document outlines the architecture of the Log Analysis Copilot, a full-stack application designed for interactive log analysis using a local Large Language Model (LLM) with Retrieval-Augmented Generation (RAG).

## 1. High-Level Overview

The application consists of two main parts:

1.  **React Frontend**: A web-based chat interface where users can ask natural language questions about their logs.
2.  **Python (FastAPI) Backend**: An API that processes user queries, retrieves relevant log data, uses an LLM to generate an answer, and returns a structured response.

The core of the application is the **RAG pipeline** on the backend, which allows the LLM to answer questions based on the content of provided log files, rather than relying solely on its pre-trained knowledge.



---

## 2. Project Structure

The project is organized into two main directories:

```
.
├── logs/                  # (User-provided) Directory for log files.
├── src/
│   ├── backend/           # All Python backend code (FastAPI, RAG, etc.)
│   └── frontend/          # All React frontend code (CRA)
├── ARCHITECTURE.md        # This file
└── SETUP.md               # Setup and installation guide
```

---

## 3. Backend Architecture (`src/backend`)

The backend is built with Python using the FastAPI framework and leverages the LangChain library to construct the RAG pipeline. It runs a local LLM via Ollama.

### Components

#### a. API Server (`main.py`)

*   **Framework**: FastAPI, running on a `uvicorn` ASGI server.
*   **Endpoints**:
    *   `POST /api/query`: The main endpoint that accepts a user's query, passes it to the RAG pipeline, and returns the analysis.
    *   `GET /api/health`: A simple health check endpoint.
*   **Startup Logic**: On application startup (`@app.on_event("startup")`), it pre-loads the LLM and initializes the `RAGPipeline`. This significantly reduces the latency of the first user query by avoiding cold starts.

#### b. RAG Pipeline (`rag_pipeline.py`)

This is the heart of the application's intelligence. It's responsible for both ingesting log data and processing queries.

**Initialization & Ingestion:**

1.  **Vector Store Setup**: The pipeline first checks if a pre-built vector store exists at `vector_store/faiss_index`.
2.  **Loading (if store exists)**: If the store exists, it's loaded directly into memory using FAISS. This is fast and avoids re-processing logs on every startup.
3.  **Building (if store is missing)**:
    *   **Log Parsing**: It calls `log_parser.load_and_parse_logs()` to read all files from the `../../logs` directory. The parser intelligently handles various formats (`.jsonl`, `.apache`, key-value, etc.), converting each log entry into a structured LangChain `Document`.
    *   **Chunking**: The loaded documents are split into smaller, overlapping chunks using `RecursiveCharacterTextSplitter`. This is crucial for providing focused context to the LLM.
    *   **Embedding & Indexing**: An embedding model (`all-MiniLM-L6-v2`) is used to convert the text chunks into numerical vectors. These vectors are then stored in a `FAISS` vector store, which allows for efficient similarity searches.
    *   **Saving**: The newly created vector store is saved to disk for future use.

**Query Processing (LCEL Chain):**

The pipeline uses a **LangChain Expression Language (LCEL)** chain to process queries in a declarative and streamable manner.

1.  **Retrieve**: The user's query is passed to the FAISS `retriever`, which performs a similarity search and returns the top `k` most relevant log chunks.
2.  **Format Context**: The retrieved `Document` objects are formatted into a single string, which serves as the context for the LLM.
3.  **Prompt**: A `ChatPromptTemplate` combines the original user question with the retrieved context. The prompt is carefully engineered to instruct the LLM to act as a log analysis expert and to **output its response in a specific JSON format** (`{"analysis": "...", "summary": "...", "evidence": [...]}`).
4.  **Generate**: The formatted prompt is sent to the local LLM loaded via `llm_loader.py`. The `ChatOllama` instance is configured with `format="json"` to enforce this structured output.
5.  **Parse & Sanitize**:
    *   The LLM's string output is parsed into a Python dictionary.
    *   The response is passed to `security.mask_sensitive_data()` to redact information like IP addresses and emails before being sent to the frontend.

#### c. LLM Loader (`llm_loader.py`)

*   A utility module responsible for connecting to and configuring the local LLM.
*   It uses `langchain_ollama.ChatOllama` to interface with the Ollama server.
*   Configuration for the model name (`mistral:latest`, `phi3`, etc.) and base URL are pulled from `config.py`.

#### d. Log Parser (`log_parser.py`)

*   A critical data preparation module that makes the system robust to different log formats.
*   It uses a series of regular expressions and custom parsing functions to handle:
    *   JSON Lines (`.jsonl`)
    *   Apache common log format
    *   Pipe-separated single-line logs
    *   Key-value pair logs
    *   "Pretty" multi-line block logs
*   It gracefully falls back to treating unknown formats as plain text lines. Each parsed entry is converted into a LangChain `Document` with metadata (like source file and line number).

#### e. Configuration & Schemas

*   **`config.py`**: Centralizes all application settings (model IDs, file paths, RAG parameters) and uses `python-dotenv` to load them from a `.env` file.
*   **`schemas.py`**: Defines Pydantic models (`QueryRequest`, `QueryResponse`) for robust API data validation and serialization.
*   **`security.py`**: A simple module for post-processing the LLM output to mask sensitive data, adding a layer of security.

---

## 4. Frontend Architecture (`src/frontend`)

The frontend is a standard **Create React App** that provides a user-friendly chat interface.

### Components

*   **`App.js`**: The root component that manages the application's state, including the list of messages and the loading status. It orchestrates the interaction between the chat window and the input bar.
*   **`ChatWindow.js`**: Renders the list of messages. It automatically scrolls to the bottom as new messages are added and displays a "typing" indicator while waiting for the backend response.
*   **`Message.js`**: A versatile component that renders a single message. It handles different styles for `user` and `assistant` messages. Crucially, it also parses and displays the `evidence` array from the assistant's response, with dedicated rendering for log snippets, tables, and errors.
*   **`InputBar.js`**: Provides the text input field and send button for the user.
*   **`Header.js`**: Displays the application title and a visual indicator for the LLM status.

### API Communication

*   **`api/chatService.js`**: A dedicated module that abstracts all communication with the backend. It contains the `sendMessageToApi` function, which makes a `fetch` call to the `/api/query` endpoint.
*   **Proxy**: The `package.json` file includes a `"proxy": "http://localhost:8000"` entry. This tells the React development server to forward any unknown API requests (like `/api/query`) to the backend server, seamlessly avoiding CORS issues during local development.

---

## 5. Data Flow (Query Lifecycle)

1.  **User Input**: A user types a question into the `InputBar` on the frontend.
2.  **API Request**: `chatService.js` sends a POST request to `http://localhost:8000/api/query` with the user's query.
3.  **Backend Processing**:
    *   FastAPI receives the request.
    *   The `RAGPipeline`'s retriever finds relevant log chunks from the FAISS vector store.
    *   The context and query are formatted into a prompt.
    *   The prompt is sent to the local Ollama LLM.
4.  **LLM Generation**: The LLM generates a JSON object containing the analysis, summary, and supporting evidence.
5.  **Sanitization**: The backend masks sensitive data in the LLM's response.
6.  **API Response**: The sanitized JSON is sent back to the frontend.
7.  **UI Update**: The frontend receives the JSON, adds the new assistant message to its state, and the `ChatWindow` re-renders to display the response, including the formatted evidence.
