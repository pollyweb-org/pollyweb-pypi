"""PollyWeb Domain — signing authority for outbound messages."""
import hashlib
from dataclasses import dataclass, replace
from typing import Callable, Optional
import urllib.error
import urllib.request
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

from pollyweb.dns import fetch_dkim_entries, fetch_dkim_entry, signature_algorithm_for_dkim_record
from pollyweb.keypair import KeyPair
from pollyweb.manifest import Manifest, ManifestValidationError
from pollyweb.msg import Msg
from pollyweb._crypto import encode_signature, sign_message

MANIFEST_URLS = (
    "https://{domain}/manifest",
    "https://{domain}/manifest.yaml",
    "https://{domain}/.well-known/pollyweb/manifest",
    "https://{domain}/.well-known/pollyweb/manifest.yaml",
    "https://pw.{domain}/manifest",
    "https://pw.{domain}/manifest.yaml",
)


@dataclass
class Domain:
    Name: str
    Selector: str = ""
    KeyPair: Optional[KeyPair] = None
    Signer: Optional[Callable[[bytes], bytes]] = None

    @staticmethod
    def _fetch_url_bytes(
        url: str
    ) -> bytes:
        """Fetch raw manifest bytes from *url*."""

        request = urllib.request.Request(
            url,
            headers = {
                "Accept": "application/json, application/yaml, text/yaml, text/plain"},
        )

        with urllib.request.urlopen(
            request,
            timeout = 10,
        ) as response:
            return response.read()

    def fetch_manifest(
        self,
        domain: str = "",
        *,
        manifest_urls: tuple[str, ...] = MANIFEST_URLS
    ) -> Manifest:
        """Load the manifest for *domain* using PollyWeb URL guesses."""

        # Support both ``Domain(name).fetch_manifest()`` and the legacy
        # ``Domain.fetch_manifest(name)`` calling style.
        if isinstance(self, Domain):
            resolved_domain = domain or self.Name
        else:
            resolved_domain = domain or self

        last_error: Exception | None = None

        for template in manifest_urls:
            url = template.format(domain = resolved_domain)

            try:
                raw_manifest = Domain._fetch_url_bytes(url)
                return Manifest.parse(raw_manifest)
            except (
                urllib.error.URLError,
                urllib.error.HTTPError,
                ManifestValidationError,
            ) as err:
                last_error = err

        raise RuntimeError(f"Unable to load manifest for {resolved_domain}: {last_error}")

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
