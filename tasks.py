from crewai import Task
from agents import single_trip_agent, distance_calculator, travel_agent


# =======================================
# Task 0: Conversational Travel Assistant
# =======================================

conversation_task = Task(
    description="""
User query: {user_input}

You are a conversational travel assistant.

Your job is to help the user calculate travel distance and cost.

Follow these rules:

1. Extract starting city and destination city if provided.
2. If cities are missing, ask the user for them.
3. Ask the user which mode of transport they want
   (car, bike, foot, bus, train).
4. Ask the user which unit they prefer
   (km or miles).
5. Once you have:
   - starting city
   - destination city
   - transport mode
   - unit
   -country

   Use the tool `get_city_distance` to retrieve the distance in meters.

6. Convert meters:
   km = meters / 1000
   miles = meters / 1609.34

7. Round to 2 decimal places.

8. ask user if they need to calculate the cost per unit. If they asks for travel cost:
   ask for cost rate if missing.
   else, say thank you

9. Respond conversationally like a helpful assistant.

Always remember earlier conversation context using memory.
""",
    agent=single_trip_agent,
    expected_output="""
A conversational response that either:
- asks a clarification question
OR
- returns the calculated distance
OR
- returns travel cost.
"""
)


# =======================================
# Task 1: Distance Conversion
# =======================================

# Distance Task optimized
distance_task = Task(
    description="""
Convert the given distance into the requested unit.

Inputs:
- Starting Address: {starting_address}
- Destination Address: {destination_address}
- Transport Mode: {mode_of_transport}
- Distance from tool: {distance_in_meters}
- Requested unit: {unit}

Rules: 
1. Use get_distance_tool to get the exact distance in meters. 
2. then, Convert the distance_in_meters to the requested unit:
   - km = meters / 1000
   - miles = meters / 1609.34
3. Round the converted distance to 2 decimal places.
4. Append the unit to the number (e.g., "1345.67 km").
5. Do NOT change the numeric value beyond conversion.
6. Do NOT add any extra text or commentary. Return only the value with unit.

Return:
- The converted distance as a string with unit.
""",
    agent=distance_calculator,
    expected_output="Distance with units (e.g., '1349.31 km')."
)

# =======================================
# Task 2: Travel Cost Calculation
# =======================================

# Travel Cost Task optimized
travel_cost_task = Task(
    description="""
Calculate travel cost.

Inputs:
- Distance: {distance_with_units}
- Cost rate: {cost_rate}
- Country: {country}

Steps:
1. Extract only the numeric value from the distance input (ignore any units like 'km' or 'miles').
2. Multiply numeric distance * cost_rate.
3. Add the correct currency symbol based on country:
   India → ₹, US → $, UK → £

Return only the cost with currency symbol.
""",
    agent=travel_agent,
    expected_output="Travel cost with currency symbol (e.g., '₹260000').",
    context=[distance_task]
)