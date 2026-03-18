
"""PollyWeb Message Msg — create, validate, and transport."""

import base64
import hashlib
import json
import re
import urllib.request
import uuid
from dataclasses import dataclass, replace
from datetime import date, datetime, timezone
from typing import Any, Dict, Mapping, Optional, Union

from cryptography.exceptions import InvalidSignature
import yaml

from pollyweb._crypto import (
    canonical_signature_algorithm,
    decode_ascii_envelope,
    encode_dkim_public_key,
    load_dkim_public_key,
    signature_algorithm_for_public_key,
    verify_signature,
)
from pollyweb.dns import (
    DnsLookupError,
    DnsVerificationDiagnostics,
    dkim_dns_name,
    resolve_dkim_with_dnssec,
)
from pollyweb._crypto import signature_algorithm_for_dkim_key_type
from pollyweb.schema import Schema
from pollyweb.struct import Struct

SCHEMA = Schema("pollyweb.org/MSG:1.0")


_DOMAIN_RE = re.compile(
    r"^(?=.{1,253}$)(?:[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?\.)+"
    r"(?:[A-Za-z]{2,63}|xn--[A-Za-z0-9-]{1,59})$"
)
_Z_TIMESTAMP_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{3})?Z$"
)
_POLLYWEB_DOMAIN_ALIAS_SUFFIX = ".dom"
_POLLYWEB_DOMAIN_CANONICAL_SUFFIX = ".pollyweb.org"
_DEFAULT_WIRE_FIELDS = frozenset({"Body", "Hash", "Header", "Signature"})


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


def normalize_domain_name(value: str) -> str:
    """
    Normalize supported PollyWeb domain aliases to canonical hostnames.
    Don't call this directly - instead, use Domain.send() or Wallet.send()
    """

    stripped = value.strip()
    if stripped.endswith(_POLLYWEB_DOMAIN_ALIAS_SUFFIX):
        return (
            stripped[: -len(_POLLYWEB_DOMAIN_ALIAS_SUFFIX)]
            + _POLLYWEB_DOMAIN_CANONICAL_SUFFIX
        )
    return stripped


def _omit_algorithm_for_domain_sender(
    from_value: str
) -> bool:
    """Return whether the wire format should omit ``Header.Algorithm``."""

    return from_value not in ("", "Anonymous") and _is_domain_name(from_value)


def _resolve_dkim_public_key(
    domain: str,
    selector: str
) -> tuple[object, str, DnsVerificationDiagnostics]:
    """Fetch the public key from the DKIM DNS TXT record.

    Validates the ``pw.{domain}`` PollyWeb branch, then queries
    ``{selector}._domainkey.pw.{domain}`` for a TXT record in the standard DKIM
    wire format: ``v=DKIM1; k=<key-type>; p=<base64>``.

    Raises ``MsgValidationError`` if:
    - the DNS lookup fails,
    - no trusted resolver can return a DNSSEC-validated answer, or
    - no supported public key is found in the TXT records.
    """
    dns_name = dkim_dns_name(domain, selector)
    try:
        answers, dns_diagnostics = resolve_dkim_with_dnssec(
            domain,
            selector)
    except DnsLookupError as exc:
        raise MsgValidationError(
            str(exc),
            dns_diagnostics = exc.dns_diagnostics) from exc
    except Exception as exc:
        raise MsgValidationError(f"DKIM lookup failed for {dns_name}: {exc}") from exc

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
            return load_dkim_public_key(key_algorithm, p), key_algorithm, dns_diagnostics
        except Exception as exc:
            raise MsgValidationError(
                f"Invalid {key_algorithm} key in DKIM TXT at {dns_name}: {exc}",
                dns_diagnostics = dns_diagnostics
            ) from exc

    raise MsgValidationError(
        f"No supported DKIM public key found in TXT at {dns_name}",
        dns_diagnostics = dns_diagnostics)


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


def _validate_wire_fields(
    mapping: Mapping[str, Any],
    *,
    allowed_top_level_fields: Optional[set[str] | frozenset[str]] = None
) -> None:
    """Reject unexpected top-level wire fields when a policy is provided."""

    if allowed_top_level_fields is None:
        return

    unexpected_fields = sorted(
        set(mapping.keys()) - set(allowed_top_level_fields))
    if unexpected_fields:
        joined_fields = ", ".join(unexpected_fields)
        expected_fields = ", ".join(sorted(allowed_top_level_fields))
        raise MsgValidationError(
            f"Unexpected top-level field(s): {joined_fields}. "
            f"Expected only {expected_fields}."
        )


