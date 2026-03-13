# `pair.public_pem_bytes()`

Returns the public key encoded as SubjectPublicKeyInfo PEM bytes.

```python
public_pem = pair.public_pem_bytes()
```

This is intended for writing a shareable verification key file:

```python
from pathlib import Path

Path("public.pem").write_bytes(pair.public_pem_bytes())
```
