import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.tools import tool
from chroma_utils import ChromaUtils
import logging
from tools import google_calendar
from tools import weather as w
logger = logging.getLogger(__name__)

from datetime import datetime
todays_date = datetime.now().strftime("%Y-%m-%d")

# Load environment variables
load_dotenv()

## setting up vector store
embeddings = OllamaEmbeddings(model="nomic-embed-text:latest")

# Initialize Chroma

c = ChromaUtils(collection_name="general_docs", persist_db_directory=os.environ.get("VECTOR_INDEX_DB_PATH"), embeddings_model=embeddings)
vector_store = c.create_vector_collection()

@tool(response_format="content_and_artifact", description="tool to retrieve information from personal documents.")
def retrieve_context(query: str):
    """Retrieve information to help answer a query."""
    logger.info("[TOOL] retrieve_context  | query=%r", query)
    retrieved_docs = vector_store.similarity_search(query, k=3)
    serialized = "\n\n".join(
        (f"Source: {doc.metadata}\nContent: {doc.page_content}")
        for doc in retrieved_docs
    )
    logger.info("[TOOL] retrieve_context  | returned %d docs", len(retrieved_docs))
    return serialized, retrieved_docs

@tool(response_format="content", description="Get weather information for a specific city and hour.")
def get_weather(city: str, date: str, hour: int):
    """Get weather information for a specific city and hour."""
    logger.info("[TOOL] get_weather       | city=%s, date=%s, hour=%d", city, date, hour)
    weather_client = w.WorldWeatherClient(api_key=os.environ.get("WEATHER_API_KEY"), base_url=w.DEFAULT_BASE_URL, timeout=10)
    weather_service = w.TennisWeatherService(weather_client)
    weather_data = weather_service.get_hourly_play_conditions(city, hour, date)
    logger.info("[TOOL] get_weather       | done for %s @ %s %02d:00", city, date, hour)
    return weather_data

@tool(response_format="content", description="Create a calendar event.")
def create_calendar_event(summary: str, start_time: str, end_time: str, description: str = ""):
    '''
    Create a calendar event.
    Args:
        summary: summary of the event
        start_time: start time of the event
        end_time: end time of the event
        description: description of the event
    '''
    logger.info("[TOOL] create_event      | summary=%r, start=%s, end=%s", summary, start_time, end_time)
    google_calendar.create_calendar_event(summary, start_time, end_time, description)
    logger.info("[TOOL] create_event      | event created successfully")
    return "Calendar event created successfully!"

@tool(response_format="content", description="List Google Calendar events on the primary calendar for a date range.")
def list_calendar_events(start_date: str = "", end_date: str = ""):
    """
    View calendar events in a time window.

    Args:
        start_date: Optional. Start of range as YYYY-MM-DD or RFC3339. Empty = start of today (America/New_York).
        end_date: Optional. End of range as YYYY-MM-DD (inclusive) or RFC3339. Empty = 30 days after start.
    """
    start = start_date.strip() or None
    end = end_date.strip() or None
    logger.info("[TOOL] list_events       | start=%s, end=%s", start or "(today)", end or "(+30d)")
    text = google_calendar.list_calendar_events(time_min_iso=start, time_max_iso=end)
    logger.info("[TOOL] list_events       | returned %d chars", len(text))
    return text

