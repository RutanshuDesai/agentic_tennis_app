import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain.tools import tool
from chroma_utils import ChromaUtils
import weather as w
import logging
logger = logging.getLogger(__name__)


# Load environment variables
load_dotenv()

## setting up vector store
embeddings = OllamaEmbeddings(model="nomic-embed-text:latest")

# Initialize Chroma

c = ChromaUtils(collection_name="general_docs", persist_db_directory="app_db", embeddings_model=embeddings)
vector_store = c.create_vector_collection()

@tool(response_format="content_and_artifact", description="tool to retrieve information from personal documents.")
def retrieve_context(query: str):
    """Retrieve information to help answer a query."""
    retrieved_docs = vector_store.similarity_search(query, k=3)
    serialized = "\n\n".join(
        (f"Source: {doc.metadata}\nContent: {doc.page_content}")
        for doc in retrieved_docs
    )
    logger.info("Doc retreiver used!")
    return serialized, retrieved_docs

@tool(response_format="content", description="Get weather information for a specific city and hour.")
def get_weather(city: str, date: str, hour: int):
    """Get weather information for a specific city and hour."""
    
    weather_client = w.WorldWeatherClient(api_key=os.environ.get("WEATHER_API_KEY"), base_url=w.DEFAULT_BASE_URL, timeout=10)
    weather_service = w.TennisWeatherService(weather_client)
    weather = weather_service.get_hourly_play_conditions(city, hour, date)
    logger.info("Weather tool used!")
    return weather

def get_agent(use_ollama: bool = True):
    if use_ollama:
        llm = ChatOllama(model="gpt-oss:latest")
        logger.info("Using local Ollama LLM model!")
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
        logger.info("Using external hosted LLM model!")

    system_prompt = """
    You are a personal assistant scheduling my tennis matches and other fitness activities. If specifically asked what model you running, then only share it.
    You also have access to a vector database of your personal documents.
    You can use the vector database to answer questions about your personal documents.
    You can use the weather tool to get weather information for a specific city and hour, and ultimately check if you can play tennis at that time.
    """

    agent = create_agent(
        model=llm,
        tools=[retrieve_context, get_weather], # Add tools if defined
        system_prompt=system_prompt,
    )
    return agent

