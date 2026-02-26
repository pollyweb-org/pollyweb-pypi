import stat

import pytest

from pollyweb.demo import keys


def test_generate_keys_creates_files(tmp_path):
    pub_file = tmp_path / "my_public.pem"
    priv_file = tmp_path / "my_private.pem"
    assert not pub_file.exists()
    assert not priv_file.exists()

    keys.generate_keys(pub_path=str(pub_file), priv_path=str(priv_file), bits=2048)

    assert pub_file.exists()
    assert priv_file.exists()
    assert pub_file.stat().st_size > 0
    assert priv_file.stat().st_size > 0


def test_private_key_permissions_are_restricted(tmp_path):
    priv_file = tmp_path / "my_private.pem"
    keys.generate_keys(pub_path=str(tmp_path / "pub.pem"), priv_path=str(priv_file), bits=2048)

    mode = stat.S_IMODE(priv_file.stat().st_mode)
    assert mode == 0o600


def test_rejects_weak_key_sizes(tmp_path):
    with pytest.raises(ValueError, match="at least 2048"):
        keys.generate_keys(
            pub_path=str(tmp_path / "pub.pem"),
            priv_path=str(tmp_path / "priv.pem"),
            bits=1024,
        )
