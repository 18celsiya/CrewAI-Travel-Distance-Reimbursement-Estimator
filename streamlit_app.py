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
    page_title="AI-Powered Route Distance & Travel Reimbursement Estimator",
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
    <h1>AI-Powered Route Distance & Travel Reimbursement Estimator</h1>
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

# ===============================================
# Single Trip Chat - Streamlit
# ===============================================
if mode == 'Single Trip Between Two Cities':
    # Initialize conversation history in session_state
    if "conversation_history" not in st.session_state:
        st.session_state.conversation_history = []

    # User input box
    user_input = st.chat_input("Ask a question about travel or distance")

    if user_input:
        # Append user message as dictionary
        st.session_state.conversation_history.append({"role": "user", "content": user_input})

        # Call the agent with user_input and conversation context
        with st.spinner("Processing..."):
            try:
                result_obj = conversation_crew.kickoff({
                    "user_input": user_input,
                    "conversation_history": st.session_state.conversation_history
                })
                response = str(result_obj)
            except Exception as e:
                response = f"Error: {e}"

        # Append assistant response
        st.session_state.conversation_history.append({"role": "assistant", "content": response})

    # Display conversation in order
    for msg in st.session_state.conversation_history:
        # Convert old tuple entries to dictionary format if present
        if isinstance(msg, tuple):
            role = "user" if msg[0] == "You" else "assistant"
            content = msg[1]
            msg = {"role": role, "content": content}

        with st.chat_message(msg["role"]):
            st.write(msg["content"])
# =========================================================
# Batch Calculation via CSV/Excel
# =========================================================

if mode == "Multiple trips calculation via CSV/Excel":

    file_type = st.selectbox("Select file type:", ['CSV', 'Excel'])

    upload_file = st.file_uploader(
        f"Upload your {file_type} file:",
        type=['csv', 'xlsx']
    )

    if upload_file:

        df = pd.read_csv(upload_file) if file_type == 'CSV' else pd.read_excel(upload_file)

        st.success("File loaded successfully!")

        col1, col2 = st.columns(2)

        with col1:

            starting_address_column = st.selectbox(
                "Select column for starting address:",
                df.columns
            )

            distance_unit = st.selectbox(
                'Distance unit:',
                ['km', 'miles']
            ).lower()

            cost_rate_input = st.text_input(
                "Reimbursement cost per unit distance:",
                value="200"
            )

        with col2:

            destination_option = st.radio(
                "Destination address option:",
                ['Single Fixed Address', 'Select Column from File']
            )

            if destination_option == 'Single Fixed Address':

                fixed_destination_address = st.text_input(
                    "Enter destination address:",
                    value="Chennai"
                )

                use_destination_column = False

            else:

                destination_address_column = st.selectbox(
                    "Select column for destination address:",
                    df.columns
                )

                use_destination_column = True

            transport_mode = st.selectbox(
                "Mode of transport:",
                ["car", "bike", "foot", "bus", "train", "truck"]
            )


        df['Distance'] = None
        df['Reimbursement Amount'] = None


        if st.button("Calculate Distance & Reimbursement"):

            distance_crew = Crew(
                agents=[distance_calculator],
                tasks=[distance_task],
                verbose=True
            )

            cost_crew = Crew(
                agents=[travel_agent],
                tasks=[travel_cost_task],
                verbose=True
            )

            progress_bar = st.progress(0)

            total_rows = len(df)

            for idx, row in df.iterrows():

                progress_bar.progress((idx + 1) / total_rows)

                start_val = row[starting_address_column]

                dest_val = row[destination_address_column] if use_destination_column else fixed_destination_address

                distance_meters = get_city_distance.run(
                    starting_address=start_val,
                    destination_address=dest_val,
                    mode_of_transport=transport_mode
                )

                if distance_meters is None:

                    df.at[idx, "Distance"] = "NA"
                    df.at[idx, "Reimbursement Amount"] = "NA"
                    continue


                converted_distance = distance_crew.kickoff({
                    "starting_address": start_val,
                    "destination_address": dest_val,
                    "distance_in_meters": distance_meters,
                    "unit": distance_unit,
                    "mode_of_transport": transport_mode
                })


                reimbursement_result = cost_crew.kickoff({
                    "distance_with_units": str(converted_distance),
                    "cost_rate": cost_rate_input,
                    "country": "India"
                })


                df.at[idx, "Distance"] = str(converted_distance)
                df.at[idx, "Reimbursement Amount"] = str(reimbursement_result)


            st.success("Processing complete!")


            # =========================================================
            # Travel Reimbursement Summary
            # =========================================================

            total_trips = len(df)

            total_distance = df["Distance"]\
                .str.extract(r'([\d\.]+)')[0]\
                .astype(float)\
                .sum()

            total_cost = df["Reimbursement Amount"]\
                .str.replace(r'[^\d.]', '', regex=True)\
                .astype(float)\
                .sum()


            st.markdown("### Travel Reimbursement Summary")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Total Trips", total_trips)

            with col2:
                st.metric(
                    "Total Distance",
                    f"{round(total_distance,2)} {distance_unit}"
                )

            with col3:
                st.metric(
                    "Total Reimbursement",
                    f"₹{round(total_cost,2)}"
                )


            # =========================================================
            # Show Table
            # =========================================================

            st.dataframe(df)


            # =========================================================
            # Download Updated File
            # =========================================================

            if file_type == 'CSV':

                output_data = df.to_csv(index=False).encode('utf-8')

                st.download_button(
                    label="Download Results",
                    data=output_data,
                    file_name="reimbursement_results.csv",
                    mime="text/csv"
                )

            else:

                buffer = io.BytesIO()

                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False)

                st.download_button(
                    label="Download Results",
                    data=buffer.getvalue(),
                    file_name="reimbursement_results.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )