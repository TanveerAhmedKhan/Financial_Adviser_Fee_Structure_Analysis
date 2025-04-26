import requests
import json
import os
from getpass import getpass

def list_github_repos(username, token=None):
    """
    List all repositories for a GitHub user
    
    Args:
        username (str): GitHub username
        token (str, optional): GitHub personal access token for authentication
    
    Returns:
        list: List of repository names
    """
    # Base URL for GitHub API
    base_url = f"https://api.github.com/users/{username}/repos"
    
    # Headers for authentication if token is provided
    headers = {}
    if token:
        headers["Authorization"] = f"token {token}"
    
    # Parameters for pagination
    params = {
        "per_page": 100,  # Maximum allowed by GitHub API
        "page": 1
    }
    
    all_repos = []
    
    while True:
        # Make the API request
        response = requests.get(base_url, headers=headers, params=params)
        
        # Check if the request was successful
        if response.status_code != 200:
            print(f"Error: {response.status_code}")
            print(response.json().get("message", "Unknown error"))
            break
        
        # Parse the response
        repos = response.json()
        
        # If no repositories were returned, we've reached the end
        if not repos:
            break
        
        # Add the repositories to our list
        all_repos.extend(repos)
        
        # Move to the next page
        params["page"] += 1
    
    # Extract repository names
    repo_names = [repo["name"] for repo in all_repos]
    
    return repo_names, all_repos

def main():
    # Get GitHub username
    username = input("Enter your GitHub username: ")
    
    # Ask if the user wants to use authentication
    use_auth = input("Do you want to use authentication for higher rate limits? (y/n): ").lower() == 'y'
    
    token = None
    if use_auth:
        # Try to get token from environment variable first
        token = os.environ.get("GITHUB_TOKEN")
        
        # If not found in environment, prompt the user
        if not token:
            token = getpass("Enter your GitHub personal access token (input will be hidden): ")
    
    # Get the repositories
    repo_names, repos = list_github_repos(username, token)
    
    # Print the repository names
    print(f"\nFound {len(repo_names)} repositories for user {username}:")
    for i, name in enumerate(repo_names, 1):
        print(f"{i}. {name}")
    
    # Ask if the user wants to save detailed information
    save_details = input("\nDo you want to save detailed information about the repositories? (y/n): ").lower() == 'y'
    
    if save_details:
        # Create a more detailed report
        with open("github_repos_details.json", "w") as f:
            json.dump(repos, f, indent=2)
        print("Detailed information saved to github_repos_details.json")
        
        # Create a CSV with key information
        import csv
        with open("github_repos_summary.csv", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Name", "Description", "Language", "Stars", "Forks", "Created", "Last Updated", "URL"])
            
            for repo in repos:
                writer.writerow([
                    repo["name"],
                    repo["description"] or "",
                    repo["language"] or "",
                    repo["stargazers_count"],
                    repo["forks_count"],
                    repo["created_at"],
                    repo["updated_at"],
                    repo["html_url"]
                ])
        print("Summary information saved to github_repos_summary.csv")

if __name__ == "__main__":
    main()
