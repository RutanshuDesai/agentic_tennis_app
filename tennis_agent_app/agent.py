import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain.tools import tool

# Load environment variables
load_dotenv()

## setting up vector store
embeddings = OllamaEmbeddings(model="nomic-embed-text:latest")

# Initialize Chroma
vector_store = Chroma(
    collection_name="app_docs",
    embedding_function=embeddings,
    persist_directory="./chroma_langchain_db",
)

@tool(response_format="content_and_artifact")
def retrieve_context(query: str):
    """Retrieve information to help answer a query."""
    retrieved_docs = vector_store.similarity_search(query, k=2)
    serialized = "\n\n".join(
        (f"Source: {doc.metadata}\nContent: {doc.page_content}")
        for doc in retrieved_docs
    )
    return serialized, retrieved_docs




def get_agent():
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
    You are a math writer while Conversation with the user
    """

    agent = create_agent(
        model=llm,
        tools=[retrieve_context], # Add tools if defined
        system_prompt=system_prompt,
    )
    return agent

