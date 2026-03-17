"""PollyWeb Token wrapper for signed issuer credentials."""

from __future__ import annotations

import base64
import json
from dataclasses import dataclass, replace
from datetime import date, datetime, timezone
from typing import Any, Mapping, Optional, Union

import yaml

from pollyweb._crypto import (
    canonical_signature_algorithm,
    encode_signature,
    signature_algorithm_for_dkim_key_type,
    signature_algorithm_for_private_key,
    sign_message,
    verify_signature,
)
from pollyweb.msg import _is_domain_name, _is_z_timestamp, _resolve_dkim_public_key
from pollyweb.schema import Schema
from pollyweb.struct import Struct


def _utc_now() -> str:
    """Return the current UTC timestamp in PollyWeb Z format."""

    now = datetime.now(timezone.utc)
    return now.strftime("%Y-%m-%dT%H:%M:%S.") + f"{now.microsecond // 1000:03d}Z"


def _normalize_wire_value(value: Any) -> Any:
    """Convert YAML-native date values into token wire values."""

    if isinstance(value, datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo = timezone.utc)
        else:
            value = value.astimezone(timezone.utc)

        return value.strftime("%Y-%m-%dT%H:%M:%S.") + f"{value.microsecond // 1000:03d}Z"
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, dict):
        return {k: _normalize_wire_value(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_normalize_wire_value(item) for item in value]

    return value


class TokenValidationError(Exception):
    """Raised when token validation fails."""


@dataclass(frozen=True)
class Token:
    """Signed PollyWeb token issued by a domain."""

    Token: str
    Issuer: str
    Schema: Schema
    Context: Any = None
    Issued: str = ""
    Starts: str = ""
    Expires: str = ""
    Identifier: str = ""
    Biostamp: str = ""
    Signature: Optional[str] = None
    DKIM: str = ""
    Algorithm: str = ""

    def __post_init__(self) -> None:
        """Normalize defaults and validate the token fields."""

        issued = self.Issued or _utc_now()
        starts = self.Starts or issued
        context = {} if self.Context is None else Struct.unwrap(Struct.wrap(self.Context))

        object.__setattr__(self, "Issued", issued)
        object.__setattr__(self, "Starts", starts)
        object.__setattr__(self, "Context", context)

        try:
            schema = self.Schema if isinstance(self.Schema, Schema) else Schema(self.Schema)
        except (TypeError, ValueError) as exc:
            raise TokenValidationError(str(exc)) from exc

        object.__setattr__(self, "Schema", schema)

        if not isinstance(self.Token, str) or not self.Token.strip():
            raise TokenValidationError("Token must be a non-empty string")
        if not _is_domain_name(self.Issuer):
            raise TokenValidationError("Issuer must be a domain string")
        if not isinstance(self.Context, Mapping):
            raise TokenValidationError("Context must be a mapping")
        if not _is_z_timestamp(self.Issued):
            raise TokenValidationError("Issued must be a Z timestamp")
        if not _is_z_timestamp(self.Starts):
            raise TokenValidationError("Starts must be a Z timestamp")
        if self.Expires and not _is_z_timestamp(self.Expires):
            raise TokenValidationError("Expires must be a Z timestamp")
        if self.Identifier and not _is_domain_name(self.Identifier):
            raise TokenValidationError("Identifier must be a domain string")
        if self.Biostamp and not self.Identifier:
            raise TokenValidationError("Biostamp requires Identifier")
        if self.Algorithm:
            try:
                algorithm = canonical_signature_algorithm(self.Algorithm)
            except ValueError as exc:
                raise TokenValidationError(str(exc)) from exc
            object.__setattr__(self, "Algorithm", algorithm)

    def canonical(self) -> bytes:
        """Return canonical JSON bytes for signing and verification."""

        payload = {
            "Context": self.Context,
            "Issued": self.Issued,
            "Issuer": self.Issuer,
            "Schema": str(self.Schema),
            "Starts": self.Starts,
            "Token": self.Token,
        }

        if self.Expires:
            payload["Expires"] = self.Expires
        if self.Identifier:
            payload["Identifier"] = self.Identifier
        if self.Biostamp:
            payload["Biostamp"] = self.Biostamp
        if self.DKIM:
            payload["DKIM"] = self.DKIM

        return json.dumps(
            payload,
            sort_keys = True,
            separators = (",", ":"),
            ensure_ascii = False,
        ).encode("utf-8")

    def sign(
        self,
        private_key: object
    ) -> "Token":
        """Return a signed copy of this token using *private_key*."""

        if not self.DKIM:
            raise TokenValidationError("Missing DKIM")

        try:
            algorithm = (
                canonical_signature_algorithm(self.Algorithm)
                if self.Algorithm
                else signature_algorithm_for_private_key(private_key)
            )
            signature_bytes, _ = sign_message(
                private_key,
                self.canonical(),
                signature_algorithm = algorithm,
            )
        except (TypeError, ValueError) as exc:
            raise TokenValidationError(str(exc)) from exc

        return replace(
            self,
            Algorithm = algorithm,
            Signature = encode_signature(signature_bytes),
        )

    def verify(
        self,
        public_key: Optional[object] = None
    ) -> bool:
        """Verify the token signature using *public_key* or DNS."""

        if self.Signature is None:
            raise TokenValidationError("Missing Signature")
        if self.Expires and self.Expires < self.Starts:
            raise TokenValidationError("Expires must be after Starts")

        if public_key is None:
            if not self.DKIM:
                raise TokenValidationError("Missing DKIM")

            public_key, key_type = _resolve_dkim_public_key(self.Issuer, self.DKIM)
            dns_algorithm = signature_algorithm_for_dkim_key_type(key_type)

            if self.Algorithm and self.Algorithm != dns_algorithm:
                raise TokenValidationError(
                    f"Signature algorithm {self.Algorithm} does not match DKIM algorithm {dns_algorithm}"
                )

        try:
            verify_signature(
                public_key,
                base64.b64decode(self.Signature),
                self.canonical(),
                signature_algorithm = self.Algorithm or None,
            )
        except (TypeError, ValueError) as exc:
            raise TokenValidationError(str(exc)) from exc
        except Exception as exc:
            raise TokenValidationError(f"Invalid signature: {exc}") from exc

        return True

    def to_dict(self) -> dict[str, Any]:
        """Return the wire-format mapping for this token."""

        payload = {
            "Token": self.Token,
            "Issuer": self.Issuer,
            "Schema": str(self.Schema),
            "Context": self.Context,
            "Issued": self.Issued,
            "Starts": self.Starts,
            "DKIM": self.DKIM,
        }

        if self.Expires:
            payload["Expires"] = self.Expires
        if self.Identifier:
            payload["Identifier"] = self.Identifier
        if self.Biostamp:
            payload["Biostamp"] = self.Biostamp
        if self.Signature is not None:
            payload["Signature"] = self.Signature
        if self.Algorithm:
            payload["Algorithm"] = self.Algorithm

        return payload

    @classmethod
    def from_dict(
        cls,
        value: Mapping[str, Any]
    ) -> "Token":
        """Construct a token from a wire-format mapping."""

        mapping = dict(value)

        return cls(
            Token = mapping.get("Token", ""),
            Issuer = mapping.get("Issuer", ""),
            Schema = mapping.get("Schema", ""),
            Context = mapping.get("Context", {}),
            Issued = mapping.get("Issued", ""),
            Starts = mapping.get("Starts", ""),
            Expires = mapping.get("Expires", ""),
            Identifier = mapping.get("Identifier", ""),
            Biostamp = mapping.get("Biostamp", ""),
            Signature = mapping.get("Signature"),
            DKIM = mapping.get("DKIM", ""),
            Algorithm = mapping.get("Algorithm", ""),
        )

    @classmethod
    def parse(
        cls,
        value: Union["Token", Mapping[str, Any], str, bytes]
    ) -> "Token":
        """Parse a token from an instance, mapping, JSON, YAML, or bytes."""

        if isinstance(value, cls):
            return value
        if isinstance(value, Mapping):
            return cls.from_dict(_normalize_wire_value(dict(value)))
        if isinstance(value, bytes):
            value = value.decode("utf-8")
        if isinstance(value, str):
            try:
                parsed = json.loads(value)
            except json.JSONDecodeError:
                try:
                    parsed = yaml.safe_load(value)
                except yaml.YAMLError as exc:
                    raise TokenValidationError("Token text is not valid JSON or YAML") from exc

            if not isinstance(parsed, Mapping):
                raise TokenValidationError("Token text must decode to a mapping")

            return cls.from_dict(_normalize_wire_value(dict(parsed)))

        raise TokenValidationError("Token must be a Token, mapping, str, or bytes")

    @classmethod
    def load(
        cls,
        value: Union["Token", Mapping[str, Any], str, bytes]
    ) -> "Token":
        """Backward-compatible alias for parse()."""

        return cls.parse(value)
