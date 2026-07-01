"""Django settings for running the Shard test suite."""

from pathlib import Path

from example.example.settings import *  # noqa: F403

TESTS_DIR = Path(__file__).resolve().parent

TEMPLATES[0]["DIRS"] = [  # noqa: F405
    *TEMPLATES[0]["DIRS"],  # noqa: F405
    TESTS_DIR / "templates",
]
