"""PollyWeb Message Msg — create, sign, and validate."""

import base64
import hashlib
import json
import uuid
from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)

SCHEMA = "pollyweb.org/MSG:1.0"


def _utc_now() -> str:
    ts = datetime.now(timezone.utc)
    return ts.strftime("%Y-%m-%dT%H:%M:%S.") + f"{ts.microsecond // 1000:03d}Z"


class MsgValidationError(Exception):
    """Raised when msg validation fails."""


@dataclass(frozen=True)
class Msg:
    To: str
    Subject: str
    From: str = ""
    DKIM: str = ""
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
                "DKIM": self.DKIM,
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

    def validate(self, public_key: Ed25519PublicKey) -> bool:
        """Validate structure and signature. Raises MsgValidationError on failure."""
        # -- schema --
        if self.Schema != SCHEMA:
            raise MsgValidationError(f"Unsupported schema: {self.Schema}")

        # -- required fields --
        for field_name, value in [
            ("From", self.From),
            ("To", self.To),
            ("Subject", self.Subject),
            ("Correlation", self.Correlation),
            ("Timestamp", self.Timestamp),
            ("DKIM", self.DKIM),
        ]:
            if not value:
                raise MsgValidationError(f"Missing {field_name}")

        # -- hash & signature present --
        if self.Hash is None:
            raise MsgValidationError("Missing Hash")
        if self.Signature is None:
            raise MsgValidationError("Missing Signature")

        # -- recompute hash --
        canonical = self.canonical()
        if self.Hash != hashlib.sha256(canonical).hexdigest():
            raise MsgValidationError("Hash mismatch")

        # -- verify Ed25519 signature --
        try:
            sig_bytes = base64.b64decode(self.Signature)
        except Exception as exc:
            raise MsgValidationError(f"Malformed signature: {exc}") from exc

        try:
            public_key.verify(sig_bytes, canonical)
        except InvalidSignature:
            raise MsgValidationError("Invalid signature")

        return True

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {
            "Header": {
                "From": self.From,
                "To": self.To,
                "Subject": self.Subject,
                "Correlation": self.Correlation,
                "Timestamp": self.Timestamp,
                "DKIM": self.DKIM,
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
    def from_dict(cls, d: Dict[str, Any]) -> "Msg":
        h = d["Header"]
        return cls(
            From=h["From"],
            To=h["To"],
            Subject=h["Subject"],
            DKIM=h["DKIM"],
            Body=d["Body"],
            Correlation=h["Correlation"],
            Timestamp=h["Timestamp"],
            Schema=h["Schema"],
            Hash=d.get("Hash"),
            Signature=d.get("Signature"),
        )
