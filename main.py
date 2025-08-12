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

def fetch_repos(username: str) -> List[Dict[str, Any]]:
    r = gh_get(f'users/{username}/repos', params={'per_page': 100, 'sort': 'updated'})
    if r.status_code != 200:
        raise RuntimeError(f"Failed to fetch repos for {username}: {r.status_code} {r.text}")
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

         # Test repos
        repos = fetch_repos(username)
        print(f"\n=== Repos (showing up to 5 of {len(repos)}) ===")
        for r in repos[:5]:
            print(f"- {r.get('name')}  | ★ {r.get('stargazers_count', 0)}  | Forks {r.get('forks_count', 0)}  | Lang: {r.get('language') or '—'}")

    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    main()