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
    # ``cryptography`` is a relatively heavy dependency, but it is the de
    # facto standard for key material management in Python.  If it is not
    # available we fall back to a very simple (and insecure) random blob
    # generator so that the module still "works" for demonstration
    # purposes without pulling in extra requirements.
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.hazmat.primitives import serialization

    def _generate_rsa_keys(bits: int = 2048) -> tuple[bytes, bytes]:
        """Generate an RSA key pair and return (pub_pem, priv_pem)."""
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

except ImportError:  # pragma: no cover - fallback path
    import secrets
    import base64

    def _generate_rsa_keys(bits: int = 2048) -> tuple[bytes, bytes]:
        """Fallback generator when ``cryptography`` isn't installed.

        The returned material is not a real RSA key pair but rather two
        random blobs encoded as base64.  This makes the script runnable in
        minimal environments without extra dependencies.
        """
        length = bits // 8
        pub = base64.b64encode(secrets.token_bytes(length))
        priv = base64.b64encode(secrets.token_bytes(length))
        return pub, priv


def generate_keys(pub_path: str = "pub.pem", priv_path: str = "priv.pem", bits: int = 2048) -> None:
    """Generate key pair files in the current directory.

    :param pub_path: path where the public key will be written
    :param priv_path: path where the private key will be written
    :param bits: key size in bits (only used by the RSA generator)
    """
    pub_pem, priv_pem = _generate_rsa_keys(bits)
    with open(pub_path, "wb") as fpub:
        fpub.write(pub_pem)
    with open(priv_path, "wb") as fpriv:
        fpriv.write(priv_pem)
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
        "--bits", type=int, default=2048, help="key length in bits (RSA only)"
    )
    args = parser.parse_args(argv)

    # refuse to overwrite unless user explicitly passes same names
    if os.path.exists(args.pub) or os.path.exists(args.priv):
        answer = input(
            "one or both output files already exist; overwrite? [y/N]: "
        ).strip().lower()
        if answer not in ("y", "yes"):
            sys.exit(1)
    generate_keys(pub_path=args.pub, priv_path=args.priv, bits=args.bits)


if __name__ == "__main__":
    main()
