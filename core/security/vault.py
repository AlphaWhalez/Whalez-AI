"""File-backed encrypted secrets vault."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from .crypto import fernet_from_env


class Vault:
    """Simple encrypted vault backed by Fernet-encrypted files."""

    def __init__(self, root: str = ".secrets") -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self._fernet = fernet_from_env()

    def _path(self, key: str) -> Path:
        safe = key.replace("/", "_")
        return self.root / f"{safe}.secret"

    def set(self, key: str, value: str) -> None:
        token = self._fernet.encrypt(value.encode())
        self._path(key).write_bytes(token)

    def get(self, key: str) -> Optional[str]:
        path = self._path(key)
        if not path.exists():
            return None
        return self._fernet.decrypt(path.read_bytes()).decode()

    def list(self) -> list[str]:
        return [p.stem for p in self.root.glob("*.secret")]


__all__ = ["Vault"]
