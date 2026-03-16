# Struct

Base class providing convenience accessors for PollyWeb message-like objects.

## Overview

`Struct` is a minimal base class that provides `get()` and `require()` methods for unified access to both top-level fields and nested `Body` keys. When `Struct` wraps a mapping, its keys are also available as attributes, so nested payloads can be accessed with dot notation.

## Usage

```python
import pollyweb as pw

# Msg inherits from Struct, so you can use get() and require()
msg = pw.Msg(
    To="receiver.dom",
    Subject="Hello@Host",
    Body={
        "action": "greet",
        "meta": {"count": 42},
    }
)

# Access top-level fields
msg.get("To")           # "receiver.dom"
msg.get("Subject")      # "Hello@Host"
msg.Subject             # "Hello@Host"

# Access Body keys
msg.get("action")       # "greet"
msg.action              # "greet"
msg.Body.action         # "greet"
msg.Body.get("action")  # "greet"
msg.Body.meta.count     # 42

# Use default for missing keys
msg.get("missing", 0)   # 0

# Require a key (raises KeyError if not found)
msg.require("action")   # "greet"
msg.require("missing")  # KeyError
```

## Methods

### assert

```python
getattr(struct, "assert")(schema: dict[str, Any], *, field_name: str = "value", error_type: type[Exception] = TypeError) -> Struct
```

Validate the wrapped mapping against a JSON Schema using `fastjsonschema`, trim strings recursively before validation, apply schema defaults, and return the validated payload as a wrapped `Struct`.

**Parameters:**
- `schema` — JSON Schema dictionary used to validate the struct
- `field_name` — Field label used in type mismatch errors (default: `"value"`)
- `error_type` — Exception class raised when validation fails (default: `TypeError`)

**Returns:** A wrapped `Struct` containing the validated and default-populated data

**Raises:** `error_type` if the value is not an object or fails schema validation

**Example:**

```python
payload = pw.Struct.wrap({
    "Domain": " example.com ",
})

validated = getattr(
    payload,
    "assert")({
    "type": "object",
    "properties": {
        "Domain": {
            "type": "string",
            "minLength": 1,
        },
        "Language": {
            "type": "string",
            "default": "en-us",
        },
    },
    "required": ["Domain"],
})

validated.Domain    # "example.com"
validated.Language  # "en-us"
```

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
2. Then checks if there's a `Body` mapping containing `key`
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
2. Then checks if there's a `Body` mapping containing `key`
3. Raises `KeyError` with a descriptive message if not found

## Design Notes

- `Struct` is a simple mixin — it doesn't define any fields itself
- Mapping-backed `Struct` values expose keys as attributes, so `msg.Body.meta.count` works for nested payloads
- For message-like objects such as `Msg`, missing attributes also fall back to `Body`, so `msg.action` behaves like `msg.get("action")`
- Subclasses are expected to have a `Body` field when they want body fallback lookup
- Top-level fields take precedence over Body keys with the same name
- The `get()` method is safe for missing keys (returns default)
- The `require()` method is strict and raises `KeyError` for missing keys
