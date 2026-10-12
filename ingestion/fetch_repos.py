"""Fetch metadata and star/fork counts for the tracked GitHub repositories."""

import os
import tomllib
from pathlib import Path

import requests

REPOS_FILE = Path(__file__).parent / "repos.toml"
API_URL = "https://api.github.com"


def load_repos(path: Path = REPOS_FILE) -> list[tuple[str, str]]:
    """Return (full_name, category) pairs from repos.toml."""
    with open(path, "rb") as f:  # tomllib requires binary mode.
        data = tomllib.load(f)

    result = []
    for category, repos in data["categories"].items():
        for full_name in repos:
            result.append((full_name, category))
    return result


def fetch_repo(session: requests.Session, full_name: str) -> dict:
    """Return the GitHub API response for one repository."""
    response = session.get(f"{API_URL}/repos/{full_name}", timeout=10)
    response.raise_for_status()  # Fail loudly on 4xx/5xx instead of returning an error body.
    return response.json()


def main() -> None:
    # A Session reuses the connection and sends these headers with every request.
    session = requests.Session()
    session.headers.update(
        {
            "Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2026-03-10",
        }
    )

    for full_name, category in load_repos():
        repo = fetch_repo(session, full_name)
        print(
            f"{repo['full_name']:<35} {category:<16} "
            f"stars={repo['stargazers_count']:>7} forks={repo['forks_count']:>6}"
        )


if __name__ == "__main__":
    main()
