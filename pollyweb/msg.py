"""PollyWeb Message Msg — create, sign, and validate."""

import base64
import hashlib
import json
import re
import urllib.request
import uuid
from dataclasses import dataclass, field, replace
from datetime import date, datetime, timezone
from typing import Any, Dict, Mapping, Optional, Union

from cryptography.exceptions import InvalidSignature
import yaml

from pollyweb._crypto import (
    canonical_signature_algorithm,
    load_dkim_public_key,
    sign_message,
    signature_algorithm_for_private_key,
    signature_algorithm_for_public_key,
    verify_signature,
)
from pollyweb.dns import dkim_dns_name, pollyweb_domain, validate_pollyweb_branch
from pollyweb.schema import Schema

SCHEMA = Schema("pollyweb.org/MSG:1.0")


_DOMAIN_RE = re.compile(
    r"^(?=.{1,253}$)(?:[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?\.)+"
    r"(?:[A-Za-z]{2,63}|xn--[A-Za-z0-9-]{1,59})$"
)
_Z_TIMESTAMP_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{3})?Z$"
)


def _is_domain_name(value: str) -> bool:
    """Return True when *value* is a syntactically valid domain name."""
    return bool(_DOMAIN_RE.fullmatch(value))


def _is_uuid_string(value: str) -> bool:
    """Return True when *value* is a syntactically valid UUID string."""
    try:
        uuid.UUID(value)
    except (ValueError, AttributeError, TypeError):
        return False
    return True


def _is_z_timestamp(value: str) -> bool:
    """Return True when *value* is an ISO-8601 UTC timestamp ending in Z."""
    if not isinstance(value, str) or not _Z_TIMESTAMP_RE.fullmatch(value):
        return False
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return True


def _resolve_dkim_public_key(domain: str, selector: str) -> tuple[object, str]:
    """Fetch the public key from the DKIM DNS TXT record.

    Validates the ``pw.{domain}`` PollyWeb branch, then queries
    ``{selector}._domainkey.pw.{domain}`` for a TXT record in the standard DKIM
    wire format: ``v=DKIM1; k=<key-type>; p=<base64>``.

    Raises ``MsgValidationError`` if:
    - the DNS lookup fails,
    - DNSSEC is not enabled / the AD flag is not set on the response, or
    - no supported public key is found in the TXT records.
    """
    import dns.flags
    import dns.resolver

    branch = pollyweb_domain(domain)
    dns_name = dkim_dns_name(domain, selector)
    try:
        resolver = dns.resolver.Resolver()
        resolver.use_edns(edns=0, ednsflags=dns.flags.DO, payload=4096)
        try:
            validate_pollyweb_branch(resolver, domain)
        except ValueError as exc:
            raise MsgValidationError(
                f"DNSSEC validation failed for {branch}: cannot trust PollyWeb branch ({exc})"
            ) from exc
        answers = resolver.resolve(dns_name, "TXT")
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
        version = params.get("v", "")
        if version and version != "DKIM1":
            continue
        key_algorithm = params.get("k", "")
        p = params.get("p", "")
        if not key_algorithm or not p:
            continue
        try:
            return load_dkim_public_key(key_algorithm, p), key_algorithm
        except Exception as exc:
            raise MsgValidationError(
                f"Invalid {key_algorithm} key in DKIM TXT at {dns_name}: {exc}"
            ) from exc

    raise MsgValidationError(f"No supported DKIM public key found in TXT at {dns_name}")


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


