import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent

# Load environment variables
load_dotenv()

def get_agent():
    DATABRICKS_TOKEN = os.environ.get("DATABRICKS_TOKEN")
    
    if not DATABRICKS_TOKEN:
        raise ValueError("DATABRICKS_TOKEN not found in environment variables.")

    # Create a LangChain chat model that talks to your Databricks serving endpoint
    # Using the exact configuration from app.ipynb
    llm = ChatOpenAI(
        model="gemini-2-5-flash", 
        api_key=DATABRICKS_TOKEN,
        base_url="https://dbc-a53449c8-fa32.cloud.databricks.com/serving-endpoints/",
    )

    system_prompt = """
    You are a math writer while Conversation with the user
    """

    agent = create_agent(
        model=llm,
        # tools=[], # Add tools if defined
        system_prompt=system_prompt,
    )
    return agent

