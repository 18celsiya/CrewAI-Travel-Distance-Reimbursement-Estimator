# 🚀 AI Travel Distance & Reimbursement Estimator

![Python](https://img.shields.io/badge/Python-3.11-blue)
![CrewAI](https://img.shields.io/badge/Framework-CrewAI-purple)
![Groq](https://img.shields.io/badge/LLM-Groq-orange)
![GraphHopper](https://img.shields.io/badge/Routing-GraphHopper-green)
![Streamlit](https://img.shields.io/badge/UI-Streamlit-red)
![Status](https://img.shields.io/badge/Project-AI%20Agents-success)

An **AI-powered application** that automates travel distance calculation and reimbursement estimation using **AI agents**.

This project demonstrates how **AI agents can orchestrate tools and automate real-world workflows**, replacing manual Excel calculations with intelligent automation.

---

# 📌 Problem Statement

In many organizations, respondents or participants travel from their home to a company location to complete surveys or activities.

The travel reimbursement is often calculated **manually using Excel or CSV files**, which requires:

- Checking the distance between locations
- Converting distance units
- Calculating reimbursement costs

This process can be **time-consuming and repetitive**.

---

# 💡 Solution

This project introduces an **AI agent-based automation system** that:

✔ Calculates distance between locations  
✔ Converts units automatically  
✔ Computes reimbursement cost  
✔ Processes multiple trips from CSV/Excel files  
✔ Provides a conversational assistant for user queries  

All orchestrated using **AI agents working together**.

---

# 🤖 AI Agent Workflow

This project uses **CrewAI** to build a multi-agent system.

### 1️⃣ Conversational Bot Agent
A chatbot-style agent that answers user queries about travel distance and reimbursement cost.

Examples:
- "What is the distance between Chennai and Bangalore?"
- "What will be the reimbursement for 200 km at ₹5 per km?"

The bot understands the request, retrieves the required information, and responds to the user.

---

### 2️⃣ Distance Calculator Agent
- Calls the **GraphHopper Routing API**
- Retrieves travel distance between two locations
- Converts distance to the required unit (km / miles)

### 3️⃣Reimbursement Calculator Agent
- Takes the calculated distance
- Applies **cost per distance unit**
- Calculates the reimbursement amount

These agents collaborate to automate the workflow from  
**distance retrieval → reimbursement calculation**.

---

# 🧠 AI Concepts Implemented

This project demonstrates several **AI agent concepts**:

- Multi-agent collaboration
- Tool calling by agents
- Few-shot prompting to reduce hallucinations
- Short-term memory for conversational context
- Workflow orchestration using agents

---

### Agent Collaboration Workflow

User Input (Travel distance & cost query OR multiple trip calculation via CSV/Excel)

↓  

The Bot Agent analyzes the request and decides which workflow to trigger

↓  

Distance Agent  
• Calls the GraphHopper API  
• Retrieves distance between locations  
• Automatically converts units (km / miles)

↓  

Distance Result

↓  

Reimbursement Agent  
• Extracts numeric distance value  
• Applies cost per unit  
• Calculates reimbursement amount

↓  

Final Result returned to the user

# 🛠 Technologies Used

| Technology | Purpose |
|------------|---------|
| CrewAI | AI agent orchestration |
| Groq | High-speed LLM inference |
| GraphHopper API | Routing engine used to calculate travel distance |
| Streamlit | Web application interface |
| Python | Core programming language |
| Pandas | CSV / Excel data processing |

---

# ✨ Features

### 💬 Conversational Assistant

Users can ask questions like:

```
What is the distance between Chennai and Bangalore?
```

or

```
Calculate reimbursement cost for this trip.
```

---

### 📂 Batch Processing

Upload a **CSV or Excel file** containing multiple trips.

The system automatically:

- Calculates travel distance
- Converts units
- Computes reimbursement cost

---

# 📊 Advantages

Compared to traditional SaaS tools, this approach allows organizations to build **custom internal AI automation**.

Advantages include:

- Uses routing APIs with free tiers instead of relying on expensive services like Google Maps.
- Lower operational cost
- Fully customizable for internal workflows
- Secure API key storage using Streamlit Secrets

---

# ⚠️ Limitations

- If an address is incorrect or incomplete, the system may fail to calculate the distance
- Some small towns or lesser-known locations may not be recognized by the routing service.

---

# 🔮 Future Improvements

Possible improvements for this project:

- Add asynchronous processing for faster CSV batch execution
- Integrate address validation before sending requests to the routing API
- Implement rule-based reimbursement policies based on region or postcode
- Improve error handling for invalid location inputs

---

# 🚀 How to Run the Project

### 1️⃣ Clone the repository

```bash
git clone https://github.com/yourusername/your-repository-name.git
cd your-repository-name
```

### 2️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

### 3️⃣ Add environment variables

Create a `.env` file:

```
GROQ_API_KEY=your_groq_api_key
GRAPHOPPER_API_KEY=your_graphhopper_api_key
```

### 4️⃣ Run the Streamlit application

```bash
streamlit run main.py
```

---


# 👨‍💻 Author

Built as a learning project to explore:

- AI Agents
- Automation workflows
- Tool orchestration with CrewAI

If you have suggestions or feedback, feel free to comment!
