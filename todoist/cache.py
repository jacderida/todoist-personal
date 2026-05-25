"""Persistent on-disk cache for slow, rarely-changing API lookups.

The sync scripts invoke the CLI once per project (13-14 times), and each
invocation is a fresh process. That means any in-memory caching (including the
linear_api client's own) is thrown away between runs, so every invocation
re-fetches the same Linear teams/projects and Todoist projects. These lists
rarely change, so we cache them to disk and reuse them within a TTL.

Usage:

    from todoist import cache

    projects = cache.cached_fetch(
        f"linear_projects_{team_name}",
        lambda: linear_client.projects.get_all(team_id=team.id),
        no_cache=no_cache,
    )

Any read/deserialisation error is treated as a cache miss, so a stale or
corrupt cache file can never break a sync - it just triggers a fresh fetch.
"""

import os
import pickle
import time

# Project lists rarely change; default expiry is 7 days.
DEFAULT_TTL_SECONDS = 7 * 24 * 60 * 60


def _cache_dir():
    path = os.path.join(
        os.environ["HOME"], ".local", "share", "todoist-personal", "cache"
    )
    if not os.path.exists(path):
        os.makedirs(path)
    return path


def _cache_path(key):
    # Keep keys filesystem-safe (team/project names may contain spaces, dots, etc.).
    safe_key = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in key)
    return os.path.join(_cache_dir(), f"{safe_key}.pkl")


def _read(key, ttl_seconds):
    """Return the cached value for key if present and fresh, else None."""
    path = _cache_path(key)
    try:
        with open(path, "rb") as f:
            entry = pickle.load(f)
        if time.time() - entry["timestamp"] <= ttl_seconds:
            return entry["value"]
    except Exception:
        # Missing file, corrupt data, or schema change -> treat as a miss.
        return None
    return None


def _write(key, value):
    path = _cache_path(key)
    try:
        with open(path, "wb") as f:
            pickle.dump({"timestamp": time.time(), "value": value}, f)
    except Exception:
        # Caching is best-effort; never let a write failure break a sync.
        pass


def cached_fetch(key, fetch_fn, no_cache=False, ttl_seconds=DEFAULT_TTL_SECONDS):
    """Return a cached value for key, or fetch, store, and return a fresh one.

    Args:
        key: Stable identifier for the cached value (e.g. "todoist_projects").
        fetch_fn: Zero-argument callable that fetches the value from the API.
        no_cache: When True, bypass the cache read and force a fresh fetch
            (the result is still written back to refresh the cache).
        ttl_seconds: Maximum age of a cache entry before it is considered stale.
    """
    if not no_cache:
        cached = _read(key, ttl_seconds)
        if cached is not None:
            return cached

    value = fetch_fn()
    _write(key, value)
    return value
