import os
import pickle
from pathlib import Path
from typing import Any

import yaml

from agri_guide.exception import AgriGuideException
from agri_guide.logging import logger


def read_yaml(path: str | os.PathLike) -> dict:
    """Read a YAML file and return its content as a dict."""
    try:
        path = Path(path)
        logger.info("Reading YAML file: %s", path)
        with path.open("r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except Exception as exc:  # pragma: no cover - thin wrapper
        raise AgriGuideException(f"Failed to read YAML at {path}", exc) from exc


def save_object(path: str | os.PathLike, obj: Any) -> None:
    """Persist an arbitrary Python object to disk using pickle."""
    try:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        logger.info("Saving object to: %s", path)
        with path.open("wb") as f:
            pickle.dump(obj, f)
    except Exception as exc:  # pragma: no cover - thin wrapper
        raise AgriGuideException(f"Failed to save object at {path}", exc) from exc


def load_object(path: str | os.PathLike) -> Any:
    """Load a pickled Python object from disk."""
    try:
        path = Path(path)
        logger.info("Loading object from: %s", path)
        with path.open("rb") as f:
            return pickle.load(f)
    except Exception as exc:  # pragma: no cover - thin wrapper
        raise AgriGuideException(f"Failed to load object at {path}", exc) from exc








