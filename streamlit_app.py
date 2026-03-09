# ====================================================================
# Streamlit App for Route Distance & Cost Estimation
# This app allows users to calculate travel distance and cost between cities.
# Users can interact via chat or upload CSV/Excel files for batch processing.
# ====================================================================

# Required imports
import sys
print("Python executable:", sys.executable)

import streamlit as st
import pandas as pd
import io
from crewai import Crew
from agents import single_trip_agent, distance_calculator, travel_agent
from tasks import conversation_task, distance_task, travel_cost_task
from tools import get_city_distance
# ========================================================================

# Set Streamlit page configuration
st.set_page_config(
    page_title="Route Distance & Cost Estimator",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
body { background-color: #0E1117; font-family: 'Helvetica', sans-serif; }
h1 { color: #FFD700 !important; text-align: center; font-size: 3rem; font-weight: bold; }
.stButton>button { background-color: #FFD700; color: #0E1117; border-radius:12px; padding:10px 24px; font-size:16px; font-weight:bold; width: 100%; }
.stDownloadButton>button { background-color: #1E90FF; color:#FAFAFA; border-radius:12px; padding:10px 24px; font-size:16px; font-weight:bold; }
.stSelectbox, .stTextInput, .stRadio, .stFileUploader > div > div > input { border-radius:12px; background-color:#262730; color:#FAFAFA; }
.dataframe tbody tr:hover { background-color: #1a1c23; }
</style>
""", unsafe_allow_html=True)

# Display header with GIF
st.markdown("""
<div style="display: flex; align-items: center; justify-content: center; gap: 30px;">
    <img src="https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExbzF6b3Vnb2U3Ymh4aGNycGJjYnJhbHpieG16aHp1MWhjcGQ5ZjE1eSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9cw/4T1yKz1IpdcvCi9o6e/giphy.gif" width="60"/>
    <h1>Route Distance & Cost Estimator</h1>
</div>
""", unsafe_allow_html=True)

#=========================================================================
# subheader and description
# mode selection for single vs batch
mode = st.selectbox(
    "Select Calculation Mode:",
    ['Single Trip Between Two Cities', 'Multiple trips calculation via CSV/Excel']
)

# setup conversation crew for single trip mode
if "conversation_crew" not in st.session_state:
    st.session_state.conversation_crew = Crew(
        agents=[single_trip_agent],
        tasks=[conversation_task],
        verbose=True
    )

# session state to store conversation history
conversation_crew = st.session_state.conversation_crew

# Initialize conversation history in session state if not already present
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []

# User input 
user_input = st.chat_input("Ask a question about travel or distance")

# handle user input and agent responses
if user_input:
    # Display user input
    with st.chat_message("user"):
        st.write(user_input)
    # store user input in conversation history
    st.session_state.conversation_history.append(("You", user_input))

    # Decide which agent to use based on user input
    with st.spinner("Processing..."):
        try:
            if "convert" in user_input.lower() or "meters" in user_input.lower() or "km" in user_input.lower() or "miles" in user_input.lower():
                # Use distance calculator for conversion questions
                result_obj = distance_calculator.kickoff({
                    "user_input": user_input
                })
            elif "cost" in user_input.lower() or "price" in user_input.lower() or "₹" in user_input:
                # Use travel cost agent if explicitly asking for cost (optional)
                result_obj = travel_agent.kickoff({
                    "user_input": user_input
                })
            else:
                # Default: use single_trip_agent for travel questions
                result_obj = conversation_crew.kickoff({
                    "user_input": user_input
                })

            response = str(result_obj)

        except Exception as e:
            response = f"Error: {e}"

    # Display assistant response
    with st.chat_message("assistant"):
        st.write(response)

    st.session_state.conversation_history.append(("Assistant", response))

# Display conversation history
for speaker, text in st.session_state.conversation_history:
    if speaker == "You":
        with st.chat_message("user"):
            st.write(text)
    else:
        with st.chat_message("assistant"):
            st.write(text)

# =========================================================
# Batch Calculation via CSV/Excel
# =========================================================

if mode == "Multiple trips calculation via CSV/Excel":
    file_type = st.selectbox("Select file type:", ['CSV', 'Excel']) # option to select file type for better user experience
    upload_file = st.file_uploader(f"Upload your {file_type} file:", type=['csv','xlsx']) # accept both csv and excel files for batch processing

    if upload_file:
        df = pd.read_csv(upload_file) if file_type=='CSV' else pd.read_excel(upload_file)
        st.success("File loaded successfully!")

        # UI for selecting columns and options
        col1, col2 = st.columns(2)
        with col1:
            starting_address_column = st.selectbox("Select column for starting address:", df.columns)
            distance_unit = st.selectbox('Distance unit:', ['km','miles']).lower()
            cost_rate_input = st.text_input("Travel cost per unit distance:", value="200")

        with col2:
            destination_option = st.radio("Destination address option:", ['Single Fixed Address', 'Select Column from File'])
            if destination_option == 'Single Fixed Address':
                fixed_destination_address = st.text_input("Enter destination address:", value="Chennai")
                use_destination_column = False
            else:
                destination_address_column = st.selectbox("Select column for destination address:", df.columns)
                use_destination_column = True
            
            # Mode of transport selection
            transport_mode = st.selectbox("Mode of transport:", [
                "car", "bike", "foot", "bus", "train", "truck"
            ])
        
        # Initialize new columns to st
        df['Distance'] = None
        df['Travel Cost'] = None
        
        # Process each row when button is clicked
        if st.button("Calculate Distance & Travel Cost"):

            # Create crews for distance conversion and cost calculation
            distance_crew = Crew(agents=[distance_calculator], tasks=[distance_task], verbose=True)
            cost_crew = Crew(agents=[travel_agent], tasks=[travel_cost_task], verbose=True)

            # Row-wise processing with progress bar
            for idx, row in df.iterrows():
                start_val = row[starting_address_column]
                dest_val = row[destination_address_column] if use_destination_column else fixed_destination_address

                # Get exact distance from tool
                distance_meters = get_city_distance.run(
                    starting_address=start_val,
                    destination_address=dest_val,
                    mode_of_transport=transport_mode
                )

                # Ask LLM to convert distance to km/miles
                converted_distance = distance_crew.kickoff({
                    "starting_address": start_val,
                    "destination_address": dest_val,
                    "distance_in_meters": distance_meters,  # exact number
                    "unit": distance_unit,
                    "mode_of_transport": transport_mode  # pass the mode here
                })

                # 3Calculate travel cost
                travel_cost_result = cost_crew.kickoff({
                    "distance_with_units": str(converted_distance),  # "1345.67 km"
                    "cost_rate": cost_rate_input,
                    "country": "India"
                })

                # Store results
                df.at[idx, "Distance"] = str(converted_distance)
                df.at[idx, "Travel Cost"] = str(travel_cost_result)

            st.success("Processing complete!")

            # ------------------------------
            # Highlight invalid distances
            # ------------------------------
            def highlight_invalid(val):
                if val == "NA":
                    return 'color: red; font-weight:bold'
                return 'color: #32CD32; font-weight:bold'
            # Display results with styling
            st.dataframe(df.style.applymap(highlight_invalid, subset=["Distance"]))

            # Download button for the updated file
            col_button, col_gif = st.columns([4,1])
            with col_button:
                if file_type=='CSV':
                    output_data = df.to_csv(index=False).encode('utf-8')
                    file_name = "City_distances_updated.csv"
                    mime_type = "text/csv" # correct MIME type for CSV
                else:
                    buffer = io.BytesIO()
                    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                        df.to_excel(writer, index=False)
                    output_data = buffer.getvalue()
                    file_name = "City_distances_updated.xlsx"
                    mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                # Download button with correct MIME type and file name
                st.download_button(
                    label="Click to Download",
                    data=output_data,
                    file_name=file_name,
                    mime=mime_type
                )