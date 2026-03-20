"""PollyWeb Domain — signing authority for outbound messages."""
import hashlib
from dataclasses import dataclass, replace
from typing import Any, Callable, Mapping, Optional
import urllib.error
import urllib.request
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

from pollyweb.dns import fetch_dkim_entries, fetch_dkim_entry, signature_algorithm_for_dkim_record
from pollyweb.keypair import KeyPair
from pollyweb.manifest import Manifest, ManifestValidationError
from pollyweb.msg import Msg, normalize_domain_name
from pollyweb._crypto import encode_signature, sign_message

@dataclass
class Domain:
    Name: str
    Selector: str = ""
    KeyPair: Optional[KeyPair] = None
    Signer: Optional[Callable[[bytes], bytes]] = None

    @staticmethod
    def _manifest_payload(
        response: Any,
        *,
        domain: str
    ) -> Mapping[str, Any]:
        """Extract a manifest mapping from a PollyWeb manifest response."""

        if isinstance(response, Msg):
            payload = response.Body
        elif isinstance(response, Mapping):
            if isinstance(response.get("Response"), Mapping):
                payload = response["Response"]
            else:
                payload = response
        else:
            raise RuntimeError(f"Unexpected manifest response type: {type(response).__name__}")

        if not isinstance(payload, Mapping):
            raise RuntimeError("Manifest response body must be a mapping")

        normalized = dict(payload)
        about = normalized.get("About")
        if isinstance(about, Mapping) and "Domain" not in about:
            normalized["About"] = {
                "Domain": domain,
                **dict(about),
            }

        return normalized

    def fetch_manifest(
        self,
        domain: str = "",
    ) -> Manifest:
        """Load the manifest for *domain* using the built-in `Manifest@Domain` message."""

        # Support both ``Domain(name).fetch_manifest()`` and the legacy
        # ``Domain.fetch_manifest(name)`` calling style.
        if isinstance(self, Domain):
            resolved_domain = domain or self.Name
        else:
            resolved_domain = domain or self

        try:
            manifest_domain = normalize_domain_name(resolved_domain)
            response = Msg(
                From = "Anonymous",
                To = manifest_domain,
                Subject = "Manifest@Domain",
                Body = {},
            ).send()
            return Manifest.parse(
                self._manifest_payload(
                    response,
                    domain = manifest_domain,
                )
            )
        except (
            urllib.error.URLError,
            urllib.error.HTTPError,
            ManifestValidationError,
            RuntimeError,
        ) as err:
            raise RuntimeError(f"Unable to load manifest for {resolved_domain}: {err}") from err

    def _signature_algorithm(self, dkim_record: str) -> str:
        """Return the signing algorithm declared by the sender's DKIM record."""
        return signature_algorithm_for_dkim_record(dkim_record)

    def _signed_msg(
        self,
        msg: Msg,
        signer: Callable[[bytes, str], bytes],
        *,
        signature_algorithm: str
    ) -> Msg:
        """Return *msg* with hash and signature fields populated."""

        canonical = msg.canonical()
        signature = signer(canonical, signature_algorithm)

        return replace(
            msg,
            Hash = hashlib.sha256(canonical).hexdigest(),
            Signature = encode_signature(signature))

    def dns(self):
        """Return ``{selector: txt}`` for publishing this domain's DKIM key.

        Probes ``pw{n}._domainkey.pw.{Name}`` starting at n=1 until NXDOMAIN,
        then applies the following logic:

        - No entries found → ``{"pw1": <TXT for current key>}``.
        - Last entry matches current public key → returns existing selector + TXT.
        - Last entry differs → ``{"pw{last+1}": <TXT for current key>}``,
          unless the current key already appears in an older entry, which raises
          ``ValueError`` (reusing a revoked key is not allowed).
        """
        if self.KeyPair is None:
            if not self.Selector:
                raise ValueError("Selector is required when Domain has no KeyPair.")
            return {self.Selector: ""}

        entries = fetch_dkim_entries(self.Name, require_dnssec=False)

        current_raw = self.KeyPair.PublicKey.public_bytes(Encoding.Raw, PublicFormat.Raw)

        if not entries:
            return {"pw1": self.KeyPair.dkim()}

        last_selector, last_raw, last_txt = entries[-1]

        if last_raw == current_raw:
            return {last_selector: last_txt}

        for sel, raw, _ in entries:
            if raw == current_raw:
                raise ValueError(
                    f"Public key already used in DKIM entry '{sel}' for {self.Name}; "
                    "reusing a revoked key is not allowed"
                )

        last_num = int(last_selector[2:])
        return {f"pw{last_num + 1}": self.KeyPair.dkim()}

    def sign(self, msg: Msg) -> Msg:
        """Return a new Msg with From/Selector derived from this domain and a signature."""
        dkim_entries = self.dns()
        selector, dkim_record = next(iter(dkim_entries.items()))
        prepared = replace(msg, From=self.Name, Selector=selector)

        if self.KeyPair is not None:
            algorithm = self._signature_algorithm(dkim_record)
            return self._signed_msg(
                prepared,
                lambda canonical, selected_algorithm: sign_message(
                    self.KeyPair.PrivateKey,
                    canonical,
                    signature_algorithm = selected_algorithm,
                )[0],
                signature_algorithm = algorithm,
            )

        if self.Signer is None:
            raise ValueError("Domain requires either KeyPair or Signer to sign messages.")

        if not dkim_record:
            lookup = fetch_dkim_entry(self.Name, selector, require_dnssec = False)
            if lookup is None:
                raise ValueError(
                    f"Missing DKIM TXT at {selector}._domainkey.pw.{self.Name}; cannot determine signature algorithm."
                )
            _, _, dkim_record = lookup

        algorithm = self._signature_algorithm(dkim_record)

        return self._signed_msg(
            prepared,
            lambda canonical, selected_algorithm: self.Signer(canonical),
            signature_algorithm = algorithm,
        )

    def send(self, msg: Msg):
        """Sign *msg*, POST it to the receiver inbox, and return the parsed response.

        Returns a ``Msg``, ``dict``, or ``str`` — see ``Msg.send()`` for details.
        """
        signed = self.sign(msg)
        return signed.send()
