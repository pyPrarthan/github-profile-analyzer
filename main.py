import os 
from typing import List, Dict, Any, Tuple
import requests

# API Helpers 
GITHUB_API = 'https://api.github.com'

def gh_get(path: str, params: Dict[str, Any] | None = None) -> requests.Response:
    headers = {"Accept": "application/vnd.github+json"}
    token = os.getenv('GITHUB_TOKEN')
    if token:
        headers['Authorization'] = f'Bearer {token}'
    url = f"{GITHUB_API}/{path}"
    return requests.get(url, headers=headers, params=params, timeout=20)

def fetch_user(username: str) -> Dict[str, Any]:
    r = gh_get(f'users/{username}')
    if r.status_code != 200:
        raise RuntimeError(f"Failed to fetch user {username}: {r.status_code} {r.text}")
    return r.json()
    

def main():
    try:
        username = input("Enter GitHub username: ").strip()
        user = fetch_user(username)
        # minimal pretty print
        print("\n=== Profile ===")
        print("Login:", user.get("login"))
        print("Name :", user.get("name"))
        print("Bio  :", user.get("bio"))
        print("Followers:", user.get("followers"), " • Following:", user.get("following"))
        print("Public Repos:", user.get("public_repos"))
        print("Profile URL:", user.get("html_url"))
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    main()