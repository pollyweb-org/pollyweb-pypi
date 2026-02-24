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

By default this writes `pub.pem` and `priv.pem` in the current working
directory.  You can customize the output names with `--pub` and
`--priv`, and change the RSA key size with `--bits`.

A lightweight console script named ``pollyweb-keys`` is installed as
well, so the same functionality is available via::

    pollyweb-keys

For temporary experiments you can use the `tmp/` directory which is committed
empty but ignored by git.  Place any generated keys there to keep your
working tree clean::

    python -m pollyweb.demo.keys --pub tmp/pub.pem --priv tmp/priv.pem

Another helper script demonstrates a second command.  It takes a public
key filename and a DKIM identifier; older versions accepted two positional
arguments, but the current syntax is key/value based.  Both values are
ignored and the command simply prints a fixed API URL::

    pollyweb-setup dkim=pub.key id=key1

The module form works the same way::

    python -m pollyweb.demo.setup dkim=pub.key id=key1

The equal sign can be replaced with a colon if you prefer::

    pollyweb-setup dkim:pub.key id:key1

These forms allow easy extension if additional parameters are
introduced later.

