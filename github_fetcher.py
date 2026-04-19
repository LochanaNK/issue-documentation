import subprocess
import json
import os
from concurrent.futures import ThreadPoolExecutor
from time import time

def process_single_repo(repo_info, output_dir):
    repo_full_name = repo_info['nameWithOwner']
    synced_count = 0
    try:
        print(f"⌕  Checking {repo_full_name}")
        
        # Fetch closed issues with relevant details using GitHub CLI
        issue_cmd = [
            "gh", "issue", "list",
            "--repo", repo_full_name,
            "--state", "closed",
            "--json", "number,title,body,url,createdAt,labels"
        ]
        
        issue_result = subprocess.run(issue_cmd, capture_output=True, text=True, check=True)
        issues = json.loads(issue_result.stdout)

            # Save each issue
        for issue in issues:
            # Replace '/' with '-' to make a valid filename
            safe_repo_name = repo_full_name.replace("/", "-")
            issue_id = f"GH-{safe_repo_name}-{issue['number']}"
            file_name = f"{issue_id}.txt"
            file_path = os.path.join(output_dir, file_name)
            
            # Removed extra indentation from the f-string for cleaner files
            content = (
                f"SOURCE: GitHub Issue {repo_full_name} #{issue['number']}\n"
                f"URL: {issue['url']}\n"
                f"TITLE: {issue['title']}\n"
                f"CREATED: {issue['createdAt']}\n"
                f"LABELS: {[l['name'] for l in issue['labels']]}\n\n"
                f"NOTES:\n"
                f"{issue['body'] if issue['body'] else 'No description provided.'}"
            )
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            synced_count += 1

    except Exception as e:
        print(f"❌ Error in {repo_full_name}: {e}")
        
    return synced_count
    
    

def fetch_github_issues(output_dir="./input_docs"):

    os.makedirs(output_dir, exist_ok=True)
    start_time = time()
    
    try:
        # Get a list of all repositories for the authenticated user
        repo_cmd = ["gh", "repo", "list", "--limit", "50", "--json", "nameWithOwner"]
        
        result = subprocess.run(repo_cmd, capture_output=True, text=True, check=True, shell=True)
        repos = json.loads(result.stdout)
        
        print(f"\n▷  Starting parallel sync for {len(repos)} repositories...\n")
        
        # max_workers=10 will crate 10 threads to process. 
        # DO NOT CHANGE THIS UNLESS YOU KNOW WHAT YOU ARE DOING. 
        # Setting it too high may cause rate limiting or performance issues.
        with ThreadPoolExecutor(max_workers=10) as executor:
            results = list(executor.map(lambda r: process_single_repo(r, output_dir), repos))
            
        end_time = time()
        duration = end_time - start_time
        
        total_issues_synced = sum(results)
        print(f"\n⏱️  Time taken: {duration:.2f} seconds")
        print(f"✅ Total issues synced across all repos: {total_issues_synced}\n")

    except subprocess.CalledProcessError as e:
        print(f"❌ CLI Error: {e.stderr}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    fetch_github_issues("./input_docs")