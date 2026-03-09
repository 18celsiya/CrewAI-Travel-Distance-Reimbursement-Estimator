# ================================================
# Route Cost Calculator AI - Agents
# This module defines the agents for calculating travel distance and cost.
# ================================================

# Required imports
from dotenv import load_dotenv # for loading environment variables from .env file
import os # for environment variables
from crewai import Agent, LLM # for defining agents and language model
from crewai.memory import Memory # for agent memory
from tools import get_city_distance # load the tool to get city distance

# Load environment variables from .env file
load_dotenv()


# ------------------------------------------
# LLM configuration
# -------------------------------------------
llm = LLM(
    provider="openrouter",  # MUST specify the provider
    model="openai/gpt-4o",              # OpenRouter model name
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
    temperature=0,
    max_tokens=200
)

# ------------------------------------------
# Memory configuration
# -------------------------------------------
# Memory for single_trip_agent (stores conversation context & user preferences)
trip_memory = Memory(llm=llm)

# Memory for distance_calculator (stores only recent conversions or preferred units)
distance_memory = Memory(llm=llm)


# ======================================================
# Conversation Agent: Collects user input and calls tools to get distance
# =======================================================

# Agent to collect user input and call tools to get distance
single_trip_agent = Agent(
    role= "Trip Distance & Cost Bot",
    goal="Calculate travel distance and cost",
    backstory="Quickly collect start, destination, mode, unit, and country. Use tools to find distance.",
    llm=llm,
    tools=[get_city_distance],
    memory=trip_memory
)

# =====================================================================
# Distance Calculator Agent: Calculates the distance from get_distance_tool 
# and converts distance from meters to km or miles
# =====================================================================

distance_calculator = Agent(
    role="Distance Calculator",
    goal="Convert meters to km or miles",
    backstory="""
    Convert distance from meters to km or miles, round to 2 decimals, and return only the number with unit, e.g., '1349.32 km'.
    """,
llm = llm,
    tools=[get_city_distance],
    temperature=0,
    verbose=True,
    memory=False,
    max_execution_time=1200,
    memory=distance_memory
)

# =================================================================
# Travel Cost Calculator Agent: Calculates travel cost from distance
# ================================================================

travel_agent = Agent(
    role="Travel Cost Calculator",
    goal="Calculate travel cost from distance",
    backstory=""" Multiply numeric distance by cost rate. Add currency symbol based on country:
    Return only the cost with symbol, e.g., '₹2400'.
    """,
llm = llm,
    temperature=0,
    verbose=True,
    memory=False,
    max_execution_time=1200
)