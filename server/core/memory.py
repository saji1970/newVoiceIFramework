from __future__ import annotations

import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class MemoryStore:
    """Simple persistent key-value memory store for conversation context."""

    def __init__(self, storage_path: str = ".voicei_memory.json"):
        self._path = Path(storage_path)
        self._data: dict[str, dict] = {}
        self._load()

    def _load(self):
        if self._path.exists():
            try:
                self._data = json.loads(self._path.read_text())
            except Exception:
                logger.warning("Failed to load memory store, starting fresh")
                self._data = {}

    def _save(self):
        self._path.write_text(json.dumps(self._data, indent=2))

    def set(self, namespace: str, key: str, value: str):
        self._data.setdefault(namespace, {})[key] = value
        self._save()

    def get(self, namespace: str, key: str) -> str | None:
        return self._data.get(namespace, {}).get(key)

    def get_all(self, namespace: str) -> dict:
        return dict(self._data.get(namespace, {}))

    def delete(self, namespace: str, key: str) -> bool:
        if namespace in self._data and key in self._data[namespace]:
            del self._data[namespace][key]
            self._save()
            return True
        return False

    def clear_namespace(self, namespace: str):
        self._data.pop(namespace, None)
        self._save()
