# Agentic AI Workflow Chatbot Backend

## Task Description
This project was developed as part of a placement assignment.  
The objective is to build a Python backend that implements an **Agentic AI workflow chatbot**, where the AI can intelligently reason, decide which tools to use, fetch data, and generate accurate responses.

The system follows an **agent-based architecture** with multiple specialized agents that collaborate to answer user queries.

---

## Agentic Flow Architecture

User Query  
↓  
AI Reasoning Agent  
↓  
Tool Decision  
- Weather Tool  
- Document QA Tool  
- Web Search Tool  
- Database Tool  
↓  
Action Execution  
↓  
Final Response Generation  

---

## Implemented Agents

### 1️⃣ Weather Intelligence Agent
Uses the **OpenWeatherMap API** to answer natural language weather queries.

**Example queries:**
- What is the weather in Chennai today?
- What was the weather in Bengaluru yesterday?
- What will the weather be like in London tomorrow?

---

### 2️⃣ Document Understanding + Web Intelligence Agent
- Allows users to upload a document (PDF / Text).
- Answers questions strictly based on document content.
- If the answer is **not present in the document**, the agent intelligently redirects the query to a web search and provides a valid response.

**Example:**
- "What is the leave policy?" → Answered from document  
- "Who is the CEO of Google?" → Identified as not in document and answered via web search

---

### 3️⃣ Meeting Scheduling + Weather Reasoning Agent
Handles complex multi-step reasoning.

**Workflow:**
1. Checks tomorrow’s weather using the Weather Intelligence Agent  
2. Logically determines whether the weather is good or bad  
3. Connects to the database  
4. Checks if a meeting is already scheduled  
5. Creates a meeting if none exists  
6. If already scheduled, responds with reasoning  

**Example query:**
- "Verify tomorrow’s weather and schedule a team meeting if the weather is good."

---

### 4️⃣ Natural Language → Database Query Agent
Converts natural language queries into database queries and returns results.

**Example queries:**
- Show all meetings scheduled tomorrow
- Do we have any meetings today?
- List meetings next week
- Is there any review meeting?

---

## Tech Stack
- Python
- FastAPI
- LangChain / Agentic Framework
- OpenWeatherMap API
- SQL-based Database (SQLite / PostgreSQL)

---

## Setup Instructions

### 1️⃣ Clone the repository
```bash
git clone https://github.com/DineshK-18/agentic-chatbot.git
cd agentic-chatbot
