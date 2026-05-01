from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from processor import run_processor
from github_fetcher import fetch_github_issues
from gitlab_fetcher import fetch_gitlab_issues
from jira_fetcher import fetch_jira_issues
from search import search_issues
import asyncio

app = FastAPI(title="DevDoc API server")
is_syncing = False


#CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SearchRequest(BaseModel):
    query: str
    limit: int
    
@app.post("/sync")
async def sync_docs(background_tasks: BackgroundTasks):
    global is_syncing
    
    if is_syncing:
        return {"status": "Busy", "details": "A sync is already in progress."}
    
    def run_pipeline():
        global is_syncing
        input_dir= "./input_docs"
        
        try:
            is_syncing = True
            fetch_gitlab_issues(output_dir=input_dir)
            fetch_github_issues(output_dir=input_dir)
            fetch_jira_issues(output_dir=input_dir)
            
            run_processor()
        finally:
            is_syncing = False
                    
                    
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