def get_agent(model: str = "ollama"):
    """
    Create and return the tennis agent.

    Args:
        model: LLM backend to use — "ollama", "databricks", or "vertex".
    """
    if model == "ollama":
        llm = ChatOllama(model="gemma4:26b")
        logger.info("Using local Ollama LLM model!")

    elif model == "databricks":
        DATABRICKS_TOKEN = os.environ.get("DATABRICKS_TOKEN")
        DATABRICKS_BASE_URL = os.environ.get("DATABRICKS_BASE_URL")

        if not DATABRICKS_TOKEN:
            raise ValueError("DATABRICKS_TOKEN not found in environment variables.")
        if not DATABRICKS_BASE_URL:
            raise ValueError("DATABRICKS_BASE_URL not found in environment variables.")

        llm = ChatOpenAI(
            model="gemini-3-flash-preview",
            api_key=DATABRICKS_TOKEN,
            base_url=DATABRICKS_BASE_URL,
        )
        logger.info("Using Databricks-hosted LLM model!")

    elif model == "vertex":
        VERTEX_API_KEY = os.environ.get("VERTEX_API_KEY")
        if not VERTEX_API_KEY:
            raise ValueError("VERTEX_API_KEY not found in environment variables.")

        llm = ChatGoogleGenerativeAI(
            model="gemini-3.1-flash-lite-preview", # gemini-2.5-flash; gemini-3.1-flash-lite-preview ; gemini-3-flash-preview
            google_api_key=VERTEX_API_KEY,
            vertexai=True,
        )
        logger.info("Using Google Vertex AI LLM model!")

    else:
        raise ValueError(f"Unknown model '{model}'. Choose from: ollama, databricks, vertex.")

    system_prompt = f"""
        <|turn|>system
        <|channel|>thought
        You are a proactive personal fitness assistant and tennis coordinator being run on {todays_date}.
        Your goal: Determine the playability of tennis sessions and manage fitness scheduling.

        ### CAPABILITIES & TOOLS
        1.  **Vector DB (Retrieval):** Access personal documents to answer specific user questions or find player preferences.
        2.  **Weather Tool:** Retrieve hourly forecasts (Wind, Rain, Temp). When searching for the weather, always refer to ET timezone. 
        3.  **Calendar Tools:** Used to analyze events on my calendar as well as create new events. Use this tool when asked to list or fetch or view my upcoming events, as well as for analysis if I can play tennis match. When creating new events, always put on ET timezone. 

        ### TENNIS PLAYABILITY CONSTRAINTS
        A session is ONLY "Playable" if ALL these conditions are met:
        * **Wind Speed:** Must be < 10 mph.
        * **Precipitation:** Must be 0% rain during the match, 6 hours BEFORE, and 4 hours AFTER.
        * **Temperature:** Must be > 40°F and < 90°F.

        ### OPERATIONAL WORKFLOW
        When asked "Can I play tennis on [Date] at [Time] in [Location]?":
        1.  **Phase 0 (Calendar & History Check):** 
            *   List ALL calendar events for the requested [Date].
            *   Check for conflicts: A session is "Not Playable" if there is an existing event during the match time or within the 4-hour buffer AFTER the match.
            *   Check Workout History: List events for the PREVIOUS day. If any event contains "workout", "gym", "tennis", or "exercise", the user is too tired to play today ("Not Playable").
            *   Always list all events found for the requested day to the user.
        2.  **Phase 1 (Weather Validation):** If Phase 0 passes, use the Weather Tool for the requested time and the surrounding buffer window (-6h / +4h). Always note that this has been checked and show the weather ranges between the time periods for wind, rain and temperature.  
        3.  **Phase 2 (Reasoning):** Compare weather data against constraints.
        4.  **Phase 3 (Initial Summary):** Provide a clear "Playable" or "Not Playable" verdict with a brief justification (e.g., "You have a conflict at 2 PM" or "You worked out yesterday" or "Wind is 12mph").
        5.  **Phase 4 (Timeline Check):** Ask the user if they have an alternative timeline or want you to scan the rest of the day/weekend for a better window. If they provide a timeline, check all slots and summarize the best options.

        ### OUTPUT STYLE
        * Be concise, professional, and encouraging.
        * Always show the data (e.g., "Temp: 45°F, Wind: 5mph") when giving a verdict.
        <channel|>
    """

    agent = create_agent(
        model=llm,
        tools=[retrieve_context, get_weather, create_calendar_event, list_calendar_events],
        system_prompt=system_prompt,
    )
    return agent

