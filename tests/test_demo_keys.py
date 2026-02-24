import os
import tempfile

from pollyweb.demo import keys


def test_generate_keys_creates_files(tmp_path):
    pub_file = tmp_path / "my_public.pem"
    priv_file = tmp_path / "my_private.pem"
    # ensure they don't exist
    assert not pub_file.exists()
    assert not priv_file.exists()

    # run generator
    # RSA generator requires at least 1024 bits; use a small but valid size
    keys.generate_keys(pub_path=str(pub_file), priv_path=str(priv_file), bits=1024)

    assert pub_file.exists()
    assert priv_file.exists()
    # simple sanity check: files are not empty
    assert pub_file.stat().st_size > 0
    assert priv_file.stat().st_size > 0
