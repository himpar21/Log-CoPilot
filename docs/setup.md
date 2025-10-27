# Log Analysis Copilot - Setup Guide

This guide provides step-by-step instructions to set up and run the Log Analysis Copilot on your local machine.

## 1. Prerequisites

Before you begin, ensure you have the following installed:

*   **Git**: To clone the repository.
*   **Python**: Version 3.9 or newer.
*   **Node.js**: Version 18.0 or newer.
*   **Ollama**: For running the local Large Language Model. Download it from [ollama.ai](https://ollama.ai/).

## 2. Initial Setup

### Step 2.1: Clone the Repository

Clone this repository to your local machine:

```bash
git clone <your-repository-url>
cd <your-repository-name>
```

### Step 2.2: Add Your Log Files

The application analyzes logs from a specific directory.

1.  In the project's root directory, create a folder named `logs`.
2.  Place all the log files you want to analyze inside this `logs` folder.

The application is designed to parse several common formats out-of-the-box, including:
*   JSON Lines (`.jsonl`)
*   Apache logs (`.apache`)
*   Key-value logs (e.g., `key1=value1 key2=value2`)
*   Pipe-separated logs
*   Plain text files

## 3. Backend Setup

The backend is a Python application that powers the RAG pipeline and API.

### Step 3.1: Create and Activate a Virtual Environment

Navigate to the backend directory and create a Python virtual environment. This isolates the project's dependencies.

```bash
cd src/backend
python -m venv venv
```

Activate the environment:
*   **On macOS/Linux:**
    ```bash
    source venv/bin/activate
    ```
*   **On Windows:**
    ```bash
    .\venv\Scripts\activate
    ```

You will know the environment is active when you see `(venv)` at the beginning of your command prompt.

### Step 3.2: Install Python Dependencies

Install all required Python packages using the `requirements.txt` file.

```bash
pip install -r requirements.txt
```

### Step 3.3: Set Up Ollama

1.  **Install Ollama**: If you haven't already, install Ollama from [ollama.ai](https://ollama.ai/) and ensure it is running.
2.  **Pull an LLM**: The application needs a model to be available in Ollama. Pull the default model by running:
    ```bash
    ollama run mistral:latest
    ```
    Alternatively, you can use another model like `phi3`. If you use a different model, you will need to configure it in the next step.

### Step 3.4: Configure Environment Variables

The backend uses a `.env` file for configuration.

1.  In the `src/backend` directory, create a new file named `.env`.
2.  Copy the following content into it. The default values are suitable for a standard local setup.

    ```env
    # .env file for backend configuration

    # The model to use from your local Ollama instance.
    # Make sure you have pulled this model (e.g., `ollama run mistral:latest`).
    OLLAMA_MODEL="mistral:latest"

    # The base URL for the Ollama API server.
    OLLAMA_BASE_URL="http://localhost:11434"

    # --- Optional: You can override default paths if needed ---
    # LOGS_DIRECTORY="../../logs"
    # VECTOR_STORE_PATH="vector_store/faiss_index"
    ```

    > **Note**: If you chose a different model in the previous step (e.g., `phi3`), update the `OLLAMA_MODEL` variable here.

## 4. Frontend Setup

The frontend is a standard React application.

### Step 4.1: Install Node.js Dependencies

Open a **new terminal window** and navigate to the frontend directory.

```bash
cd src/frontend
npm install
```

## 5. Running the Application

You will need two separate terminal windows to run both the backend and frontend servers simultaneously.

### Terminal 1: Start the Backend Server

1.  Make sure you are in the `src/backend` directory.
2.  Ensure your Python virtual environment is activated (`source venv/bin/activate` or `.\venv\Scripts\activate`).
3.  Start the FastAPI server using `uvicorn`:

    ```bash
    uvicorn main:app --reload
    ```

4.  **Important**: The first time you run the backend, it will need to **build the vector store** from your log files. This process involves parsing, chunking, and embedding all the data. It can take several minutes depending on the size of your logs. You will see log messages like "Building new vector store...". Subsequent startups will be much faster as they will load the pre-built store from disk.

    The server is ready when you see a message like:
    `Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)`

### Terminal 2: Start the Frontend Server

1.  Make sure you are in the `src/frontend` directory.
2.  Start the React development server:

    ```bash
    npm start
    ```

3.  This will automatically open a new tab in your web browser.

## 6. Access the Application

Open your web browser and navigate to:

**[http://localhost:3000](http://localhost:3000)**

You should now see the Log Analysis Copilot interface. You can start asking questions about the logs you provided in the `logs` directory.

---

## Troubleshooting

*   **CORS Error**: The frontend is configured to proxy API requests to the backend, which should prevent CORS errors. If you still encounter one, ensure the `proxy` setting in `src/frontend/package.json` is `http://localhost:8000` and that your backend is running on that port.
*   **`allow_dangerous_deserialization`**: The `FAISS.load_local` function uses this flag because it loads a file from disk using Python's `pickle` module, which can be a security risk if the file is from an untrusted source. Since you are building and loading the file locally, this is considered safe in this context.
*   **No Logs Found**: If you see an error like `ValueError: No documents found...`, ensure you have created the `logs` directory at the **root of the project** (at the same level as the `src` folder) and that it contains your log files.
*   **Ollama Connection Error**: If the application can't connect to the LLM, make sure Ollama is running and that the `OLLAMA_BASE_URL` in your `.env` file is correct.
