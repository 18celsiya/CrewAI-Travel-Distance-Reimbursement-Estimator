# agents.py
from dotenv import load_dotenv
import os
from crewai import Agent, LLM
from crewai.memory import Memory
from tools import get_city_distance

load_dotenv()


# -----------------------
# LLM configuration
# -----------------------
llm = LLM(
    provider="openrouter",  # MUST specify the provider
    model="openai/gpt-4o",              # OpenRouter model name
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
    temperature=0.3,
    max_tokens=200
)

# -----------------------
# Memory for conversational context
# -----------------------
memory = Memory(llm=llm)

# =======================
# Conversational Travel Assistant Agent
# =======================
# Keep backstories extremely lean
single_trip_agent = Agent(
    role="Travel Assistant",
    goal="Calculate travel distance and cost",
    backstory="Quickly collect start, destination, mode, unit, and country. Use tools to find distance.",
    llm=llm,
    tools=[get_city_distance],
    memory=memory
)

# =======================
# Distance Conversion Agent
# =======================
distance_calculator = Agent(
    role="Distance Calculator",
    goal="Convert meters to km or miles",
    backstory="""
Convert distance from meters to km or miles, round to 2 decimals,
and return only the number with unit, e.g., '1349.32 km'.
""",
llm = llm,
    tools=[get_city_distance],
    temperature=0,
    verbose=True,
    memory=False,
    max_execution_time=1200
)

# =======================
# Travel Cost Calculator Agent
# =======================
travel_agent = Agent(
    role="Travel Cost Calculator",
    goal="Calculate travel cost from distance",
    backstory="""
Multiply numeric distance by cost rate.
Add currency symbol based on country:
Return only the cost with symbol, e.g., '₹2400'.
""",
llm = llm,
    temperature=0,
    verbose=True,
    memory=False,
    max_execution_time=1200
)