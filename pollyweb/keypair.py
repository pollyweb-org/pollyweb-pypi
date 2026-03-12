"""PollyWeb KeyPair — Ed25519 key pair generator."""

import base64
from dataclasses import dataclass, field

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat


def _generate_private() -> Ed25519PrivateKey:
    return Ed25519PrivateKey.generate()


@dataclass
class KeyPair:
    PrivateKey: Ed25519PrivateKey = field(default_factory=_generate_private)

    @property
    def PublicKey(self) -> Ed25519PublicKey:
        return self.PrivateKey.public_key()

    def dkim(self, v: str = "DKIM1") -> str:
        """Return the DKIM TXT record content for this key pair.

        The returned string is ready to publish as a DNS TXT record at
        ``{selector}._domainkey.pw.{domain}``.

        Example: ``v=DKIM1; k=ed25519; p=11qYAYKxCrfVS/7TyWQHOg7hcv...``
        """
        raw = self.PublicKey.public_bytes(Encoding.Raw, PublicFormat.Raw)
        p = base64.b64encode(raw).decode("ascii")
        return f"v={v}; k=ed25519; p={p}"
