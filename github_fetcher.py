from github import Github
from dotenv import load_dotenv
import json
import os
from concurrent.futures import ThreadPoolExecutor
from time import time

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_PRIVATE_TOKEN")

def process_single_repo(repo, output_dir):
    repo_full_name = repo.full_name
    synced_count = 0
    try:
        print(f"⌕  Checking {repo_full_name}")
        
        issues = repo.get_issues(state='closed')
        
        for issue in issues:
            #skip pull requests
            if issue.pull_request:
                print(f"Skipping PR {issue.number} of {repo_full_name}")
                continue
            # Replace '/' with '-' to make a valid filename
            safe_repo_name = repo_full_name.replace("/", "-")
            issue_id = f"GH-{safe_repo_name}-{issue.number}"
            file_name = f"{issue_id}.txt"
            file_path = os.path.join(output_dir, file_name)
            
            content = (
                f"SOURCE: GitHub Issue {repo_full_name} #{issue.number}\n"
                f"URL: {issue.html_url}\n"
                f"TITLE: {issue.title}\n"
                f"CREATED: {issue.created_at}\n"
                f"LABELS: {[l.name for l in issue.labels]}\n\n"
                f"NOTES:\n"
                f"{issue.body if issue.body else 'No description provided.'}"
            )
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            synced_count += 1

    except Exception as e:
        print(f"❌ Error in {repo_full_name}: {e}")
        
    return synced_count
    
    

def fetch_github_issues(output_dir="./input_docs"):

    if not GITHUB_TOKEN:
        print("❌ Error: GITHUB_PRIVATE_TOKEN not found in environment.")
        return

    os.makedirs(output_dir, exist_ok=True)
    start_time = time()
    
    try:
        g = Github(GITHUB_TOKEN)
       
        print("\nᯤ Connecting to GitHub API...")
        user = g.get_user()
        repos = user.get_repos()
        
        repo_list = [r for r in repos]
        
        print(f"\n▷  Starting parallel sync for {len(repo_list)} repositories...\n")
        
        # max_workers=10 will crate 10 threads to process. 
        # DO NOT CHANGE THIS UNLESS YOU KNOW WHAT YOU ARE DOING. 
        # Setting it too high may cause rate limiting or performance issues.
        with ThreadPoolExecutor(max_workers=10) as executor:
            results = list(executor.map(lambda r: process_single_repo(r, output_dir), repo_list))
            
        end_time = time()
        duration = end_time - start_time
        
        total_issues_synced = sum(results)
        print("\n" + "="*30)
        print(f"⏱️  Time taken: {duration:.2f} seconds")
        print(f"✅ Total issues synced across all repos: {total_issues_synced}")
        print("="*30 + "\n")
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    fetch_github_issues("./input_docs")