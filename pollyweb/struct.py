"""Generic struct base class with get/require helpers for PollyWeb."""
from typing import Any


class Struct:
    """Base class providing convenience accessors for PollyWeb message-like objects.
    
    Subclasses (e.g., Msg) can inherit get() and require() to access both
    top-level fields and nested Body dictionary keys with a unified interface.
    """

    def get(
        self,
        key: str,
        default: Any = None) -> Any:
        """Return the value of a field or Body key, or default if not found."""
        # First check if it's a top-level attribute on the object
        if hasattr(self, key):
            return getattr(self, key)
        
        # Then check if there's a Body dict with the key
        if hasattr(self, 'Body') and isinstance(self.Body, dict):
            return self.Body.get(key, default)
        
        # Not found anywhere, return default
        return default

    def require(
        self,
        key: str) -> Any:
        """Return the value of a field or Body key, raising KeyError if not found."""
        # First check if it's a top-level attribute on the object
        if hasattr(self, key):
            return getattr(self, key)
        
        # Then check if there's a Body dict with the key
        if hasattr(self, 'Body') and isinstance(self.Body, dict) and key in self.Body:
            return self.Body[key]
        
        # Not found anywhere, raise KeyError
        raise KeyError(f"{type(self).__name__} has no field or Body key '{key}'")
