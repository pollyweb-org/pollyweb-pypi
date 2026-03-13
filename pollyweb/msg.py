"""PollyWeb Message Msg — create, sign, and validate."""

import base64
import hashlib
import json
import uuid
from dataclasses import dataclass, field, replace
from datetime import date, datetime, timezone
from typing import Any, Dict, Mapping, Optional, Union

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)
import yaml

SCHEMA = "pollyweb.org/MSG:1.0"


def _resolve_dkim_public_key(domain: str, selector: str) -> Ed25519PublicKey:
    """Fetch the Ed25519 public key from the DKIM DNS TXT record.

    Queries ``{selector}._domainkey.pw.{domain}`` for a TXT record in the standard
    DKIM wire format: ``v=DKIM1; k=ed25519; p=<base64>``.

    Raises ``MsgValidationError`` if:
    - the DNS lookup fails,
    - DNSSEC is not enabled / the AD flag is not set on the response, or
    - no valid Ed25519 key is found in the TXT records.
    """
    import dns.flags
    import dns.resolver

    dns_name = f"{selector}._domainkey.pw.{domain}"
    try:
        answers = dns.resolver.resolve(dns_name, "TXT")
    except Exception as exc:
        raise MsgValidationError(f"DKIM lookup failed for {dns_name}: {exc}") from exc

    if not (answers.response.flags & dns.flags.AD):
        raise MsgValidationError(
            f"DNSSEC not enabled for {dns_name}: cannot trust DKIM public key"
        )

    for rdata in answers:
        txt = b"".join(rdata.strings).decode("utf-8")
        params: Dict[str, str] = {}
        for part in txt.split(";"):
            part = part.strip()
            if "=" in part:
                k, v = part.split("=", 1)
                params[k.strip()] = v.strip()
        p = params.get("p", "")
        if not p:
            continue
        try:
            raw = base64.b64decode(p)
            return Ed25519PublicKey.from_public_bytes(raw)
        except Exception as exc:
            raise MsgValidationError(
                f"Invalid Ed25519 key in DKIM TXT at {dns_name}: {exc}"
            ) from exc

    raise MsgValidationError(f"No Ed25519 public key found in DKIM TXT at {dns_name}")


def _utc_now() -> str:
    ts = datetime.now(timezone.utc)
    return ts.strftime("%Y-%m-%dT%H:%M:%S.") + f"{ts.microsecond // 1000:03d}Z"


