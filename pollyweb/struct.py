"""Generic struct base class with get/require helpers for PollyWeb."""
import json
from collections.abc import Mapping
from functools import lru_cache
from typing import Any, Iterator

import fastjsonschema


class Struct:
    """Base class providing convenience accessors for PollyWeb message-like objects."""

    _MISSING = object()

    def __init__(
        self,
        **values: Any) -> None:
        """Store mapping-style values for attribute and key lookup."""

        # Wrap nested mappings eagerly so attribute access works recursively.
        object.__setattr__(
            self,
            "_data",
            {key: self.wrap(value) for key, value in values.items()},
        )

    @classmethod
    def wrap(
        cls,
        value: Any) -> Any:
        """Wrap nested mappings as Struct instances and leave other values unchanged."""

        if isinstance(value, Struct):
            return value
        if isinstance(value, Mapping):
            return cls(**dict(value))
        if isinstance(value, list):
            return [cls.wrap(item) for item in value]
        return value

    @classmethod
    def list(
        cls,
        value: Any,
        *,
        field_name: str,
        error_type: type[Exception] = TypeError
    ) -> list[Any]:
        """Validate that *value* is a list and return a shallow copy."""

        if not isinstance(value, list):
            raise error_type(f"{field_name} must be a list.")

        return list(value)

    @classmethod
    def mapping(
        cls,
        value: Any,
        *,
        field_name: str,
        error_type: type[Exception] = TypeError
    ) -> dict[str, Any]:
        """Validate that *value* is a mapping-like object and return a plain dict."""

        if not isinstance(value, (Mapping, Struct)):
            raise error_type(f"{field_name} must be an object.")

        if isinstance(value, Struct):
            return value.to_dict()

        return dict(value)

    @classmethod
    def coerce_string(
        cls,
        value: Any,
        *,
        field_name: str,
        error_type: type[Exception] = TypeError
    ) -> str:
        """Validate that *value* is a non-empty string and return it trimmed."""

        if not isinstance(value, str) or not value.strip():
            raise error_type(f"Missing {field_name}.")

        return value.strip()

    @classmethod
    def unwrap(
        cls,
        value: Any) -> Any:
        """Convert Struct instances back into plain Python data."""

        if isinstance(value, Struct):
            return {key: cls.unwrap(item) for key, item in value.items()}
        if isinstance(value, list):
            return [cls.unwrap(item) for item in value]
        return value

    def __getattr__(
        self,
        key: str) -> Any:
        """Provide attribute-style access for mapping-backed values and Body fallback."""

        data = self.__dict__.get("_data")
        if data is not None and key in data:
            return data[key]

        # For message-like structs, missing attributes can fall back to Body keys.
        value = self._lookup_body_value(key)
        if value is not self._MISSING:
            return value

        raise AttributeError(f"{type(self).__name__} has no attribute '{key}'")

    def __contains__(
        self,
        key: object) -> bool:
        """Return whether a mapping-backed Struct contains *key*."""

        data = self.__dict__.get("_data")
        return isinstance(key, str) and data is not None and key in data

    def __iter__(self) -> Iterator[str]:
        """Iterate over keys when this Struct wraps mapping-style data."""

        data = self.__dict__.get("_data", {})
        return iter(data)

    def __len__(self) -> int:
        """Return the number of keys when this Struct wraps mapping-style data."""

        data = self.__dict__.get("_data", {})
        return len(data)

    def __eq__(
        self,
        other: object) -> bool:
        """Compare Struct instances against plain mappings by value."""

        if isinstance(other, Struct):
            return self.to_dict() == other.to_dict()
        if isinstance(other, Mapping):
            return self.to_dict() == dict(other)
        return super().__eq__(other)

    def items(self):
        """Return mapping items for mapping-backed Struct instances."""

        data = self.__dict__.get("_data", {})
        return data.items()

    def to_dict(self) -> dict[str, Any]:
        """Return the wrapped mapping as plain Python data."""

        return {key: self.unwrap(value) for key, value in self.items()}

    def _lookup_header_value(
        self,
        key: str) -> Any:
        """Return a top-level attribute value if present."""

        if key in self.__dict__.get("_data", {}):
            return self.__dict__["_data"][key]
        if hasattr(type(self), key):
            return getattr(self, key)
        if key in self.__dict__:
            return self.__dict__[key]
        return self._MISSING

    def _lookup_body_value(
        self,
        key: str) -> Any:
        """Return a nested Body value if present."""

        body = self._lookup_header_value("Body")
        if body is self._MISSING:
            return self._MISSING
        if isinstance(body, Struct):
            return body._lookup_header_value(key)
        if isinstance(body, Mapping) and key in body:
            return self.wrap(body[key])
        return self._MISSING

    def get(
        self,
        key: str,
        default: Any = None) -> Any:
        """Return the value of a field or Body key, or default if not found."""

        # Header fields always take precedence over Body keys.
        value = self._lookup_header_value(key)
        if value is not self._MISSING:
            return value

        # Fall back to Body only when the top-level field is absent.
        value = self._lookup_body_value(key)
        if value is not self._MISSING:
            return value

        return default

    def require(
        self,
        key: str) -> Any:
        """Return the value of a field or Body key, raising KeyError if not found."""

        value = self.get(key, self._MISSING)
        if value is not self._MISSING:
            return value

        raise KeyError(f"{type(self).__name__} has no field or Body key '{key}'")

    def require_string(
        self,
        key: str,
        *,
        error_type: type[Exception] = KeyError
    ) -> str:
        """Return a required non-empty string field or Body key."""

        value = self.get(key, self._MISSING)
        if value is self._MISSING:
            raise error_type(f"Missing {key}.")

        return type(self).coerce_string(
            value,
            field_name = key,
            error_type = error_type,
        )


