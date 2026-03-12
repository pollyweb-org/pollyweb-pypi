"""PollyWeb Domain — signing authority for outbound messages."""

from dataclasses import dataclass, replace
from typing import Union

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import load_pem_private_key

from pollyweb.msg import Msg


@dataclass
class Domain:
    Name: str
    PrivateKey: Union[Ed25519PrivateKey, str, bytes]
    DKIM: str

    def _private_key(self) -> Ed25519PrivateKey:
        if isinstance(self.PrivateKey, Ed25519PrivateKey):
            return self.PrivateKey
        pem = self.PrivateKey if isinstance(self.PrivateKey, bytes) else self.PrivateKey.encode()
        return load_pem_private_key(pem, password=None)  # type: ignore[return-value]

    def sign(self, msg: Msg) -> Msg:
        """Return a new Msg with From/DKIM set from this domain and Ed25519 signature."""
        return replace(msg, From=self.Name, DKIM=self.DKIM).sign(self._private_key())
