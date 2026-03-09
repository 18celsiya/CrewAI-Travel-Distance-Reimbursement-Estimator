# main.py
import sys
print("Python executable:", sys.executable)

import streamlit as st
import pandas as pd
import io
from crewai import Crew
from agents import single_trip_agent, distance_calculator, travel_agent
from tasks import conversation_task, distance_task, travel_cost_task
from tools import get_city_distance

# ------------------------------
# Page Config
# ------------------------------
st.set_page_config(
    page_title="Route Distance & Cost Estimator",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ------------------------------
# Custom CSS
# ------------------------------
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

# ------------------------------
# Main Heading
# ------------------------------
st.markdown("""
<div style="display: flex; align-items: center; justify-content: center; gap: 30px;">
    <img src="https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExbzF6b3Vnb2U3Ymh4aGNycGJjYnJhbHpieG16aHp1MWhjcGQ5ZjE1eSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9cw/4T1yKz1IpdcvCi9o6e/giphy.gif" width="60"/>
    <h1>Route Distance & Cost Estimator</h1>
</div>
""", unsafe_allow_html=True)

# ------------------------------
# Mode Selection
# ------------------------------
mode = st.selectbox(
    "Select Calculation Mode:",
    ['Single Trip Between Two Cities', 'Batch Calculation via CSV/Excel']
)

# ------------------------------
# Single Trip Crew
# ------------------------------
if 'conversation_crew' not in st.session_state:
    st.session_state.conversation_crew = Crew(
        agents=[single_trip_agent],
        tasks=[conversation_task],
        verbose=True
    )
conversation_crew = st.session_state.conversation_crew

# ------------------------------
# Single Trip Mode
# ------------------------------
if mode == "Single Trip Between Two Cities":
    st.subheader("💬 Interactive Travel Assistant")

    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []

    # Display previous messages
    for speaker, text in st.session_state.conversation_history:
        if speaker == "You":
            with st.chat_message("user"):
                st.write(text)
        else:
            with st.chat_message("assistant"):
                st.write(text)

    # Chat Input
    user_input = st.chat_input("Ask your questions related to travel or cost")

    if user_input:
        with st.chat_message("user"):
            st.write(user_input)
        st.session_state.conversation_history.append(("You", user_input))

        with st.spinner("Processing..."):
            try:
                result = conversation_crew.kickoff({
                    "user_input": user_input
                })
                response = str(result)
            except Exception as e:
                response = f"Error: {e}"

        with st.chat_message("assistant"):
            st.write(response)
        st.session_state.conversation_history.append(("Assistant", response))

# ------------------------------
# Batch Mode
# ------------------------------
if mode == "Batch Calculation via CSV/Excel":
    file_type = st.selectbox("Select file type:", ['CSV', 'Excel'])
    upload_file = st.file_uploader(f"Upload your {file_type} file:", type=['csv','xlsx'])

    if upload_file:
        df = pd.read_csv(upload_file) if file_type=='CSV' else pd.read_excel(upload_file)
        st.success("File loaded successfully!")

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

            transport_mode = st.selectbox("Mode of transport:", [
                "car", "bike", "foot", "bus", "train", "truck"
            ])

        df['Distance'] = None
        df['Travel Cost'] = None

        if st.button("Calculate Distance & Travel Cost"):

            # --------------------------
            # Create Crews
            # --------------------------
            distance_crew = Crew(agents=[distance_calculator], tasks=[distance_task], verbose=True)
            cost_crew = Crew(agents=[travel_agent], tasks=[travel_cost_task], verbose=True)

            for idx, row in df.iterrows():
                start_val = row[starting_address_column]
                dest_val = row[destination_address_column] if use_destination_column else fixed_destination_address

                # 1️⃣ Get exact distance from tool
                distance_meters = get_city_distance.run(
                    starting_address=start_val,
                    destination_address=dest_val,
                    mode_of_transport=transport_mode
                )

                # 2️⃣ Ask LLM to convert distance to km/miles
                converted_distance = distance_crew.kickoff({
                    "starting_address": start_val,
                    "destination_address": dest_val,
                    "distance_in_meters": distance_meters,  # exact number
                    "unit": distance_unit,
                    "mode_of_transport": transport_mode  # pass the mode here
                })

                # 3️⃣ Calculate travel cost
                travel_cost_result = cost_crew.kickoff({
                    "distance_with_units": str(converted_distance),  # "1345.67 km"
                    "cost_rate": cost_rate_input,
                    "country": "India"
                })

                # 4️⃣ Store results
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

            st.dataframe(df.style.applymap(highlight_invalid, subset=["Distance"]))

            # ------------------------------
            # Download button
            # ------------------------------
            col_button, col_gif = st.columns([4,1])
            with col_button:
                if file_type=='CSV':
                    output_data = df.to_csv(index=False).encode('utf-8')
                    file_name = "City_distances_updated.csv"
                    mime_type = "text/csv"
                else:
                    buffer = io.BytesIO()
                    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                        df.to_excel(writer, index=False)
                    output_data = buffer.getvalue()
                    file_name = "City_distances_updated.xlsx"
                    mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

                st.download_button(
                    label="Click to Download",
                    data=output_data,
                    file_name=file_name,
                    mime=mime_type
                )