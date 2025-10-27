# import os
# from dotenv import load_dotenv

# load_dotenv()

# # --- Model Configuration ---
# # Using a small, capable model perfect for local execution on specified hardware.
# # Phi-3 is excellent. Other options: 'HuggingFaceH4/zephyr-7b-beta'
# LLM_MODEL_ID = "HuggingFaceH4/zephyr-7b-beta"
# EMBEDDING_MODEL_ID = "all-MiniLM-L6-v2"

# # --- Directory Configuration ---
# # Assumes a folder named 'local_logs' is in the same directory as the 'src' folder.
# # Project Root -> local_logs/
# #              -> src/backend/
# LOGS_DIRECTORY = os.getenv("LOGS_DIRECTORY", "../../logs")
# VECTOR_STORE_PATH = os.getenv("VECTOR_STORE_PATH", "vector_store/faiss_index")

# # --- RAG Configuration ---
# CHUNK_SIZE = 1000
# CHUNK_OVERLAP = 100
# RETRIEVER_K = 3 # Number of relevant log chunks to retrieve


import os
from dotenv import load_dotenv

load_dotenv()

# --- Model Configuration ---
# The model name to use from your local Ollama instance.
# Make sure you have pulled this model, e.g., by running `ollama run phi3`
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral:latest") 
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# Embedding model remains the same, as it's used for the retriever.
EMBEDDING_MODEL_ID = "all-MiniLM-L6-v2"

# --- Directory Configuration ---
# Assumes a folder named 'logs' is in the project root.
LOGS_DIRECTORY = os.getenv("LOGS_DIRECTORY", "../../logs")
VECTOR_STORE_PATH = os.getenv("VECTOR_STORE_PATH", "vector_store/faiss_index")

# --- RAG Configuration ---
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 100
RETRIEVER_K = 3 # Number of relevant log chunks to retrieve