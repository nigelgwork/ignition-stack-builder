"""
Docker Hub API integration for fetching available image tags
"""
import requests
from typing import List, Optional
from functools import lru_cache
import re


@lru_cache(maxsize=128)
def get_docker_tags(repository: str, limit: int = 100) -> List[str]:
    """
    Fetch available tags for a Docker Hub repository

    Args:
        repository: Docker repository name (e.g., 'inductiveautomation/ignition')
        limit: Maximum number of tags to fetch

    Returns:
        List of tag names
    """
    try:
        url = f"https://hub.docker.com/v2/repositories/{repository}/tags"
        params = {"page_size": limit, "ordering": "-name"}

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()
        tags = [tag["name"] for tag in data.get("results", [])]

        return tags
    except Exception as e:
        print(f"Error fetching Docker tags for {repository}: {e}")
        return []


def get_ignition_versions() -> List[str]:
    """
    Get available Ignition versions from Docker Hub, sorted and filtered

    Returns:
        List of version strings starting with 'latest', then sorted by version
    """
    all_tags = get_docker_tags("inductiveautomation/ignition", limit=200)

    # Filter for version tags (8.x.x format)
    version_pattern = re.compile(r'^8\.\d+\.\d+$')
    versions = [tag for tag in all_tags if version_pattern.match(tag)]

    # Sort versions (newest first)
    def version_key(v):
        parts = v.split('.')
        return (int(parts[0]), int(parts[1]), int(parts[2]))

    versions.sort(key=version_key, reverse=True)

    # Add 'latest' at the beginning
    return ['latest'] + versions[:20]  # Limit to 20 most recent versions


def get_postgres_versions() -> List[str]:
    """Get available PostgreSQL versions"""
    all_tags = get_docker_tags("library/postgres", limit=100)

    # Filter for version tags and alpine variants
    version_pattern = re.compile(r'^(\d+)(-alpine)?$')
    versions = [tag for tag in all_tags if version_pattern.match(tag)]

    return ['latest'] + versions[:15]
