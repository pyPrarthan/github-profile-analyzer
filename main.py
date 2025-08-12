import os
from typing import List, Dict, Any
import requests

# ---------------- API Helpers ----------------
GITHUB_API = "https://api.github.com"

def gh_get(path: str, params: Dict[str, Any] | None = None) -> requests.Response:
    headers = {"Accept": "application/vnd.github+json"}
    token = os.getenv("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    # ensure no accidental double slashes
    path = path.lstrip("/")
    url = f"{GITHUB_API}/{path}"
    return requests.get(url, headers=headers, params=params, timeout=20)

def fetch_user(username: str) -> Dict[str, Any]:
    r = gh_get(f"users/{username}")
    if r.status_code != 200:
        raise RuntimeError(f"Failed to fetch user {username}: {r.status_code} {r.text}")
    return r.json()

def fetch_repos(username: str) -> List[Dict[str, Any]]:
    r = gh_get(f"users/{username}/repos", params={"per_page": 100, "sort": "updated"})
    if r.status_code != 200:
        raise RuntimeError(f"Failed to fetch repos for {username}: {r.status_code} {r.text}")
    return r.json()

# --------------- Language Bytes (accurate) ---------------
def fetch_language_bytes(repos: List[Dict[str, Any]], verbose: bool = False) -> Dict[str, int]:
    totals: Dict[str, int] = {}
    token = os.getenv("GITHUB_TOKEN")
    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    for i, repo in enumerate(repos, start=1):
        url = repo.get("languages_url")
        if not url:
            if verbose: print(f"[{i}] skip: no languages_url for {repo.get('name')}")
            continue
        if verbose: print(f"[{i}] GET {url}")
        try:
            lr = requests.get(url, headers=headers, timeout=20)
            if verbose: print(f"     -> status {lr.status_code}")
            if lr.status_code != 200:
                continue
            data = lr.json()  # {"Python": 12345, "HTML": 6789, ...}
            for lang, size in data.items():
                totals[lang] = totals.get(lang, 0) + int(size)
                if verbose:
                    print(f"        add {lang:<12} +{int(size):>8} (total {totals[lang]})")
        except requests.RequestException as e:
            if verbose: print(f"     !! error: {e}")
            continue

    if not totals:
        totals["Other"] = len(repos)  # fallback
    return totals

# ---------------- Main / Quick Tests ----------------
def main():
    try:
        username = input("Enter GitHub username: ").strip()
        if not username:
            raise ValueError("Username cannot be empty.")

        # Profile summary
        user = fetch_user(username)
        print("\n=== Profile ===")
        print("Login:", user.get("login"))
        print("Name :", user.get("name"))
        print("Bio  :", user.get("bio"))
        print("Followers:", user.get("followers"), " • Following:", user.get("following"))
        print("Public Repos:", user.get("public_repos"))
        print("Profile URL:", user.get("html_url"))

        # Repos preview
        repos = fetch_repos(username)
        print(f"\n=== Repos (showing up to 5 of {len(repos)}) ===")
        for r in repos[:5]:
            print(f"- {r.get('name')}  | ★ {r.get('stargazers_count', 0)}  | Forks {r.get('forks_count', 0)}  | Lang: {r.get('language') or '—'}")

        # Language bytes (ACCURATE aggregation across repos)
        verbose = os.getenv("VERBOSE_LANG", "0") == "1"
        lang_bytes = fetch_language_bytes(repos, verbose=verbose)

        print("\n=== Languages (by code size — LIVE) ===")
        total_bytes = sum(lang_bytes.values()) or 1
        top_langs = sorted(lang_bytes.items(), key=lambda x: x[1], reverse=True)[:10]
        for lang, size in top_langs:
            pct = (size / total_bytes) * 100
            print(f"- {lang:<15} {size:>12} bytes  ({pct:5.1f}%)")

        print("\nDone ✅")

    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    main()
