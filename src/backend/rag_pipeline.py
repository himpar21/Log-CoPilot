import os
import json
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser

from config import LOGS_DIRECTORY, VECTOR_STORE_PATH, EMBEDDING_MODEL_ID, CHUNK_SIZE, CHUNK_OVERLAP, RETRIEVER_K
from log_parser import load_and_parse_logs
from security import mask_sensitive_data

class RAGPipeline:
    def __init__(self, llm):
        self.llm = llm
        self.retriever = None
        self._setup_pipeline()

    def _setup_pipeline(self):
        """Initializes the vector store and the RAG chain."""
        embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_ID)

        if os.path.exists(VECTOR_STORE_PATH):
            print("Loading existing vector store...")
            vector_store = FAISS.load_local(VECTOR_STORE_PATH, embeddings, allow_dangerous_deserialization=True)
        else:
            print("Building new vector store...")
            print(f"Loading logs from: {LOGS_DIRECTORY}")
            documents = load_and_parse_logs(LOGS_DIRECTORY)
            if not documents:
                raise ValueError("No documents found in the log directory. Cannot build vector store.")
            
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
            chunks = text_splitter.split_documents(documents)
            
            vector_store = FAISS.from_documents(chunks, embeddings)
            os.makedirs(os.path.dirname(VECTOR_STORE_PATH), exist_ok=True)
            vector_store.save_local(VECTOR_STORE_PATH)
            print(f"Vector store built and saved to {VECTOR_STORE_PATH}")

        self.retriever = vector_store.as_retriever(search_kwargs={"k": RETRIEVER_K})
        
        # --- Prompt Engineering ---
        # This generic prompt works well with Ollama's JSON mode.
        # It clearly instructs the model on the desired output format.
        template = """
        You are an expert Log Analysis Assistant. Your task is to answer questions based ONLY on the provided log snippets.
        Do not make up information. If the context does not contain the answer, state that clearly.
        
        Present your answer in two parts:
        1. 4-5 line summary answering the user's question and explaining the logs.
        2. The exact log entries or data that support your answer, presented as evidence.

        Your final output must be a single JSON object with three keys: "analysis", "summary" and "evidence".
        The "evidence" key should be a list of objects, where each object has a "type" (e.g., "log") and "content" (the log data).
        
        Question: {question}

        Context from Logs:
        {context}
        """
        
        prompt = ChatPromptTemplate.from_template(template)

        def format_docs(docs):
            return "\n\n".join(f"Source: {doc.metadata.get('source', 'N/A')}, Line: {doc.metadata.get('line', 'N/A')}\n{doc.page_content}" for doc in docs)

        def parse_json_output(text: str):
            """Safely parse the LLM's JSON output string."""
            try:
                return json.loads(text)
            except json.JSONDecodeError:
                print(f"Failed to parse LLM JSON output: {text}")
                return {
                    "summary": "The model's response was not in the expected JSON format.",
                    "evidence": [{"type": "error", "content": text}]
                }

        self.chain = (
            {"context": self.retriever | RunnableLambda(format_docs), "question": RunnablePassthrough()}
            | prompt
            | self.llm
            | StrOutputParser()
            | RunnableLambda(parse_json_output)
        )

    def query(self, user_query: str):
        """Executes a query against the RAG chain."""
        print(f"Received query: {user_query}")
        response = self.chain.invoke(user_query)

        # Mask sensitive data and ensure consistent output format
        if 'summary' in response and isinstance(response.get('summary'), str):
            response['summary'] = mask_sensitive_data(response['summary'])
        
        if 'evidence' in response and isinstance(response.get('evidence'), list):
            for item in response['evidence']:
                content = item.get('content')
                content_str = ""

                # Ensure the content is always a string before masking
                if isinstance(content, dict):
                    # If it's a dictionary, convert it to a formatted JSON string
                    content_str = json.dumps(content, indent=2)
                elif isinstance(content, str):
                    # If it's already a string, use it directly
                    content_str = content
                elif content is not None:
                    # For any other type (numbers, etc.), convert to a plain string
                    content_str = str(content)
                
                # Now, mask the guaranteed-to-be-string content and update the item
                item['content'] = mask_sensitive_data(content_str)
        
        return response