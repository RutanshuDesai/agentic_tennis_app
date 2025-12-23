### Tennis AI Agent — Personal Scheduling Assistant

This project is an agentic AI assistant that helps me schedule my tennis matches and other fitness activities.
The agent connects to my Google Calendar and a Weather API to determine whether I can play at a specified time and location.

### 🔧 What the agent does today

Understands natural-language prompts like:
“Can I play tennis tomorrow at 5 PM at Cary Tennis Park?”

Checks:

* 🌦 Weather conditions (rain, storms, temperature)

* 📅 Calendar availability (busy, conflicts, travel)

* If conditions are good, the agent:

    - Creates a Tennis Match Event on my Google Calendar

    - Includes optional opponent name in the event title

* All agent reasoning + prompts + tool executions are tracked in LangSmith for full observability.

### 🚀 Upcoming enhancements

* Suggests alternative playable times when the requested time is not feasible

* Tracks other fitness activities (gym, strength, endurance, stability)

* Helps balance a weekly plan of:

    - Tennis

    - Strength training

    - Stability work

    - Endurance sessions


### decisions made
1. langchain v1 - for easier agent build
2. chromadb - easier local vector db with production suppoort if need to expand
3. unstructed - for processing pdf and docs
4. llm - openai oss , openai top model with local run option. alternative - use dbrx hosted model since i have access to it. 
5. streamlit - easy app build. easy debug and hosting
6. container architecture - easy to shift and lift the application. cloud agnostic. can be hosted provate server like raspberry pi
7. GCP cloud run - easier platform to get started. 
