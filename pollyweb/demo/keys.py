"""Demo utilities for pollyweb.

This module currently provides a simple key-pair generator.  It can be
executed as a script using the module path:

    python -m pollyweb.demo.keys

or, after the package is installed with ``pip install pollyweb``, the same
command will work from anywhere in the system.

The generator writes two files in the current working directory:
``pub.key`` and ``priv.key`` in PEM format.
"""

import os
import sys

try:
    # ``cryptography`` is the standard and required backend for generating
    # real key material.
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.hazmat.primitives import serialization
except ImportError as exc:  # pragma: no cover - import error path
    raise RuntimeError(
        "cryptography is required to generate keys; install with 'pip install cryptography'"
    ) from exc


def _generate_rsa_keys(bits: int = 2048) -> tuple[bytes, bytes]:
    """Generate an RSA key pair and return ``(pub_pem, priv_pem)``."""
    if bits < 2048:
        raise ValueError("key size must be at least 2048 bits")

    priv_key = rsa.generate_private_key(public_exponent=65537, key_size=bits)
    pub_key = priv_key.public_key()
    priv_pem = priv_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    )
    pub_pem = pub_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    return pub_pem, priv_pem


def _write_private_key(path: str, key_bytes: bytes) -> None:
    """Write private key bytes with mode 0600, avoiding permissive defaults."""
    flags = os.O_WRONLY | os.O_CREAT | os.O_TRUNC
    nofollow = getattr(os, "O_NOFOLLOW", 0)
    fd = os.open(path, flags | nofollow, 0o600)
    with os.fdopen(fd, "wb") as fpriv:
        fpriv.write(key_bytes)

    # Enforce restrictive permissions even if a pre-existing file was reused.
    os.chmod(path, 0o600)


def generate_keys(pub_path: str = "pub.pem", priv_path: str = "priv.pem", bits: int = 2048) -> None:
    """Generate key pair files in the current directory.

    :param pub_path: path where the public key will be written
    :param priv_path: path where the private key will be written
    :param bits: key size in bits
    """
    pub_pem, priv_pem = _generate_rsa_keys(bits)
    with open(pub_path, "wb") as fpub:
        fpub.write(pub_pem)
    _write_private_key(priv_path, priv_pem)
    print(f"wrote public key to {pub_path}")
    print(f"wrote private key to {priv_path}")


def main(argv=None):
    """Script entry point.

    This accepts optional command-line arguments so that the user can specify
    output file names and key size.  ``python -m pollyweb.demo.keys`` invokes
    this function automatically.
    """
    if argv is None:
        argv = sys.argv[1:]

    import argparse

    parser = argparse.ArgumentParser(description="Generate a public/private key pair.")
    parser.add_argument(
        "--pub", default="pub.pem", help="output filename for the public key"
    )
    parser.add_argument(
        "--priv", default="priv.pem", help="output filename for the private key"
    )
    parser.add_argument(
        "--bits", type=int, default=2048, help="key length in bits (minimum 2048)"
    )
    args = parser.parse_args(argv)

    # refuse to overwrite unless user explicitly confirms
    if os.path.exists(args.pub) or os.path.exists(args.priv):
        answer = input(
            "one or both output files already exist; overwrite? [y/N]: "
        ).strip().lower()
        if answer not in ("y", "yes"):
            sys.exit(1)
    generate_keys(pub_path=args.pub, priv_path=args.priv, bits=args.bits)


if __name__ == "__main__":
    main()
