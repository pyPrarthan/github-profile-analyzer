# GitHub Profile Analyzer (Python) 🔍

A colorful CLI tool that fetches a GitHub user’s profile, aggregates repository stats, and shows an accurate language breakdown by **code size**. Built with `requests` + `rich`.

> Perfect for showcasing API work, data aggregation, and CLI UI on your GitHub.

---

## ✨ Features

- **Profile summary**: name, bio, followers, public repos  
- **Repo highlights**: most recently updated repos with ⭐ stars, forks, language  
- **Accurate language usage**: aggregates bytes from each repo’s `languages_url`  
- **Pretty CLI**: `rich` panels and tables for a clean dashboard  
- **Optional verbose mode** for learning/debugging

---

## 📸 Demo

Run the tool and you’ll see a dashboard like:

```
┌ GitHub User (@username) ┐
│ followers • following • public repos
│ bio...
└─────────────────────────┘

Repository Highlights
Name                ★ Stars   Forks   Language
...

Quick Stats
Metric              Value
Total Stars         123
Total Forks         45
Top Repo            cool-project
Top Repo ★          67

Languages (by code size)
Language            %
Python              62.4
TypeScript          21.7
JavaScript          9.8
...
```

*(Optional) Add a screenshot later: `docs/demo.png`)*

---

## 🚀 Quick Start

### 1) Clone & install
```bash
git clone https://github.com/pyPrarthan/github-profile-analyzer.git
cd github-profile-analyzer
pip install -r requirements.txt
```

---

### 2) (Optional) Set a GitHub token
Unauthenticated requests are limited to **60/hour**. With a token you get **5000/hour**.

- macOS/Linux:
  ```bash
  export GITHUB_TOKEN=YOUR_TOKEN
  ```
- Windows (PowerShell):
  ```powershell
  $env:GITHUB_TOKEN="YOUR_TOKEN"
  ```

No special scopes needed for public data.

---

### 3) Run
```bash
python main.py
```
Enter any public GitHub username (e.g., `torvalds`, `microsoft`, or your own).

---

## ⚙️ Environment Variables

- `GITHUB_TOKEN` (optional) – raises your rate limit from 60/hr to 5000/hr.
- `VERBOSE_LANG=1` (optional) – prints each `languages_url` request and how bytes are accumulated.

Example:
```bash
VERBOSE_LANG=1 python main.py
```

---

## 🧠 How It Works

- `GET /users/{username}` → profile details  
- `GET /users/{username}/repos?per_page=100&sort=updated` → list repos  
- For each repo: `GET {languages_url}` → `{ "Python": 12345, "HTML": 6789, ... }`  
- Sum bytes per language across all repos → show percentages  
- Render everything via `rich` tables/panels

---

## 📁 Project Structure

```
.
├─ main.py                # CLI entrypoint
├─ requirements.txt       # (optional) requests, rich
├─ README.md
```

---

## 🛠 Troubleshooting

- **403 or rate limit errors**: set `GITHUB_TOKEN` as shown above.  
- **Blank language table**: user may have no public code or requests failed; try again with a token.  
- **Slow on large accounts**: this makes one `languages_url` call per repo; that’s expected.

