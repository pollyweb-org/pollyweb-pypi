# `pair.private_pem_bytes()`

Returns the private key encoded as unencrypted PKCS#8 PEM bytes.

```python
private_pem = pair.private_pem_bytes()
```

This is intended for writing a local signing key file:

```python
from pathlib import Path

Path("private.pem").write_bytes(pair.private_pem_bytes())
```
