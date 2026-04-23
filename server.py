from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from processor import run_processor
from github_fetcher import fetch_github_issues
from search import search_issues

app = FastAPI(title="DevDoc API server")


#CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], # Next.js default port
    allow_credentials=True,
    allow_methods=["*"], # Allows POST, GET, OPTIONS, etc.
    allow_headers=["*"], # Allows Content-Type, Authorization, etc.
)


class SearchRequest(BaseModel):
    query: str
    limit: int
    
@app.post("/sync")
async def sync_docs(background_tasks: BackgroundTasks):
    
    def run_pipeline():
        input_dir= "./input_docs"
        
        # fetch_github_issues(output_dir=input_dir)
        
        run_processor()
                    
                    
    background_tasks.add_task(run_pipeline)
    return {"status": "Syncing", "details": "Issue fetch and LLM processing started."}

@app.post("/search")
async def search(request: SearchRequest):
    
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Search query cannot be empty.")
    
    results = search_issues(
        query_text=request.query, 
        n_results=request.limit, 
    )
    
    return {"results": results}

