import gitlab
import os
import json
from concurrent.futures import ThreadPoolExecutor
from time import time

# Use the token from your environment variables (Safe for Docker/PC)
GITLAB_TOKEN = os.getenv("GITLAB_PRIVATE_TOKEN")

def process_single_gitlab_project(project, output_dir):
    """Processes a single GitLab project and saves closed issues as text files."""
    synced_count = 0
    project_full_name = project.path_with_namespace
    
    try:
        print(f"⌕  Checking GitLab: {project_full_name}")
        
        # Fetch closed issues for this specific project
        # get_all=True handles pagination automatically
        issues = project.issues.list(state='closed', get_all=True)

        for issue in issues:
            # Create a safe filename (GitLab issues use iid for the number)
            safe_name = project_full_name.replace("/", "-")
            issue_id = f"GL-{safe_name}-{issue.iid}"
            file_name = f"{issue_id}.txt"
            file_path = os.path.join(output_dir, file_name)

            # Format content to match your GitHub style exactly
            content = (
                f"SOURCE: GitLab Issue {project_full_name} #{issue.iid}\n"
                f"URL: {issue.web_url}\n"
                f"TITLE: {issue.title}\n"
                f"CREATED: {issue.created_at}\n"
                f"LABELS: {issue.labels}\n\n"
                f"NOTES:\n"
                f"{issue.description if issue.description else 'No description provided.'}"
            )

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            synced_count += 1

    except Exception as e:
        print(f"❌ Error in GitLab Project {project_full_name}: {e}")
        
    return synced_count

def fetch_gitlab_issues(output_dir="./input_docs"):
    """Fetches closed issues from all GitLab projects in parallel."""
    if not GITLAB_TOKEN:
        print("❌ Error: GITLAB_PRIVATE_TOKEN not found in environment.")
        return

    os.makedirs(output_dir, exist_ok=True)
    start_time = time()
    
    try:
        gl = gitlab.Gitlab('https://gitlab.com', private_token=GITLAB_TOKEN)
        
        print("📡 Connecting to GitLab API...")
        projects = gl.projects.list(membership=True, limit=50)
        
        print(f"\n▷  Starting parallel GitLab sync for {len(projects)} projects...\n")
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            results = list(executor.map(lambda p: process_single_gitlab_project(p, output_dir), projects))
            
        end_time = time()
        duration = end_time - start_time
        
        total_issues_synced = sum(results)
        print("\n" + "="*40)
        print(f"⏱️  GitLab Sync: {duration:.2f} seconds")
        print(f"✅ Total GitLab issues synced: {total_issues_synced}")
        print("="*40 + "\n")

    except Exception as e:
        print(f"❌ Unexpected GitLab error: {e}")

if __name__ == "__main__":
    fetch_gitlab_issues("./input_docs")