def _normalize_wire_value(value: Any) -> Any:
    """Convert YAML-native scalars into JSON-wire-compatible values."""
    if isinstance(value, datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
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


class MsgValidationError(Exception):
    """Raised when msg validation fails."""


@dataclass(frozen=True)
class Msg:
    To: str
    Subject: str
    From: str = ""
    Selector: str = ""
    Body: Dict[str, Any] = field(default_factory=dict)
    Correlation: str = field(default_factory=lambda: str(uuid.uuid4()))
    Timestamp: str = field(default_factory=_utc_now)
    Schema: str = SCHEMA
    Hash: Optional[str] = None
    Signature: Optional[str] = None

    def canonical(self) -> bytes:
        """Return the canonical JCS JSON bytes of schema + header + body."""
        payload = {
            "Body": self.Body,
            "Header": {
                "Correlation": self.Correlation,
                "Selector": self.Selector,
                "From": self.From,
                "Schema": self.Schema,
                "Subject": self.Subject,
                "Timestamp": self.Timestamp,
                "To": self.To,
            },
        }
        return json.dumps(
            payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
        ).encode("utf-8")

    def sign(self, private_key: Ed25519PrivateKey) -> "Msg":
        """Compute hash and Ed25519-sign this msg. Returns a new signed Msg."""
        canonical = self.canonical()
        hash_hex = hashlib.sha256(canonical).hexdigest()
        sig_b64 = base64.b64encode(private_key.sign(canonical)).decode("ascii")
        return replace(self, Hash=hash_hex, Signature=sig_b64)

    def _validate_schema(self) -> None:
        if self.Schema != SCHEMA:
            raise MsgValidationError(f"Unsupported schema: {self.Schema}")

    def _validate_required_fields(self, *, require_selector: bool) -> None:
        required_fields = [
            ("From", self.From),
            ("To", self.To),
            ("Subject", self.Subject),
            ("Correlation", self.Correlation),
            ("Timestamp", self.Timestamp),
        ]
        if require_selector:
            required_fields.append(("Selector", self.Selector))

        for field_name, value in required_fields:
            if not value:
                raise MsgValidationError(f"Missing {field_name}")

    def _validate_hash(self) -> bytes:
        if self.Hash is None:
            raise MsgValidationError("Missing Hash")

        canonical = self.canonical()
        if self.Hash != hashlib.sha256(canonical).hexdigest():
            raise MsgValidationError("Hash mismatch")

        return canonical

    def validate_unsigned(self) -> bool:
        """Validate structure and canonical hash, but skip signature verification."""
        self._validate_schema()
        self._validate_required_fields(require_selector=False)
        self._validate_hash()
        return True

    def verify(self, public_key: Optional[Ed25519PublicKey] = None) -> bool:
        """Validate structure, canonical hash, and Ed25519 signature.

        If *public_key* is omitted, the key is fetched from DNS using the
        selector and the From domain: ``{Selector}._domainkey.pw.{From}`` (TXT record,
        DKIM wire format: ``v=DKIM1; k=ed25519; p=<base64>``).
        """
        self._validate_schema()
        self._validate_required_fields(require_selector=public_key is None)
        canonical = self._validate_hash()

        if self.Signature is None:
            raise MsgValidationError("Missing Signature")

        if public_key is None:
            public_key = _resolve_dkim_public_key(self.From, self.Selector)

        try:
            sig_bytes = base64.b64decode(self.Signature)
        except Exception as exc:
            raise MsgValidationError(f"Malformed signature: {exc}") from exc

        try:
            public_key.verify(sig_bytes, canonical)
        except InvalidSignature:
            raise MsgValidationError("Invalid signature")

        return True

    def validate_signature(self, public_key: Optional[Ed25519PublicKey] = None) -> bool:
        """Backward-compatible alias for :meth:`verify`."""
        return self.verify(public_key)

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {
            "Header": {
                "From": self.From,
                "To": self.To,
                "Subject": self.Subject,
                "Correlation": self.Correlation,
                "Timestamp": self.Timestamp,
                "Selector": self.Selector,
                "Schema": self.Schema,
            },
            "Body": self.Body,
        }
        if self.Hash is not None:
            d["Hash"] = self.Hash
        if self.Signature is not None:
            d["Signature"] = self.Signature
        return d

    @classmethod
    def parse(cls, value: Union["Msg", Mapping[str, Any], str, bytes]) -> "Msg":
        """Parse a Msg from another Msg, a wire-format dict, or JSON/YAML text."""
        if isinstance(value, cls):
            return value

        if isinstance(value, Mapping):
            return cls.from_dict(_normalize_wire_value(dict(value)))

        if isinstance(value, bytes):
            value = value.decode("utf-8")

        if isinstance(value, str):
            try:
                loaded = json.loads(value)
            except json.JSONDecodeError:
                loaded = yaml.safe_load(value)

            if isinstance(loaded, cls):
                return loaded
            if isinstance(loaded, Mapping):
                return cls.from_dict(_normalize_wire_value(dict(loaded)))
            raise TypeError("Parsed message must be a mapping")

        raise TypeError("Msg.parse() expects a Msg, mapping, str, or bytes")

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Msg":
        h = d["Header"]
        return cls(
            From=h["From"],
            To=h["To"],
            Subject=h["Subject"],
            Selector=h["Selector"],
            Body=d["Body"],
            Correlation=h["Correlation"],
            Timestamp=h["Timestamp"],
            Schema=h["Schema"],
            Hash=d.get("Hash"),
            Signature=d.get("Signature"),
        )