@lru_cache(maxsize = 64)
def _compiled_validator(
    schema_json: str):
    """Return a cached fastjsonschema validator for a serialized schema."""

    # Compile validators once per schema so repeated validations stay fast.
    return fastjsonschema.compile(
        json.loads(schema_json),
        use_default = True)


def _normalize_for_schema(
    value: Any) -> Any:
    """Trim strings recursively before schema validation."""

    if isinstance(value, str):
        return value.strip()
    if isinstance(value, list):
        return [_normalize_for_schema(item) for item in value]
    if isinstance(value, dict):
        return {
            key: _normalize_for_schema(item)
            for key, item in value.items()}
    if isinstance(value, Struct):
        return _normalize_for_schema(value.to_dict())
    return value


def _is_full_json_schema(
    schema: Any) -> bool:
    """Return whether *schema* already looks like a standard JSON Schema object."""

    if not isinstance(schema, dict):
        return False

    schema_keywords = {
        "$ref",
        "$schema",
        "additionalProperties",
        "anyOf",
        "default",
        "enum",
        "format",
        "items",
        "minLength",
        "oneOf",
        "pattern",
        "properties",
        "required",
        "type",
    }
    return any(key in schema for key in schema_keywords)


def _compact_string_schema(
    schema: str) -> tuple[dict[str, Any], bool]:
    """Convert a compact scalar schema token into JSON Schema plus required flag."""

    required = schema.endswith("!")
    token = schema[:-1] if required else schema

    if token == "str":  # nosec B105
        converted: dict[str, Any] = {
            "type": "string"}
        if required:
            converted["minLength"] = 1
        return converted, required

    raise ValueError(f"Unsupported compact schema token: {schema}")


def _expand_compact_schema(
    schema: Any) -> tuple[dict[str, Any], bool]:
    """Expand the compact schema form into standard JSON Schema."""

    if isinstance(schema, str):
        return _compact_string_schema(schema)

    if isinstance(schema, list):
        if len(schema) != 1:
            raise ValueError("Compact list schemas must contain exactly one item schema.")

        items_schema, _ = _expand_compact_schema(schema[0])
        return {
            "type": "array",
            "items": items_schema}, True

    if isinstance(schema, dict):
        if _is_full_json_schema(schema):
            return schema, bool(schema.get("required"))

        properties: dict[str, Any] = {}
        required: list[str] = []

        for raw_key, raw_value in schema.items():
            key = raw_key
            is_optional = False
            if raw_key.endswith("?"):
                key = raw_key[:-1]
                is_optional = True

            property_schema, property_required = _expand_compact_schema(raw_value)
            properties[key] = property_schema

            if not is_optional and property_required:
                required.append(key)

        converted = {
            "type": "object",
            "properties": properties}
        if required:
            converted["required"] = required
        return converted, True

    raise ValueError(f"Unsupported compact schema value: {schema!r}")


def _format_schema_error(
    err: Exception) -> str:
    """Convert a fastjsonschema error into a concise validation message."""

    path = getattr(err, "path", [])
    rule = getattr(err, "rule", "")
    value = getattr(err, "value", None)

    if path:
        field_name = str(path[-1])
    else:
        field_name = "value"

    if rule == "required" and isinstance(value, dict):
        missing = str(err).split("must contain", 1)[-1].strip().strip("'\"")
        missing = missing.replace("properties", "").strip()
        if missing:
            return f"Missing {missing}."

    if rule == "type":
        if "object" in str(err):
            return f"{field_name} must be an object."
        if "array" in str(err):
            return f"{field_name} must be a list."
        if "string" in str(err):
            return f"{field_name} must be a string."

    if rule == "minLength":
        return f"Missing {field_name}."

    return str(err)


def _assert(
    self: Struct,
    schema: dict[str, Any],
    *,
    field_name: str = "value",
    error_type: type[Exception] = TypeError
) -> Struct:
    """Validate this struct against JSON Schema and return the wrapped result."""

    payload = Struct.mapping(
        self,
        field_name = field_name,
        error_type = error_type)
    normalized = _normalize_for_schema(payload)
    expanded_schema, _ = _expand_compact_schema(schema)
    validator = _compiled_validator(
        json.dumps(
            expanded_schema,
            sort_keys = True))

    try:
        validated = validator(normalized)
    except fastjsonschema.JsonSchemaException as err:
        raise error_type(_format_schema_error(err)) from err

    return Struct.wrap(validated)


# Expose both ``Struct.assert(...)`` and the Python-friendly ``Struct.schema(...)``.
setattr(
    Struct,
    "assert",
    _assert)
setattr(
    Struct,
    "schema",
    _assert)
