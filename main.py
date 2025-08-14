import os
from typing import List, Dict, Any
import requests

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box 

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


def show_dashboard(user: Dict[str, Any], repos: List[Dict[str, Any]], lang_bytes: Dict[str, int]) -> None:
    console = Console()

    #Header panel
    header = f"[bold bright_cyan]{user.get('name') or user['login']}[/] (@{user['login']})"
    sub = f"Followers: {user['followers']} • Following: {user['following']} • Public Repos: {user['public_repos']}"
    bio = user.get("bio") or "—"
    console.print(Panel.fit(f"{header}\n[dim]{sub}[/]\n\n{bio}", border_style="bright_cyan"))

    # Recent repos (up to 10)
    table = Table(title="Repository Highlights", box=box.MINIMAL_DOUBLE_HEAD)
    table.add_column("Name", style="bold")
    table.add_column("★ Stars", justify="right")
    table.add_column("Forks", justify="right")
    table.add_column("Language", style="dim")
    for r in repos[:10]:
        table.add_row(
            r.get("name", "—"),
            str(r.get("stargazers_count", 0)),
            str(r.get("forks_count", 0)),
            str(r.get("language") or "—"),
        )
    console.print(table)

    # Quick stats
    stars_total = sum(r.get("stargazers_count", 0) for r in repos)
    forks_total = sum(r.get("forks_count", 0) for r in repos)
    top_repo = max(repos, key=lambda rr: rr.get("stargazers_count", 0), default=None)

    stats = Table(box=box.SIMPLE_HEAVY)
    stats.add_column("Metric")
    stats.add_column("Value", justify="right")
    stats.add_row("Total Stars", str(stars_total))
    stats.add_row("Total Forks", str(forks_total))
    stats.add_row("Top Repo", top_repo["name"] if top_repo else "—")
    stats.add_row("Top Repo ★", str(top_repo["stargazers_count"]) if top_repo else "—")
    console.print(stats)

    # Language breakdown (percent of total bytes)
    total_bytes = sum(lang_bytes.values()) or 1
    langs_sorted = sorted(lang_bytes.items(), key=lambda x: x[1], reverse=True)[:10]
    langs = Table(title="Languages (by code size)", box=box.SIMPLE)
    langs.add_column("Language")
    langs.add_column("%", justify="right")
    for lang, size in langs_sorted:
        langs.add_row(lang, f"{(size/total_bytes)*100:.1f}")
    console.print(langs)


# ---------------- Main / Quick Tests ----------------
def main():
    try:
        username = input("Enter GitHub username: ").strip()
        if not username:
            raise ValueError("Username cannot be empty.")

        # Fetch profile and repos
        user = fetch_user(username)
        repos = fetch_repos(username)

        # Calculate language usage
        verbose = os.getenv("VERBOSE_LANG", "0") == "1"
        lang_bytes = fetch_language_bytes(repos, verbose=verbose)

        # Show rich dashboard
        show_dashboard(user, repos, lang_bytes)

        print("\nDone ✅")

    except Exception as e:
        print("Error:", e)


if __name__ == "__main__":
    main()
