"""PollyWeb Domain — signing authority for outbound messages."""

import base64
import json
from dataclasses import dataclass, replace

from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

from pollyweb.keypair import KeyPair
from pollyweb.msg import Msg


@dataclass
class Domain:
    Name: str
    KeyPair: KeyPair
    DKIM: str

    def dkim(self):
        """Return ``(selector, txt)`` for publishing this domain's DKIM key.

        Probes ``pw{n}._domainkey.pw.{Name}`` starting at n=1 until NXDOMAIN,
        then applies the following logic:

        - No entries found → ``("pw1", <TXT for current key>)``.
        - Last entry matches current public key → returns existing selector + TXT.
        - Last entry differs → ``("pw{last+1}", <TXT for current key>)``,
          unless the current key already appears in an older entry, which raises
          ``ValueError`` (reusing a revoked key is not allowed).
        """
        import dns.resolver

        def _fetch(selector):
            dns_name = f"{selector}._domainkey.pw.{self.Name}"
            try:
                answers = dns.resolver.resolve(dns_name, "TXT")
            except Exception:
                return None
            for rdata in answers:
                txt = b"".join(rdata.strings).decode("utf-8")
                params = {}
                for part in txt.split(";"):
                    part = part.strip()
                    if "=" in part:
                        k, v = part.split("=", 1)
                        params[k.strip()] = v.strip()
                p = params.get("p", "")
                if p:
                    try:
                        raw = base64.b64decode(p)
                        return selector, raw, txt
                    except Exception:
                        pass
            return None

        entries = []
        i = 1
        while True:
            result = _fetch(f"pw{i}")
            if result is None:
                break
            entries.append(result)
            i += 1

        current_raw = self.KeyPair.PublicKey.public_bytes(Encoding.Raw, PublicFormat.Raw)

        if not entries:
            return "pw1", self.KeyPair.dkim()

        last_selector, last_raw, last_txt = entries[-1]

        if last_raw == current_raw:
            return last_selector, last_txt

        for sel, raw, _ in entries:
            if raw == current_raw:
                raise ValueError(
                    f"Public key already used in DKIM entry '{sel}' for {self.Name}; "
                    "reusing a revoked key is not allowed"
                )

        last_num = int(last_selector[2:])
        return f"pw{last_num + 1}", self.KeyPair.dkim()

    def sign(self, msg: Msg) -> Msg:
        """Return a new Msg with From/DKIM set from this domain and Ed25519 signature."""
        return replace(msg, From=self.Name, DKIM=self.DKIM).sign(self.KeyPair.PrivateKey)

    def send(self, msg: Msg) -> Msg:
        """Sign *msg* and POST it to ``https://pw.{msg.To}/inbox``. Returns the signed Msg."""
        import urllib.request

        signed = self.sign(msg)
        url = f"https://pw.{msg.To}/inbox"
        body = json.dumps(signed.to_dict(), separators=(",", ":")).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req) as resp:
            resp.read()
        return signed
