import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain.tools import tool
import chroma_utils as c

# Load environment variables
load_dotenv()

## setting up vector store
embeddings = OllamaEmbeddings(model="nomic-embed-text:latest")
# Initialize Chroma
vector_store = c.instantiate_vector_db(collection_name="general_docs", persist_db_directory="app_db", embeddings_model=embeddings)

@tool(response_format="content_and_artifact")
def retrieve_context(query: str):
    """Retrieve information to help answer a query."""
    retrieved_docs = vector_store.similarity_search(query, k=3)
    serialized = "\n\n".join(
        (f"Source: {doc.metadata}\nContent: {doc.page_content}")
        for doc in retrieved_docs
    )
    return serialized, retrieved_docs




def get_agent(use_ollama: bool = True):
    if use_ollama:
        llm = ChatOllama(model="gpt-oss:latest")
    else:
        DATABRICKS_TOKEN = os.environ.get("DATABRICKS_TOKEN")
        DATABRICKS_BASE_URL = os.environ.get("DATABRICKS_BASE_URL")
        
        if not DATABRICKS_TOKEN:
            raise ValueError("DATABRICKS_TOKEN not found in environment variables.")
        if not DATABRICKS_BASE_URL:
            raise ValueError("DATABRICKS_BASE_URL not found in environment variables.")

        # Create a LangChain chat model that talks to your Databricks serving endpoint
        # Using the exact configuration from app.ipynb
        llm = ChatOpenAI(
            model="gemini-2-5-flash", 
            api_key=DATABRICKS_TOKEN,
            base_url=DATABRICKS_BASE_URL,
        )

    system_prompt = """
    You are a personal assistant scheduling my tennis matches and other fitness activities. You can share what LLM you are using to answer the questions. 
    You also have access to a vector database of your personal documents.
    You can use the vector database to answer questions about your personal documents.
    """

    agent = create_agent(
        model=llm,
        tools=[retrieve_context], # Add tools if defined
        system_prompt=system_prompt,
    )
    return agent

