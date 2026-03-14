"""PollyWeb domain manifest parsing and validation."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Dict, Mapping, Optional, Union
from urllib.parse import urlparse

import yaml

from pollyweb.msg import _is_domain_name
from pollyweb.schema import Schema

SCHEMA = Schema("pollyweb.org/MANIFEST:1.0")
WIRE_SCHEMA_KEY = "\U0001F91D"


def _normalize_manifest_value(value: Any) -> Any:
    """Convert tuples and nested mappings into plain wire-compatible containers."""
    if isinstance(value, tuple):
        return [_normalize_manifest_value(item) for item in value]
    if isinstance(value, list):
        return [_normalize_manifest_value(item) for item in value]
    if isinstance(value, dict):
        return {k: _normalize_manifest_value(v) for k, v in value.items()}
    return value


def _is_uri(value: str) -> bool:
    """Return True when *value* looks like an absolute URI."""
    if not isinstance(value, str):
        return False
    parsed = urlparse(value)
    return bool(parsed.scheme and parsed.netloc)


class ManifestValidationError(Exception):
    """Raised when manifest validation fails."""


def _ensure_mapping(value: Any, field_name: str) -> Dict[str, Any]:
    if not isinstance(value, Mapping):
        raise ManifestValidationError(f"{field_name} must be a mapping")
    return dict(value)


def _validate_translation(value: Any) -> Dict[str, Any]:
    item = _ensure_mapping(value, "About.Translations item")
    language = item.get("Language")
    if not isinstance(language, str) or not language:
        raise ManifestValidationError("About.Translations item Language must be a string")

    for field_name in ("Title", "Description", "Emoji"):
        if field_name in item and not isinstance(item[field_name], str):
            raise ManifestValidationError(
                f"About.Translations item {field_name} must be a string"
            )

    return item


def _validate_about(value: Any) -> Dict[str, Any]:
    about = _ensure_mapping(value, "About")

    domain = about.get("Domain")
    if not isinstance(domain, str) or not _is_domain_name(domain):
        raise ManifestValidationError("About.Domain must be a domain string")

    normalized = dict(about)
    normalized.setdefault("Language", "en-us")

    for field_name in ("Language", "Title", "Description", "Emoji"):
        if field_name in normalized and not isinstance(normalized[field_name], str):
            raise ManifestValidationError(f"About.{field_name} must be a string")

    for field_name in ("SmallIcon", "BigIcon"):
        if field_name in normalized and not _is_uri(normalized[field_name]):
            raise ManifestValidationError(f"About.{field_name} must be an absolute URI")

    translations = normalized.get("Translations")
    if translations is not None:
        if not isinstance(translations, list):
            raise ManifestValidationError("About.Translations must be a list")
        normalized["Translations"] = [_validate_translation(item) for item in translations]

    return normalized


def _validate_section_list(value: Any, field_name: str) -> list[Dict[str, Any]]:
    if not isinstance(value, list):
        raise ManifestValidationError(f"{field_name} must be a list")
    return [_ensure_mapping(item, f"{field_name} item") for item in value]


@dataclass(frozen=True)
class Manifest:
    About: Dict[str, Any]
    Trust: list[Dict[str, Any]] = field(default_factory=list)
    Code: list[Dict[str, Any]] = field(default_factory=list)
    Delegate: list[Dict[str, Any]] = field(default_factory=list)
    Offer: list[Dict[str, Any]] = field(default_factory=list)
    Chat: list[Dict[str, Any]] = field(default_factory=list)
    Schema: Schema = SCHEMA

    def __post_init__(self) -> None:
        try:
            object.__setattr__(
                self,
                "Schema",
                self.Schema if isinstance(self.Schema, Schema) else Schema(self.Schema),
            )
        except (TypeError, ValueError) as exc:
            raise ManifestValidationError(str(exc)) from exc

        if self.Schema != SCHEMA:
            raise ManifestValidationError(f"Unsupported schema: {self.Schema}")

        object.__setattr__(self, "About", _validate_about(self.About))
        object.__setattr__(self, "Trust", _validate_section_list(self.Trust, "Trust"))
        object.__setattr__(self, "Code", _validate_section_list(self.Code, "Code"))
        object.__setattr__(self, "Delegate", _validate_section_list(self.Delegate, "Delegate"))
        object.__setattr__(self, "Offer", _validate_section_list(self.Offer, "Offer"))
        object.__setattr__(self, "Chat", _validate_section_list(self.Chat, "Chat"))

    def to_dict(self) -> Dict[str, Any]:
        """Return the PollyWeb wire-format mapping for this manifest."""
        payload: Dict[str, Any] = {
            WIRE_SCHEMA_KEY: str(self.Schema),
            "About": _normalize_manifest_value(self.About),
        }

        for field_name in ("Trust", "Code", "Delegate", "Offer", "Chat"):
            value = _normalize_manifest_value(getattr(self, field_name))
            if value:
                payload[field_name] = value

        return payload

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "Manifest":
        """Construct a Manifest from a wire-format mapping."""
        mapping = dict(value)
        schema_value = mapping.get(WIRE_SCHEMA_KEY, mapping.get("Schema", SCHEMA))

        if "About" not in mapping:
            raise ManifestValidationError("Missing About")

        return cls(
            Schema=schema_value,
            About=mapping["About"],
            Trust=mapping.get("Trust", []),
            Code=mapping.get("Code", []),
            Delegate=mapping.get("Delegate", []),
            Offer=mapping.get("Offer", []),
            Chat=mapping.get("Chat", []),
        )

    @classmethod
    def parse(cls, value: Union["Manifest", Mapping[str, Any], str, bytes]) -> "Manifest":
        """Parse a Manifest from an existing instance, mapping, JSON, YAML, or bytes."""
        if isinstance(value, cls):
            return value
        if isinstance(value, Mapping):
            return cls.from_dict(value)
        if isinstance(value, bytes):
            value = value.decode("utf-8")
        if isinstance(value, str):
            try:
                parsed = json.loads(value)
            except json.JSONDecodeError:
                try:
                    parsed = yaml.safe_load(value)
                except yaml.YAMLError as exc:
                    raise ManifestValidationError("Manifest text is not valid JSON or YAML") from exc
            if not isinstance(parsed, Mapping):
                raise ManifestValidationError("Manifest text must decode to a mapping")
            return cls.from_dict(parsed)
        raise ManifestValidationError("Manifest must be a Manifest, mapping, str, or bytes")

    @classmethod
    def load(cls, value: Union["Manifest", Mapping[str, Any], str, bytes]) -> "Manifest":
        """Backward-compatible alias for parse()."""
        return cls.parse(value)
