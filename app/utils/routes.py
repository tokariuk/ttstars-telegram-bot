from __future__ import annotations


def normalize_route_path(path: str) -> str:
    return path if path.startswith("/") else f"/{path}"
