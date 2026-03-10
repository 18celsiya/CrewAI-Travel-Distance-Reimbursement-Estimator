# ====================================================
# Tasks for Route Cost Calculator AI
# ====================================================
from crewai import Task
from agents import single_trip_agent, distance_calculator, travel_agent

# ------------------------------------------------------------------
# Conversation Task
# ------------------------------------------------------------------
# This is the main task that handles the entire conversation with the user. It uses the single_trip_agent which has memory enabled to remember previous interactions. The agent will ask for necessary information, use tools to calculate distance, and respond conversationally.
conversation_task = Task(
    description="""
User query: {user_input}

You are a conversational Trip Distance & Cost Bot.

Rules:
1. Extract starting city and destination city from the user input.
2. If missing, ask the user for them.
3. Ask which mode of transport (car, bike, foot, bus, train) if missing.
4. Ask which unit (km or miles) if missing.
5. Use get_city_distance to get distance in meters.
6. Convert meters:
   km = meters / 1000
   miles = meters / 1609.34
   Round to 2 decimals.
7. 7. Ask the user if they want to calculate the reimbursement amount by providing the cost per kilometer.
8. Respond conversationally and remember previous conversation using memory.
""",
    agent=single_trip_agent,
    expected_output="""
Conversational response that either:
- asks a clarification question
- returns the calculated distance
- returns travel cost.
"""
)

# -----------------------------------------------------------
# Distance Task
# -----------------------------------------------------------------
# This task is responsible for converting the distance obtained from the tool (in meters) to the requested unit (km or miles). It uses the distance_calculator agent which does not have memory enabled since it only performs a specific calculation based on the input provided.
distance_task = Task(
    description="""
Convert distance to requested unit.

Inputs:
- Starting Address: {starting_address}
- Destination Address: {destination_address}
- Transport Mode: {mode_of_transport}
- Distance from tool: {distance_in_meters}
- Requested unit: {unit}

Rules:
1. Convert distance_in_meters to requested unit:
   - km = meters / 1000
   - miles = meters / 1609.34
2. Round to 2 decimals.
3. Return only the numeric value with unit (e.g., '1345.67 km').
""",
    agent=distance_calculator,
    expected_output="Distance with units (e.g., '1349.31 km')."
)

# --------------------------------------------------------------
# Travel Cost Task
# -----------------------------------------------------------------------
# This task calculates the travel reimbursement cost based on the distance and cost rate. It uses the travel_agent which does not have memory enabled since it performs a specific calculation based on the input provided.
travel_cost_task = Task(
    description="""
Calculate reimbursement amount.

Inputs:
- Distance: {distance_with_units}
- Cost rate: {cost_rate}
- Country: {country}

Steps:
1. Extract numeric value from distance.
2. Multiply distance by cost_rate.
3. Add currency symbol based on country:
   - India → ₹
   - US → $
   - UK → £
4. Return only cost with symbol.
""",
    agent=travel_agent,
    expected_output="Travel cost with currency symbol (e.g., '₹260000').",
    context=[distance_task]
)