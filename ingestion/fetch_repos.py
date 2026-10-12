"""Fetch metadata and star/fork counts for the tracked GitHub repositories."""

import logging
import os
import tomllib
from pathlib import Path

import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

REPOS_FILE = Path(__file__).parent / "repos.toml"
API_URL = "https://api.github.com"

logger = logging.getLogger(__name__)


class LoggingRetry(Retry):
    """urllib3 Retry that logs every retry attempt."""

    def increment(self, method=None, url=None, response=None, error=None, *args, **kwargs):
        reason = response.status if response is not None else repr(error)
        logger.warning("Retrying %s %s (reason: %s)", method, url, reason)
        return super().increment(method, url, response, error, *args, **kwargs)


def build_session(token: str) -> requests.Session:
    """Return a Session with GitHub auth headers and automatic retries."""
    session = requests.Session()
    session.headers.update(
        {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2026-03-10",
        }
    )

    retry = LoggingRetry(
        total=5,
        backoff_factor=1,  # Waits 0, 2, 4, 8 seconds between attempts.
        status_forcelist=[429, 500, 502, 503, 504],  # Only transient errors.
        raise_on_status=False,  # Let raise_for_status() report the final error.
    )
    session.mount("https://", HTTPAdapter(max_retries=retry))
    return session


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
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    session = build_session(os.environ["GITHUB_TOKEN"])
    repos = load_repos()
    logger.info("Fetching %d repositories", len(repos))

    for full_name, category in repos:
        repo = fetch_repo(session, full_name)
        logger.info(
            "%-35s %-16s stars=%7d forks=%6d",
            repo["full_name"],
            category,
            repo["stargazers_count"],
            repo["forks_count"],
        )

    logger.info("Done")


if __name__ == "__main__":
    main()
