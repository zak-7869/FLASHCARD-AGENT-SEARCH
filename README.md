# 🗂️ AI Flashcard Agent Engine (LangGraph + Tavily + Groq)

An advanced, full-stack AI Flashcard Generator application featuring a **deterministic multi-step agent workflow**. The application leverages **Tavily Web Search** to gather real-time data from the live internet, pipes it into **Groq Cloud (`llama-3.3-70b-versatile`)** to output perfectly structured educational content, and serves a sleek, responsive single-page 3D flipping card frontend.

Optimised for frictionless one-click deployment directly on **Vercel Serverless Functions**.

---
```
🗺️ System Architecture Flowchart
   [ User Browser (index.html) ] 
       │
       │ (1) User Input: Topic & Count
       ▼
 ┌────────────────────────────────────────────────────────┐
 │ Vercel Serverless Function Host (`main.py`)            │
 │                                                        │
 │   ┌──────────────────────────────────────────────┐     │
 │   │ FastAPI Route Handler: `POST /api/generate`  │     │
 │   └──────────────────────┬───────────────────────┘     │
 │                          │                             │
 │                          ▼ (2) Invokes Graph           │
 │   ┌──────────────────────────────────────────────┐     │
 │   │          LangGraph State Machine             │     │
 │   │                                              │     │
 │   │  [ Entry Point ]                             │     │
 │   │        │                                     │     │
 │   │        ▼                                     │     │
 │   │   ┌───────────────────────────────────────┐  │     │
 │   │   │ Node 1: search_web_node               │  │     │
 │   │   │ ───────────────────────────────────── │  │     │
 │   │   │ Connects to live internet to scrape   │  │     │
 │   │   │ real-time, accurate context data.     │  │     │
 │   │   └──────────────────┬────────────────────┘  │     │
 │   │                      │                       │     │
 │   │                      ▼ (3) State update:     │     │
 │   │                            "search_context"  │     │
 │   │   ┌───────────────────────────────────────┐  │     │
 │   │   │ Node 2: generate_cards_node           │  │     │
 │   │   │ ───────────────────────────────────── │  │     │
 │   │   │ Injects context + applies Pydantic    │  │     │
 │   │   │ structural constraints on LLM output. │  │     │
 │   │   └──────────────────┬────────────────────┘  │     │
 │   │                      │                       │     │
 │   │                      ▼ (4) State update:     │     │
 │   │                            "final_cards"     │     │
 │   │                   [ END ]                    │     │
 │   └──────────────────────┬───────────────────────┘     │
 │                          │                             │
 │                          ▼ (5) Return JSON Response    │
 └──────────────────────────┼─────────────────────────────┘
                            │
                            ▼
[ Client UI renders interactive 3D Flashcards ]


```
## 🚀 Features

- **Agentic State Machine:** Powered by LangGraph to orchestrate step-by-step workflow state transitions (`Search` ➔ `Structure Generation`).
- **Live Internet Access:** Integrated with Tavily Search API to bypass LLM training cutoff limits and pull accurate, current context.
- **Ultra-Fast LLM Processing:** Utilizes Groq's high-throughput `llama-3.3-70b-versatile` engine.
- **Native JSON Enforcement:** Strictly maps responses using Pydantic schemas via LangChain structure utilities.
- **Interactive UX:** Lightweight single-page frontend (`index.html`) featuring fluid 3D card flipping CSS transforms.
- **Vercel-Ready Architecture:** Clean layout configurations configured specifically for serverless deployment constraints.

---

## 📂 Project Structure

```text
├── .env                 # Local environment/credential keys (ignored by git)
├── requirements.txt     # Python backend dependencies
├── vercel.json          # Deployment & routing configurations for Vercel
├── main.py              # FastAPI server & LangGraph workflow logic
└── index.html           # Single-page interactive frontend layout
```

---

## 🛠️ Local Installation & Development

Follow these steps to run the application locally on your machine:

### 1. Clone the Project Workspace
```bash
mkdir flashcard-agent-app && cd flashcard-agent-app
# (Move your main.py, index.html, vercel.json, and requirements.txt files here)
```

### 2. Set Up a Virtual Environment
```bash
python -bin -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Your Credentials
Create a `.env` file in the root folder:
```env
GROQ_API_KEY=gsk_your_actual_groq_api_key_here
TAVILY_API_KEY=tvly-your_actual_tavily_api_key_here
```

### 5. Start the Server Instance
```bash
python main.py
```
Open your browser and navigate to **`http://127.0.0.1:8000`**.

---

## ☁️ Deploying to Vercel

This repository is pre-configured for Vercel Serverless Functions out-of-the-box.

### Method A: Using Vercel CLI
1. Install the CLI tool globally: `npm i -g vercel`
2. Run deployment setup: `vercel`
3. Add your Environment Keys in your Vercel Dashboard under **Settings > Environment Variables**.

### Method B: Git Integration
1. Push your code workspace to a **GitHub/GitLab** repository.
2. Link the repository directly inside the Vercel Web Dashboard.
3. Add your Environment variables (`GROQ_API_KEY` and `TAVILY_API_KEY`) under project configurations.
4. Click **Deploy**.

---

## ⚙️ How It Works (The Graph State Routing)

1. **User Request (`POST /api/generate`):** Receives the core query topic and target flashcard volume count.
2. **`search_web_node` (Tavily Engine):** Connects to the web to retrieve live content snippets and raw educational facts.
3. **`generate_cards_node` (Groq Engine):** Validates raw reference context against strict JSON interfaces, generating distinct `front` prompts and `back` contextual answers.
4. **Client Render:** Emits uniform data collections directly to the browser UI.

---

## 📄 License
This project is open-source and free for all personal and commercial educational uses.
