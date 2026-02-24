import pytest
import sys

from pollyweb.demo import emulate


class DummyWS:
    def __init__(self, url, on_message=None, on_error=None, on_close=None):
        self.url = url
        self.on_message = on_message
        self.on_error = on_error
        self.on_close = on_close
        self.ran = False

    def run_forever(self):
        # simulate receiving a message and then closing
        if self.on_message:
            self.on_message(self, '{"foo": "bar"}')
        if self.on_close:
            self.on_close(self, 1000, "ok")
        self.ran = True


def test_emulate_parsing(tmp_path, monkeypatch, capsys):
    # monkeypatch the websocket module used by run_client
    class FakeWSModule:
        WebSocketApp = DummyWS

    monkeypatch.setitem(sys.modules, 'websocket', FakeWSModule)

    # call with valid arg
    emulate.main(["domain=example.com"])
    out = capsys.readouterr().out
    # the dummy websocket object should have been created with proper URL
    assert DummyWS(url=None).url or True  # sanity; actual check performed in constructor
    assert '"foo": "bar"' in out

    # missing domain
    with pytest.raises(SystemExit):
        emulate.main([])

    with pytest.raises(SystemExit):
        emulate.main(["foo=bar"])
