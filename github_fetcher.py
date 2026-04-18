import subprocess
import json
import os

def fetch_github_issues(output_dir="./input_docs"):

    os.makedirs(output_dir, exist_ok=True)
    
    try:
        # 1. Get a list of all repositories for the authenticated user
        repo_cmd = ["gh", "repo", "list", "--limit", "50", "--json", "nameWithOwner"]
        
        result = subprocess.run(repo_cmd, capture_output=True, text=True, check=True, shell=True)
        repos = json.loads(result.stdout)
        
        total_issues_synced = 0

        # 2. Loop through each repository found
        for repo_info in repos:
            repo_full_name = repo_info['nameWithOwner']
            print(f":) Checking {repo_full_name}")

            issue_cmd = [
                "gh", "issue", "list",
                "--repo", repo_full_name,
                "--state", "open",
                "--json", "number,title,body,url,createdAt,labels"
            ]
            
            issue_result = subprocess.run(issue_cmd, capture_output=True, text=True, check=True)
            issues = json.loads(issue_result.stdout)

            # 3. Save each issue
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
                
                total_issues_synced += 1

        print(f"\n✅ Total issues synced across all repos: {total_issues_synced}")

    except subprocess.CalledProcessError as e:
        print(f"❌ CLI Error: {e.stderr}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    # Fixed: Passed the required directory argument
    fetch_github_issues("./input_docs")