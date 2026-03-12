"""PollyWeb Domain — signing authority for outbound messages."""

import json
from dataclasses import dataclass, replace

from pollyweb.keypair import KeyPair
from pollyweb.msg import Msg


@dataclass
class Domain:
    Name: str
    KeyPair: KeyPair
    DKIM: str

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