def _extract_msg_mapping(value: Mapping[str, Any]) -> Dict[str, Any]:
    """Return a PollyWeb wire mapping, unwrapping known transport envelopes."""
    def _parse_embedded_mapping(embedded: Any) -> Optional[Dict[str, Any]]:
        if isinstance(embedded, str):
            try:
                embedded = json.loads(embedded)
            except json.JSONDecodeError:
                try:
                    embedded = yaml.safe_load(embedded)
                except yaml.YAMLError:
                    return None

        if isinstance(embedded, Mapping):
            embedded_mapping = _normalize_wire_value(dict(embedded))
            if "Header" in embedded_mapping:
                return embedded_mapping

        return None

    normalized = _normalize_wire_value(dict(value))
    if "Header" in normalized:
        return normalized

    for field_name in ("detail", "Message"):
        embedded_mapping = _parse_embedded_mapping(normalized.get(field_name))
        if embedded_mapping is not None:
            return embedded_mapping

    records = normalized.get("Records")
    if isinstance(records, list):
        for record in records:
            if not isinstance(record, Mapping):
                continue
            embedded_mapping = _parse_embedded_mapping(record.get("body"))
            if embedded_mapping is not None:
                return embedded_mapping
            kinesis = record.get("kinesis")
            if isinstance(kinesis, Mapping):
                data = kinesis.get("data")
                if isinstance(data, str):
                    try:
                        data = base64.b64decode(data).decode("utf-8")
                    except Exception:
                        data = None
                    embedded_mapping = _parse_embedded_mapping(data)
                    if embedded_mapping is not None:
                        return embedded_mapping

    body = normalized.get("body")
    if body is not None:
        if normalized.get("isBase64Encoded") is True and isinstance(body, str):
            try:
                body = base64.b64decode(body).decode("utf-8")
            except Exception:
                body = None
        embedded_mapping = _parse_embedded_mapping(body)
        if embedded_mapping is not None:
            return embedded_mapping

    return normalized


class MsgValidationError(Exception):
    """Raised when msg validation fails."""


