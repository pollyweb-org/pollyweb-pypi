# Struct

Base class providing convenience accessors for PollyWeb message-like objects.

## Overview

`Struct` is a minimal base class that provides `get()` and `require()` methods for unified access to both top-level fields and nested `Body` dictionary keys. It's designed to be inherited by classes like `Msg` that have a `Body` field containing arbitrary key-value data.

## Usage

```python
import pollyweb as pw

# Msg inherits from Struct, so you can use get() and require()
msg = pw.Msg(
    To="receiver.dom",
    Subject="Hello@Host",
    Body={"action": "greet", "count": 42}
)

# Access top-level fields
msg.get("To")           # "receiver.dom"
msg.get("Subject")      # "Hello@Host"

# Access Body keys
msg.get("action")       # "greet"
msg.get("count")        # 42

# Use default for missing keys
msg.get("missing", 0)   # 0

# Require a key (raises KeyError if not found)
msg.require("action")   # "greet"
msg.require("missing")  # KeyError
```

## Methods

### get

```python
def get(self, key: str, default: Any = None) -> Any
```

Return the value of a field or Body key, or default if not found.

**Parameters:**
- `key` — Field name or Body dictionary key to retrieve
- `default` — Value to return if key is not found (default: `None`)

**Returns:** The field value, `Body[key]`, or `default`

**Behavior:**
1. First checks if `key` is a top-level attribute on the object
2. Then checks if there's a `Body` dict containing `key`
3. Returns `default` if not found anywhere

### require

```python
def require(self, key: str) -> Any
```

Return the value of a field or Body key, raising `KeyError` if not found.

**Parameters:**
- `key` — Field name or Body dictionary key to retrieve

**Returns:** The field value or `Body[key]`

**Raises:** `KeyError` if key is not found as a field or in Body

**Behavior:**
1. First checks if `key` is a top-level attribute on the object
2. Then checks if there's a `Body` dict containing `key`
3. Raises `KeyError` with a descriptive message if not found

## Design Notes

- `Struct` is a simple mixin — it doesn't define any fields itself
- Subclasses are expected to have a `Body: Dict[str, Any]` field for the nested key lookup to work
- Top-level fields take precedence over Body keys with the same name
- The `get()` method is safe for missing keys (returns default)
- The `require()` method is strict and raises `KeyError` for missing keys
