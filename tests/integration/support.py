from __future__ import annotations

import os
import unittest


def required_test_url(name: str) -> str:
    value = (os.getenv(name) or "").strip()
    if not value:
        raise unittest.SkipTest(f"{name} is not configured")
    return value
