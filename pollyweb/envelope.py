"""PollyWeb Message Envelope — create, sign, and validate."""

import base64
import hashlib
import json
import uuid
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)

SCHEMA = "pollyweb.org/MSG:1.0"


class EnvelopeValidationError(Exception):
    """Raised when envelope validation fails."""


@dataclass(frozen=True)
class Header:
    from_: str
    to: str
    subject: str
    correlation: str
    timestamp: str
    dkim: str

    def to_dict(self) -> Dict[str, str]:
        return {
            "From": self.from_,
            "To": self.to,
            "Subject": self.subject,
            "Correlation": self.correlation,
            "Timestamp": self.timestamp,
            "DKIM": self.dkim,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, str]) -> "Header":
        return cls(
            from_=d["From"],
            to=d["To"],
            subject=d["Subject"],
            correlation=d["Correlation"],
            timestamp=d["Timestamp"],
            dkim=d["DKIM"],
        )


@dataclass(frozen=True)
class Envelope:
    schema: str
    header: Header
    body: Dict[str, Any]
    hash: Optional[str] = None
    signature: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {
            "\U0001f91d": self.schema,
            "Header": self.header.to_dict(),
            "Body": self.body,
        }
        if self.hash is not None:
            d["Hash"] = self.hash
        if self.signature is not None:
            d["Signature"] = self.signature
        return d

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Envelope":
        return cls(
            schema=d["\U0001f91d"],
            header=Header.from_dict(d["Header"]),
            body=d["Body"],
            hash=d.get("Hash"),
            signature=d.get("Signature"),
        )


# ---------------------------------------------------------------------------
# Canonical payload (JCS-style: sorted keys, compact separators)
# ---------------------------------------------------------------------------

def _canonical_payload(envelope: Envelope) -> bytes:
    """Build the canonical JSON bytes of schema + header + body for hashing/signing."""
    payload = {
        "\U0001f91d": envelope.schema,
        "Body": envelope.body,
        "Header": envelope.header.to_dict(),
    }
    return json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
    ).encode("utf-8")


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def create_envelope(
    from_: str,
    to: str,
    subject: str,
    body: Dict[str, Any],
    *,
    correlation: Optional[str] = None,
    dkim: str = "pk1",
    timestamp: Optional[str] = None,
) -> Envelope:
    """Create a new unsigned envelope."""
    if correlation is None:
        correlation = str(uuid.uuid4())
    if timestamp is None:
        ts = datetime.now(timezone.utc)
        timestamp = ts.strftime("%Y-%m-%dT%H:%M:%S.") + f"{ts.microsecond // 1000:03d}Z"

    header = Header(
        from_=from_,
        to=to,
        subject=subject,
        correlation=correlation,
        timestamp=timestamp,
        dkim=dkim,
    )
    return Envelope(schema=SCHEMA, header=header, body=body)


def sign_envelope(
    envelope: Envelope,
    private_key: Ed25519PrivateKey,
) -> Envelope:
    """Compute hash and Ed25519-sign the envelope. Returns a new signed Envelope."""
    canonical = _canonical_payload(envelope)
    hash_hex = hashlib.sha256(canonical).hexdigest()
    sig_b64 = base64.b64encode(private_key.sign(canonical)).decode("ascii")
    return replace(envelope, hash=hash_hex, signature=sig_b64)


def validate_envelope(
    envelope: Envelope,
    public_key: Ed25519PublicKey,
) -> bool:
    """Validate structure and signature. Raises EnvelopeValidationError on failure."""
    # -- schema --
    if envelope.schema != SCHEMA:
        raise EnvelopeValidationError(f"Unsupported schema: {envelope.schema}")

    # -- required header fields --
    for field_name, value in [
        ("From", envelope.header.from_),
        ("To", envelope.header.to),
        ("Subject", envelope.header.subject),
        ("Correlation", envelope.header.correlation),
        ("Timestamp", envelope.header.timestamp),
        ("DKIM", envelope.header.dkim),
    ]:
        if not value:
            raise EnvelopeValidationError(f"Missing {field_name}")

    # -- hash & signature present --
    if envelope.hash is None:
        raise EnvelopeValidationError("Missing Hash")
    if envelope.signature is None:
        raise EnvelopeValidationError("Missing Signature")

    # -- recompute hash --
    canonical = _canonical_payload(envelope)
    expected_hash = hashlib.sha256(canonical).hexdigest()
    if envelope.hash != expected_hash:
        raise EnvelopeValidationError("Hash mismatch")

    # -- verify Ed25519 signature --
    try:
        sig_bytes = base64.b64decode(envelope.signature)
    except Exception as exc:
        raise EnvelopeValidationError(f"Malformed signature: {exc}") from exc

    try:
        public_key.verify(sig_bytes, canonical)
    except InvalidSignature:
        raise EnvelopeValidationError("Invalid signature")

    return True
