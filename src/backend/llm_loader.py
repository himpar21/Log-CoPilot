from langchain_ollama import ChatOllama
from config import OLLAMA_MODEL, OLLAMA_BASE_URL

def load_local_llm():
    """
    Loads a model from a local Ollama instance.
    """
    print(f"Loading Ollama model: '{OLLAMA_MODEL}' from {OLLAMA_BASE_URL}...")
    
    # Instantiate the Ollama model
    # We use format="json" to ensure the model's output is a valid JSON string.
    # Other parameters like temperature are passed directly.
    llm = ChatOllama(
        model=OLLAMA_MODEL,
        base_url=OLLAMA_BASE_URL,
        temperature=0,
        top_p=0.9,
        num_predict=2048,  # Corresponds to max_new_tokens
        format="json",    # Enforce JSON output
    )

    print("Ollama model loaded successfully.")
    return llm