@dataclass(frozen=True)
class Msg:
    To: str
    Subject: str
    From: str = ""
    Selector: str = ""
    Algorithm: str = ""
    Body: Dict[str, Any] = field(default_factory=dict)
    Correlation: str = field(default_factory=lambda: str(uuid.uuid4()))
    Timestamp: str = field(default_factory=_utc_now)
    Schema: Schema = SCHEMA
    Hash: Optional[str] = None
    Signature: Optional[str] = None

    def __post_init__(self) -> None:
        if not _is_domain_name(self.To):
            raise MsgValidationError("To must be a domain string")
        if not isinstance(self.Subject, str):
            raise MsgValidationError("Subject must be a string")
        try:
            object.__setattr__(self, "Schema", self.Schema if isinstance(self.Schema, Schema) else Schema(self.Schema))
        except (TypeError, ValueError) as exc:
            raise MsgValidationError(str(exc)) from exc
        if self.Algorithm:
            try:
                object.__setattr__(self, "Algorithm", canonical_signature_algorithm(self.Algorithm))
            except ValueError as exc:
                raise MsgValidationError(str(exc)) from exc
        if not _is_uuid_string(self.Correlation):
            raise MsgValidationError("Correlation must be a UUID")
        if not _is_z_timestamp(self.Timestamp):
            raise MsgValidationError("Timestamp must be a Z timestamp")
        if self.From not in ("", "Anonymous") and not _is_domain_name(self.From) and not _is_uuid_string(self.From):
            raise MsgValidationError(
                "From must be empty, Anonymous, a domain string, or a UUID"
            )

    def _effective_from(self) -> str:
        """Return the sender name used on the wire and in canonicalization."""
        return self.From or "Anonymous"

    def canonical(self) -> bytes:
        """Return the canonical JCS JSON bytes of schema + header + body."""
        header = {
            "Correlation": self.Correlation,
            "From": self._effective_from(),
            "Schema": self.Schema,
            "Subject": self.Subject,
            "Timestamp": self.Timestamp,
            "To": self.To,
        }
        if self.Selector:
            header["Selector"] = self.Selector
        if self.Algorithm:
            header["Algorithm"] = self.Algorithm

        payload = {
            "Body": self.Body,
            "Header": header,
        }
        return json.dumps(
            payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
        ).encode("utf-8")

    def sign(self, private_key: object) -> "Msg":
        """Compute hash and sign this msg. Returns a new signed Msg."""
        try:
            algorithm = (
                canonical_signature_algorithm(self.Algorithm)
                if self.Algorithm
                else signature_algorithm_for_private_key(private_key)
            )
        except (TypeError, ValueError) as exc:
            raise MsgValidationError(str(exc)) from exc
        msg = replace(self, Algorithm=algorithm)
        canonical = msg.canonical()
        hash_hex = hashlib.sha256(canonical).hexdigest()
        try:
            signature_bytes, _ = sign_message(
                private_key,
                canonical,
                signature_algorithm=algorithm,
            )
        except (TypeError, ValueError) as exc:
            raise MsgValidationError(str(exc)) from exc
        sig_b64 = base64.b64encode(signature_bytes).decode("ascii")
        return replace(msg, Hash=hash_hex, Signature=sig_b64)

    def _validate_schema(self) -> None:
        if self.Schema != SCHEMA:
            raise MsgValidationError(f"Unsupported schema: {self.Schema}")

    def _validate_required_fields(self, *, require_selector: bool) -> None:
        required_fields = [
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

    def verify(self, public_key: Optional[object] = None) -> bool:
        """Validate structure, canonical hash, and signature.

        If *public_key* is omitted, the key is fetched from DNS using the
        selector and the From domain: ``{Selector}._domainkey.pw.{From}`` (TXT record,
        DKIM wire format: ``v=DKIM1; k=<key-type>; p=<base64>``).
        """
        self._validate_schema()
        self._validate_required_fields(require_selector=public_key is None)
        canonical = self._validate_hash()

        if self.Signature is None:
            raise MsgValidationError("Missing Signature")

        key_type = None
        if public_key is None:
            public_key, key_type = _resolve_dkim_public_key(self.From, self.Selector)

        try:
            sig_bytes = base64.b64decode(self.Signature)
        except Exception as exc:
            raise MsgValidationError(f"Malformed signature: {exc}") from exc

        signature_algorithm = self.Algorithm or None
        if public_key is not None and signature_algorithm is None:
            signature_algorithm = signature_algorithm_for_public_key(public_key)

        try:
            verify_signature(
                public_key,
                sig_bytes,
                canonical,
                signature_algorithm=signature_algorithm,
                key_type=key_type,
            )
        except InvalidSignature:
            raise MsgValidationError("Invalid signature")
        except (TypeError, ValueError) as exc:
            raise MsgValidationError(str(exc)) from exc

        return True

    def validate_signature(self, public_key: Optional[object] = None) -> bool:
        """Backward-compatible alias for :meth:`verify`."""
        return self.verify(public_key)

    def send(self):
        """Validate this message, POST it to the receiver inbox, and return the HTTP response."""
        self.verify()
        url = f"https://pw.{self.To}/inbox"
        body = json.dumps(self.to_dict(), separators=(",", ":")).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        return urllib.request.urlopen(req)

    def to_dict(self) -> Dict[str, Any]:
        header: Dict[str, Any] = {
            "From": self._effective_from(),
            "To": self.To,
            "Subject": self.Subject,
            "Correlation": self.Correlation,
            "Timestamp": self.Timestamp,
            "Schema": self.Schema,
        }
        if self.Selector:
            header["Selector"] = self.Selector
        if self.Algorithm:
            header["Algorithm"] = self.Algorithm

        d: Dict[str, Any] = {
            "Header": header,
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
            return cls.from_dict(_extract_msg_mapping(value))

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
                return cls.from_dict(_extract_msg_mapping(loaded))
            raise TypeError("Parsed message must be a mapping")

        raise TypeError("Msg.parse() expects a Msg, mapping, str, or bytes")

    @classmethod
    def load(cls, value: Union["Msg", Mapping[str, Any], str, bytes]) -> "Msg":
        """Backward-compatible alias for :meth:`parse`."""
        return cls.parse(value)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Msg":
        h = d["Header"]
        return cls(
            From=h.get("From") or "Anonymous",
            To=h["To"],
            Subject=h["Subject"],
            Selector=h.get("Selector", ""),
            Algorithm=h.get("Algorithm", ""),
            Body=d.get("Body", {}),
            Correlation=h["Correlation"],
            Timestamp=h["Timestamp"],
            Schema=h["Schema"],
            Hash=d.get("Hash"),
            Signature=d.get("Signature"),
        )
