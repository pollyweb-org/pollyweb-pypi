"""PollyWeb Prompt wrapper for chat prompts carried in Msg bodies."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Mapping, Union

import yaml

from pollyweb.msg import Msg
from pollyweb.struct import Struct

PROMPT_SUBJECT = "Prompted@Host"


class PromptValidationError(Exception):
    """Raised when prompt validation fails."""


def _normalize_prompt_value(value: Any) -> Any:
    """Convert nested values into plain prompt wire-compatible containers."""

    return Struct.unwrap(Struct.wrap(value))


def _require_string(
    value: Any,
    *,
    field_name: str
) -> str:
    """Return a required non-empty string field."""

    if not isinstance(value, str) or not value.strip():
        raise PromptValidationError(f"{field_name} must be a non-empty string")

    return value.strip()


def _optional_string(
    value: Any,
    *,
    field_name: str
) -> str:
    """Return an optional string field normalized to an empty string."""

    if value in (None, ""):
        return ""
    if not isinstance(value, str):
        raise PromptValidationError(f"{field_name} must be a string")

    return value


@dataclass(frozen = True)
class Prompt:
    """Typed wrapper for the PollyWeb Prompt chat payload."""

    Text: str
    Details: str = ""
    Options: list[Any] = field(default_factory = list)
    Default: Any = None
    Appendix: str = ""
    Input: str = ""
    Format: str = ""
    Status: str = ""

    def __post_init__(self) -> None:
        """Validate prompt fields and normalize nested values."""

        object.__setattr__(
            self,
            "Text",
            _require_string(
                self.Text,
                field_name = "Text",
            ),
        )
        object.__setattr__(
            self,
            "Details",
            _optional_string(
                self.Details,
                field_name = "Details",
            ),
        )
        object.__setattr__(
            self,
            "Appendix",
            _optional_string(
                self.Appendix,
                field_name = "Appendix",
            ),
        )
        object.__setattr__(
            self,
            "Input",
            _optional_string(
                self.Input,
                field_name = "Input",
            ),
        )
        object.__setattr__(
            self,
            "Format",
            _optional_string(
                self.Format,
                field_name = "Format",
            ),
        )
        object.__setattr__(
            self,
            "Status",
            _optional_string(
                self.Status,
                field_name = "Status",
            ),
        )

        # Preserve prompt option ordering while normalizing nested values.
        if not isinstance(self.Options, list):
            raise PromptValidationError("Options must be a list")

        object.__setattr__(
            self,
            "Options",
            [_normalize_prompt_value(item) for item in self.Options],
        )
        object.__setattr__(
            self,
            "Default",
            _normalize_prompt_value(self.Default),
        )

    def to_dict(self) -> dict[str, Any]:
        """Return the wire-format mapping for this prompt."""

        payload = {
            "Text": self.Text,
        }

        if self.Details:
            payload["Details"] = self.Details
        if self.Options:
            payload["Options"] = _normalize_prompt_value(self.Options)
        if self.Default is not None:
            payload["Default"] = _normalize_prompt_value(self.Default)
        if self.Appendix:
            payload["Appendix"] = self.Appendix
        if self.Input:
            payload["Input"] = self.Input
        if self.Format:
            payload["Format"] = self.Format
        if self.Status:
            payload["Status"] = self.Status

        return payload

    def to_msg(
        self,
        To: str,
        *,
        From: str = "",
        Selector: str = "",
        Correlation: str = None,
        Timestamp: str = None
    ) -> Msg:
        """Return this prompt wrapped in a PollyWeb ``Prompted@Host`` message."""

        return Msg(
            To = To,
            Subject = PROMPT_SUBJECT,
            From = From,
            Selector = Selector,
            Body = self.to_dict(),
            Correlation = Correlation,
            Timestamp = Timestamp,
        )

    @classmethod
    def from_dict(
        cls,
        value: Mapping[str, Any]
    ) -> "Prompt":
        """Construct a prompt from a wire-format mapping."""

        mapping = dict(value)

        return cls(
            Text = mapping.get("Text", ""),
            Details = mapping.get("Details", ""),
            Options = list(mapping.get("Options", [])),
            Default = mapping.get("Default"),
            Appendix = mapping.get("Appendix", ""),
            Input = mapping.get("Input", ""),
            Format = mapping.get("Format", ""),
            Status = mapping.get("Status", ""),
        )

    @classmethod
    def from_msg(
        cls,
        value: Union[Msg, Mapping[str, Any], str, bytes]
    ) -> "Prompt":
        """Construct a prompt from a PollyWeb ``Prompted@Host`` message."""

        msg = Msg.parse(value)

        if msg.Subject != PROMPT_SUBJECT:
            raise PromptValidationError(
                f"Prompt message Subject must be {PROMPT_SUBJECT}"
            )
        if not isinstance(msg.Body, (Mapping, Struct)):
            raise PromptValidationError("Prompt message Body must be a mapping")

        return cls.from_dict(Struct.unwrap(msg.Body))

    @classmethod
    def parse(
        cls,
        value: Union["Prompt", Msg, Mapping[str, Any], str, bytes]
    ) -> "Prompt":
        """Parse a prompt from an instance, message, mapping, JSON, YAML, or bytes."""

        if isinstance(value, cls):
            return value
        if isinstance(value, Msg):
            return cls.from_msg(value)
        if isinstance(value, Mapping):
            mapping = dict(value)

            if "Header" in mapping:
                return cls.from_msg(mapping)

            return cls.from_dict(mapping)
        if isinstance(value, bytes):
            value = value.decode("utf-8")
        if isinstance(value, str):
            try:
                parsed = json.loads(value)
            except json.JSONDecodeError:
                try:
                    parsed = yaml.safe_load(value)
                except yaml.YAMLError as exc:
                    raise PromptValidationError("Prompt text is not valid JSON or YAML") from exc

            if not isinstance(parsed, Mapping):
                raise PromptValidationError("Prompt text must decode to a mapping")

            return cls.parse(parsed)

        raise PromptValidationError("Prompt must be a Prompt, Msg, mapping, str, or bytes")

    @classmethod
    def load(
        cls,
        value: Union["Prompt", Msg, Mapping[str, Any], str, bytes]
    ) -> "Prompt":
        """Backward-compatible alias for parse()."""

        return cls.parse(value)
