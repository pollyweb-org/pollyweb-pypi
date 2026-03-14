"""Internal signature and DKIM key helpers."""

import base64
from dataclasses import dataclass
from typing import Callable, Optional

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ed25519, padding, rsa


KeyLoader = Callable[[bytes], object]
Verifier = Callable[[object, bytes, bytes], None]
Signer = Callable[[object, bytes], bytes]


@dataclass(frozen=True)
class SignatureAlgorithmSpec:
    name: str
    key_type: str
    verify: Verifier
    sign: Signer


def _load_ed25519_public_key(key_bytes: bytes) -> ed25519.Ed25519PublicKey:
    try:
        return ed25519.Ed25519PublicKey.from_public_bytes(key_bytes)
    except ValueError:
        key = _load_der_or_pem_public_key(key_bytes)
        if not isinstance(key, ed25519.Ed25519PublicKey):
            raise ValueError("Expected an Ed25519 public key")
        return key


def _load_rsa_public_key(key_bytes: bytes) -> rsa.RSAPublicKey:
    key = _load_der_or_pem_public_key(key_bytes)
    if not isinstance(key, rsa.RSAPublicKey):
        raise ValueError("Expected an RSA public key")
    return key


def _load_der_or_pem_public_key(key_bytes: bytes) -> object:
    loaders = [serialization.load_der_public_key]
    if b"-----BEGIN" in key_bytes:
        loaders.insert(0, serialization.load_pem_public_key)

    last_error: Optional[Exception] = None
    for loader in loaders:
        try:
            return loader(key_bytes)
        except (TypeError, ValueError) as exc:
            last_error = exc

    raise ValueError(str(last_error) if last_error is not None else "Unsupported public key")


def _verify_ed25519(public_key: object, signature: bytes, message: bytes) -> None:
    if not isinstance(public_key, ed25519.Ed25519PublicKey):
        raise TypeError("Expected an Ed25519 public key")
    public_key.verify(signature, message)


def _verify_rsa_sha256(public_key: object, signature: bytes, message: bytes) -> None:
    if not isinstance(public_key, rsa.RSAPublicKey):
        raise TypeError("Expected an RSA public key")
    public_key.verify(signature, message, padding.PKCS1v15(), hashes.SHA256())


def _sign_ed25519(private_key: object, message: bytes) -> bytes:
    if not isinstance(private_key, ed25519.Ed25519PrivateKey):
        raise TypeError("Expected an Ed25519 private key")
    return private_key.sign(message)


def _sign_rsa_sha256(private_key: object, message: bytes) -> bytes:
    if not isinstance(private_key, rsa.RSAPrivateKey):
        raise TypeError("Expected an RSA private key")
    return private_key.sign(message, padding.PKCS1v15(), hashes.SHA256())


KEY_TYPE_LOADERS: dict[str, KeyLoader] = {
    "ed25519": _load_ed25519_public_key,
    "rsa": _load_rsa_public_key,
}


SIGNATURE_ALGORITHMS: dict[str, SignatureAlgorithmSpec] = {
    "ed25519-sha256": SignatureAlgorithmSpec(
        name="ed25519-sha256",
        key_type="ed25519",
        verify=_verify_ed25519,
        sign=_sign_ed25519,
    ),
    "rsa-sha256": SignatureAlgorithmSpec(
        name="rsa-sha256",
        key_type="rsa",
        verify=_verify_rsa_sha256,
        sign=_sign_rsa_sha256,
    ),
}


def canonical_signature_algorithm(name: str) -> str:
    lowered = name.lower()
    if lowered not in SIGNATURE_ALGORITHMS:
        raise ValueError(f"Unsupported signature algorithm: {name}")
    return lowered


def load_dkim_public_key(key_type: str, public_key_b64: str) -> object:
    loader = KEY_TYPE_LOADERS.get(key_type.lower())
    if loader is None:
        raise ValueError(f"Unsupported DKIM key algorithm: {key_type}")

    key_bytes = base64.b64decode(public_key_b64)
    return loader(key_bytes)


def signature_algorithm_for_private_key(private_key: object) -> str:
    if isinstance(private_key, ed25519.Ed25519PrivateKey):
        return "ed25519-sha256"
    if isinstance(private_key, rsa.RSAPrivateKey):
        return "rsa-sha256"
    raise TypeError(f"Unsupported private key type: {type(private_key).__name__}")


def signature_algorithm_for_public_key(public_key: object) -> str:
    if isinstance(public_key, ed25519.Ed25519PublicKey):
        return "ed25519-sha256"
    if isinstance(public_key, rsa.RSAPublicKey):
        return "rsa-sha256"
    raise TypeError(f"Unsupported public key type: {type(public_key).__name__}")


def sign_message(private_key: object, message: bytes, *, signature_algorithm: Optional[str] = None) -> tuple[bytes, str]:
    algorithm_name = signature_algorithm_for_private_key(private_key) if signature_algorithm is None else canonical_signature_algorithm(signature_algorithm)
    spec = SIGNATURE_ALGORITHMS[algorithm_name]
    return spec.sign(private_key, message), algorithm_name


def verify_signature(
    public_key: object,
    signature: bytes,
    message: bytes,
    *,
    signature_algorithm: Optional[str] = None,
    key_type: Optional[str] = None,
) -> None:
    algorithm_name = signature_algorithm_for_public_key(public_key) if signature_algorithm is None else canonical_signature_algorithm(signature_algorithm)
    spec = SIGNATURE_ALGORITHMS[algorithm_name]

    if key_type is not None and spec.key_type != key_type.lower():
        raise ValueError(
            f"Signature algorithm {algorithm_name} does not match DKIM key type {key_type}"
        )

    spec.verify(public_key, signature, message)