class MsgValidationError(Exception):
    """Raised when msg validation fails."""

    def __init__(
        self,
        message: str,
        *,
        dns_diagnostics: DnsVerificationDiagnostics | None = None
    ) -> None:
        """Store an optional DNS verification snapshot with the error."""

        super().__init__(message)
        self.dns_diagnostics = dns_diagnostics


@dataclass(frozen=True)
class VerificationDetails:
    """Structured details describing what ``Msg.verify_details()`` validated."""

    schema: str
    required_headers_present: bool
    hash_valid: bool
    signature_valid: bool
    dns_lookup_used: bool
    from_value: str
    to_value: str
    subject: str
    correlation: str
    selector: str
    algorithm: str
    dns_diagnostics: Optional[DnsVerificationDiagnostics] = None



@dataclass(frozen=True, init=False)
class Msg(Struct):
    To: str
    Subject: str
    From: str
    Selector: str
    Algorithm: str
    Body: Any
    Correlation: str
    Timestamp: str
    Schema: Schema
    Hash: Optional[str]
    Signature: Optional[str]

    def __init__(
        self,
        To: Union[str, "Msg", Mapping[str, Any], bytes],
        Subject: Optional[str] = None,
        *,
        From: str = "",
        Selector: str = "",
        Algorithm: str = "",
        Body: Any = None,
        Correlation: str = None,
        Timestamp: str = None,
        Schema: "Schema" = SCHEMA,
        Hash: Optional[str] = None,
        Signature: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Initialize a Msg from fields or parse a single raw/enveloped input."""

        if Subject is None and not isinstance(To, str):
            parsed = type(self).parse(To)
            self._copy_from_msg(parsed)
            return

        # Merge any extra keyword arguments into Body as convenience shorthand.
        if Body is None:
            merged_body: Any = {}
        elif isinstance(Body, Mapping):
            merged_body = dict(Body)
        elif isinstance(Body, Struct):
            merged_body = Body.to_dict()
        elif isinstance(Body, str):
            if kwargs:
                raise MsgValidationError("Body string cannot be merged with extra keyword arguments")
            merged_body = Body
        else:
            raise MsgValidationError("Body must be a mapping or a string")

        if kwargs:
            if not isinstance(merged_body, dict):
                raise MsgValidationError("Body must be a mapping when extra keyword arguments are provided")
            merged_body.update(kwargs)

        object.__setattr__(self, "To", To)
        object.__setattr__(self, "Subject", Subject)
        object.__setattr__(self, "From", From)
        object.__setattr__(self, "Selector", Selector)
        object.__setattr__(self, "Algorithm", Algorithm)
        object.__setattr__(self, "Body", Struct.wrap(merged_body))
        object.__setattr__(self, "Correlation", Correlation if Correlation is not None else str(uuid.uuid4()))
        object.__setattr__(self, "Timestamp", Timestamp if Timestamp is not None else _utc_now())
        object.__setattr__(self, "Schema", Schema)
        object.__setattr__(self, "Hash", Hash)
        object.__setattr__(self, "Signature", Signature)
        self.__post_init__()

    def _copy_from_msg(
        self,
        other: "Msg"
    ) -> None:
        """Copy all normalized fields from another Msg instance into this one."""

        object.__setattr__(self, "To", other.To)
        object.__setattr__(self, "Subject", other.Subject)
        object.__setattr__(self, "From", other.From)
        object.__setattr__(self, "Selector", other.Selector)
        object.__setattr__(self, "Algorithm", other.Algorithm)
        object.__setattr__(self, "Body", other.Body)
        object.__setattr__(self, "Correlation", other.Correlation)
        object.__setattr__(self, "Timestamp", other.Timestamp)
        object.__setattr__(self, "Schema", other.Schema)
        object.__setattr__(self, "Hash", other.Hash)
        object.__setattr__(self, "Signature", other.Signature)

    def __post_init__(self) -> None:
        if not _is_domain_name(self.To):
            raise MsgValidationError("To must be a domain string")
        if not isinstance(self.Subject, str):
            raise MsgValidationError("Subject must be a string")
        from_is_domain = self.From not in ("", "Anonymous") and _is_domain_name(self.From)
        try:
            object.__setattr__(self, "Schema", self.Schema if isinstance(self.Schema, Schema) else Schema(self.Schema))
        except (TypeError, ValueError) as exc:
            raise MsgValidationError(str(exc)) from exc
        if self.Algorithm:
            try:
                object.__setattr__(self, "Algorithm", canonical_signature_algorithm(self.Algorithm))
            except ValueError as exc:
                raise MsgValidationError(str(exc)) from exc
        if from_is_domain and self.Algorithm:
            raise MsgValidationError("Algorithm must be empty for domain senders")
        if not _is_uuid_string(self.Correlation):
            raise MsgValidationError("Correlation must be a UUID")
        if not _is_z_timestamp(self.Timestamp):
            raise MsgValidationError("Timestamp must be a Z timestamp")
        if self.From not in ("", "Anonymous") and not _is_domain_name(self.From) and not _is_uuid_string(self.From):
            raise MsgValidationError(
                "From must be empty, Anonymous, a domain string, or a UUID"
            )
        if not isinstance(self.Body, (Struct, str)):
            raise MsgValidationError("Body must be a mapping or a string")

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
            "Body": Struct.unwrap(self.Body),
            "Header": header,
        }
        return json.dumps(
            payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
        ).encode("utf-8")

    def _validate_schema(self) -> None:
        if self.Schema != SCHEMA:
            raise MsgValidationError(f"Unsupported schema: {self.Schema}")

    def _validate_required_fields(self, *, require_selector: bool, require_from: bool) -> None:
        required_fields = [
            ("To", self.To),
            ("Subject", self.Subject),
            ("Correlation", self.Correlation),
            ("Timestamp", self.Timestamp),
        ]
        if require_from:
            required_fields.append(("From", self.From))
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
        self._validate_required_fields(require_selector=False, require_from=True)
        self._validate_hash()
        return True

    def _validate_expected_fields(
        self,
        *,
        expected_from: Optional[str] = None,
        expected_to: Optional[str] = None,
        allowed_to_values: Optional[set[str]] = None,
        expected_subject: Optional[str] = None,
        expected_correlation: Optional[str] = None
    ) -> None:
        """Validate optional caller-provided expectations about signed headers."""

        if expected_from is not None and self.From != expected_from:
            raise MsgValidationError(f"Unexpected From value: {self.From}")

        if expected_subject is not None and self.Subject != expected_subject:
            raise MsgValidationError(f"Unexpected Subject: {self.Subject}")

        if expected_correlation is not None and self.Correlation != expected_correlation:
            raise MsgValidationError(
                f"Unexpected Correlation: {self.Correlation}")

        valid_to_values = (
            set(allowed_to_values)
            if allowed_to_values is not None
            else ({expected_to} if expected_to is not None else None)
        )
        if valid_to_values is not None and self.To not in valid_to_values:
            raise MsgValidationError(f"Unexpected To value: {self.To}")

    def verify(
        self,
        public_key: Optional[object] = None,
        *,
        expected_from: Optional[str] = None,
        expected_to: Optional[str] = None,
        allowed_to_values: Optional[set[str]] = None,
        expected_subject: Optional[str] = None,
        expected_correlation: Optional[str] = None
    ) -> bool:
        """Validate structure, canonical hash, signature, and optional expectations.

        Optional expected values let callers enforce subject- or flow-specific
        header constraints after the signed payload is verified.
        """

        self.verify_details(
            public_key,
            expected_from = expected_from,
            expected_to = expected_to,
            allowed_to_values = allowed_to_values,
            expected_subject = expected_subject,
            expected_correlation = expected_correlation)
        return True

    def verify_details(
        self,
        public_key: Optional[object] = None,
        *,
        expected_from: Optional[str] = None,
        expected_to: Optional[str] = None,
        allowed_to_values: Optional[set[str]] = None,
        expected_subject: Optional[str] = None,
        expected_correlation: Optional[str] = None
    ) -> VerificationDetails:
        """Validate the message and return structured verification details."""
        self._validate_schema()
        dns_lookup_used = public_key is None
        self._validate_required_fields(require_selector=dns_lookup_used, require_from=True)
        canonical = self._validate_hash()

        if self.Signature is None:
            raise MsgValidationError("Missing Signature")

        key_type = None
        dns_diagnostics = None
        if dns_lookup_used:
            public_key, key_type, dns_diagnostics = _resolve_dkim_public_key(
                self.From,
                self.Selector)

        try:
            sig_bytes = base64.b64decode(self.Signature)
        except Exception as exc:
            raise MsgValidationError(f"Malformed signature: {exc}") from exc

        signature_algorithm = self.Algorithm or None
        if dns_lookup_used and key_type is not None:
            dns_algorithm = signature_algorithm_for_dkim_key_type(key_type)
            if signature_algorithm is not None and signature_algorithm != dns_algorithm:
                raise MsgValidationError(
                    f"Signature algorithm {signature_algorithm} does not match DKIM algorithm {dns_algorithm}"
                )
            signature_algorithm = dns_algorithm
        elif public_key is not None and signature_algorithm is None:
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
            raise MsgValidationError(
                "Invalid signature",
                dns_diagnostics = dns_diagnostics)
        except (TypeError, ValueError) as exc:
            raise MsgValidationError(
                str(exc),
                dns_diagnostics = dns_diagnostics) from exc

        self._validate_expected_fields(
            expected_from = expected_from,
            expected_to = expected_to,
            allowed_to_values = allowed_to_values,
            expected_subject = expected_subject,
            expected_correlation = expected_correlation)

        return VerificationDetails(
            schema=str(self.Schema),
            required_headers_present=True,
            hash_valid=True,
            signature_valid=True,
            dns_lookup_used=dns_lookup_used,
            from_value=self.From,
            to_value=self.To,
            subject=self.Subject,
            correlation=self.Correlation,
            selector=self.Selector,
            algorithm=signature_algorithm or "",
            dns_diagnostics=dns_diagnostics,
        )

    def validate_signature(self, public_key: Optional[object] = None) -> bool:
        """Backward-compatible alias for :meth:`verify`."""
        return self.verify(public_key)

    def send(self):
        """Validate this message, POST it to the receiver inbox, and return the parsed response.

        When ``From`` is a domain name, signature is verified via DKIM DNS.
        When ``From`` is ``"Anonymous"`` and the message is unsigned, only basic
        envelope structure is validated before sending. When ``From`` is
        ``"Anonymous"`` or a UUID and the message already carries ``Hash`` or
        ``Signature``, structure and hash are validated without DNS lookup.

        The response body is parsed automatically:
        - Returns a ``Msg`` if the server replies with a PollyWeb message.
        - Returns a ``dict`` if the response is JSON but not a valid ``Msg``.
        - Returns a ``str`` if the response body is not valid JSON.

        Don't call this directly - instead, use Domain.send() or Wallet.send()
        """
        if _is_domain_name(self._effective_from()):
            self.verify()
        elif self.Hash is None and self.Signature is None:
            self._validate_schema()
            self._validate_required_fields(
                require_selector = False,
                require_from = self._effective_from() != "Anonymous")
        else:
            self.validate_unsigned()
        normalized_to = normalize_domain_name(self.To)
        url = f"https://pw.{normalized_to}/inbox"
        body = json.dumps(self.to_dict(), separators=(",", ":")).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        resp = urllib.request.urlopen(req)
        raw = resp.read()
        # Parse the response body into a structured object rather than raw bytes.
        try:
            data = json.loads(raw)
        except (json.JSONDecodeError, UnicodeDecodeError):
            return raw.decode("utf-8", errors="replace")
        # Attempt to interpret the response as a PollyWeb Msg.
        try:
            return Msg.parse(data)
        except (TypeError, MsgValidationError, KeyError, ValueError):
            return data

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
            "Body": Struct.unwrap(self.Body),
        }
        if self.Hash is not None:
            d["Hash"] = self.Hash
        if self.Signature is not None:
            d["Signature"] = self.Signature
        return d

    @classmethod
    def parse(
        cls,
        value: Union["Msg", Mapping[str, Any], str, bytes],
        *,
        allowed_top_level_fields: Optional[set[str] | frozenset[str]] = None
    ) -> "Msg":
        """Parse a Msg from another Msg, a wire-format dict, or JSON/YAML text."""
        if isinstance(value, cls):
            return value

        if isinstance(value, Mapping):
            mapping = _extract_msg_mapping(value)
            _validate_wire_fields(
                mapping,
                allowed_top_level_fields = allowed_top_level_fields)
            return cls.from_dict(mapping)

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
                mapping = _extract_msg_mapping(loaded)
                _validate_wire_fields(
                    mapping,
                    allowed_top_level_fields = allowed_top_level_fields)
                return cls.from_dict(mapping)
            raise TypeError("Parsed message must be a mapping")

        raise TypeError("Msg.parse() expects a Msg, mapping, str, or bytes")

    @classmethod
    def load(
        cls,
        value: Union["Msg", Mapping[str, Any], str, bytes],
        *,
        allowed_top_level_fields: Optional[set[str] | frozenset[str]] = None
    ) -> "Msg":
        """Backward-compatible alias for :meth:`parse`."""
        return cls.parse(
            value,
            allowed_top_level_fields = allowed_top_level_fields)

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


def dkim_public_key_value(public_key: object) -> str:
    """Return the DKIM `p=` value for an Ed25519 public key."""
    return encode_dkim_public_key(public_key)


def decode_transport_bytes(value: str) -> bytes:
    """Decode an ASCII-armored transport payload into raw bytes."""
    return decode_ascii_envelope(value)


def decode_transport_text(value: str, *, errors: str = "strict") -> str:
    """Decode an ASCII-armored transport payload into text."""
    return decode_transport_bytes(value).decode("utf-8", errors=errors)
