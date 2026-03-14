"""PollyWeb schema code value type."""

from __future__ import annotations

import re

DEFAULT_SCHEMA_AUTHORITY = "pollyweb.org"

_DOMAIN_RE = re.compile(
    r"^(?=.{1,253}$)(?:[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?\.)+"
    r"(?:[A-Za-z]{2,63}|xn--[A-Za-z0-9-]{1,59})$"
)
_SCHEMA_CODE_RE = re.compile(r"^[A-Za-z0-9-]+(?:/[A-Za-z0-9-]+)*$")
_SCHEMA_VERSION_RE = re.compile(r"^\d+\.\d+$")


def _is_domain_name(value: str) -> bool:
    return bool(_DOMAIN_RE.fullmatch(value))


class Schema(str):
    """Validated PollyWeb schema code.

    Accepted formats:
    - ``{authority}/{code}``
    - ``{authority}/{code}:{major}.{minor}``
    - ``.{code}`` shorthand for ``pollyweb.org/{code}:1.0``
    """

    def __new__(cls, value: str) -> "Schema":
        if not isinstance(value, str):
            raise TypeError("Schema must be a string")

        authority: str
        code: str
        version: str

        if value.startswith("."):
            authority = DEFAULT_SCHEMA_AUTHORITY
            remainder = value[1:]
        else:
            if "/" not in value:
                raise ValueError("Schema must match {authority}/{code}[:{major}.{minor}]")
            authority, remainder = value.split("/", 1)

        if ":" in remainder:
            code, version = remainder.rsplit(":", 1)
        else:
            code, version = remainder, "1.0"

        if not _is_domain_name(authority):
            raise ValueError("Schema authority must be a domain string")
        if not _SCHEMA_CODE_RE.fullmatch(code):
            raise ValueError("Schema code must be slash-separated letters, digits, or hyphens")
        if not _SCHEMA_VERSION_RE.fullmatch(version):
            raise ValueError("Schema version must match {major}.{minor}")

        normalized = f"{authority}/{code}:{version}"
        obj = str.__new__(cls, normalized)
        obj.authority = authority
        obj.code = code
        obj.version = version
        major, minor = version.split(".", 1)
        obj.major = int(major)
        obj.minor = int(minor)
        return obj
