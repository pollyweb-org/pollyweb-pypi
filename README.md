# PollyWeb

<img src="https://www.pollyweb.org/images/pollyweb-logo.png" alt="PollyWeb logo" width="66" />

A neutral, open, and global web protocol that allows any person or AI agent to chat with any business, place, or thing.

## Usage

```
from pollyweb import hello
print(hello())
```


## Demo key generator

In addition to the `hello` helper, the package includes a simple demo
module that can generate a public/private key pair.  After installation
run::

    python -m pollyweb.demo.keys

By default this writes `pub.key` and `priv.key` in the current working
directory.  You can customize the output names with `--pub` and
`--priv`, and change the RSA key size with `--bits`.

A lightweight console script named ``pollyweb-keys`` is installed as
well, so the same functionality is available via::

    pollyweb-keys

