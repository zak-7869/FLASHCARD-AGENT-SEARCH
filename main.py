import os
from typing import List, Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# LangGraph, Groq, and Tavily imports
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from langchain_tavily import TavilySearch
from langchain_core.messages import HumanMessage, SystemMessage

# Load variables
load_dotenv()
if not os.environ.get("GROQ_API_KEY") or not os.environ.get("TAVILY_API_KEY"):
    raise ValueError("CRITICAL: Both GROQ_API_KEY and TAVILY_API_KEY must be configured in .env.")

app = FastAPI(title="AI Flashcard Agent with LangGraph, Tavily & Groq")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------------------------------
# Pydantic Schemas for Structured JSON IO
# ----------------------------------------------------
class Flashcard(BaseModel):
    front: str = Field(description="The core question, concept, or term.")
    back: str = Field(description="The exact explanation, summary, or fact checked answer.")

class FlashcardList(BaseModel):
    cards: List[Flashcard]

class GenerationRequest(BaseModel):
    topic: str
    count: int = 5

# ----------------------------------------------------
# LangGraph Workflow Architecture
# ----------------------------------------------------
class GraphState(TypedDict):
    topic: str
    count: int
    search_context: str
    final_cards: List[Dict[str, str]]

def search_web_node(state: GraphState) -> Dict[str, Any]:
    """Node 1: Executes an live web query using Tavily to fetch up-to-date context."""
    print(f"[Node: Search] Researching query: {state['topic']} via Tavily...")
    try:
        tavily_client = TavilySearch(max_results=3)
        search_results = tavily_client.invoke(state['topic'])
        
        # Compile raw snippets and text chunks into a unified string context
        context_str = ""
        if isinstance(search_results, list):
            for res in search_results:
                context_str += f"Source: {res.get('url','')}\nContent: {res.get('content','')}\n\n"
        else:
            context_str = str(search_results)
            
        return {"search_context": context_str}
    except Exception as e:
        print(f"Search warning/fallback triggered: {str(e)}")
        return {"search_context": "No live internet data retrieved. Proceed with default knowledge."}

def generate_flashcards_node(state: GraphState) -> Dict[str, Any]:
    """Node 2: Consumes search context data to output structurally formatted cards."""
    print("[Node: Generator] Transforming retrieved source facts into structured JSON via Groq...")
    
    # Utilizing ultra-fast llama-3.3-70b-versatile for structured serialization
    llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0.2)
    structured_llm = llm.with_structured_output(FlashcardList)
    
    system_instruction = (
        "You are an elite educational parsing engine. Your goal is to review a given topic "
        "alongside real-time internet search results, extract structural facts, and output educational flashcards. "
        "Each card front must be a prompt or concise concept question, and the back must be a clear summary answer."
    )
    
    user_prompt = (
        f"Topic: {state['topic']}\n"
        f"Requested Count: {state['count']}\n"
        f"Live Reference Data:\n{state['search_context']}\n\n"
        f"Generate exactly {state['count']} high-quality flashcards reflecting the latest data."
    )
    
    try:
        response: FlashcardList = structured_llm.invoke([
            SystemMessage(content=system_instruction),
            HumanMessage(content=user_prompt)
        ])
        
        cards_dict = [card.model_dump() for card in response.cards]
        return {"final_cards": cards_dict}
    except Exception as e:
        raise RuntimeError(f"JSON schema parsing failed inside LLM: {str(e)}")

# Initialize the StateGraph
workflow = StateGraph(GraphState)

# Append Nodes
workflow.add_node("search_web", search_web_node)
workflow.add_node("generate_cards", generate_flashcards_node)

# Map Edges (Deterministic path: Start -> Search -> Generate -> Complete)
workflow.set_entry_point("search_web")
workflow.add_edge("search_web", "generate_cards")
workflow.add_edge("generate_cards", END)

# Compile into functional runtime middleware agent
agent_graph = workflow.compile()

# ----------------------------------------------------
# FastAPI Routing Endpoints
# ----------------------------------------------------
@app.post("/api/generate")
async def generate_cards_endpoint(payload: GenerationRequest):
    """Triggers execution of the combined search/generation graph."""
    try:
        initial_state = {
            "topic": payload.topic,
            "count": payload.count,
            "search_context": "",
            "final_cards": []
        }
        
        output_state = await agent_graph.ainvoke(initial_state)
        return {"cards": output_state.get("final_cards", [])}
    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err))

@app.get("/")
def serve_index():
    """Serves index.html directly from local directory pathing."""
    if os.path.exists("index.html"):
        return FileResponse("index.html")
    return {"status": "Backend running, but index.html was not found in this folder."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
