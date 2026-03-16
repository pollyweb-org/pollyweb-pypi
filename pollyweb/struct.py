"""Generic struct base class with get/require helpers for PollyWeb."""
from typing import Any

class Struct:
    def get(self, key: str, default: Any = None) -> Any:
        if hasattr(self, key):
            return getattr(self, key)
        if hasattr(self, 'Body') and isinstance(self.Body, dict):
            return self.Body.get(key, default)
        return default

    def require(self, key: str) -> Any:
        if hasattr(self, key):
            return getattr(self, key)
        if hasattr(self, 'Body') and isinstance(self.Body, dict) and key in self.Body:
            return self.Body[key]
        raise KeyError(f"{type(self).__name__} has no field or Body key '{key}'")
