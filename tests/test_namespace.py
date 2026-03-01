import types

import pytest

import pollyweb as pw


def test_lazy_namespace_resolves_known_symbol():
    resolved = pw.CODE
    assert resolved.__name__ == "CODE"


def test_lazy_namespace_missing_symbol_raises_attribute_error():
    with pytest.raises(AttributeError):
        _ = pw.__definitely_not_a_symbol__


def test_lazy_namespace_ambiguous_symbol_raises_attribute_error(monkeypatch):
    monkeypatch.setattr(pw, "_candidate_modules", lambda name: ["pollyweb.a.A", "pollyweb.b.B"])

    module_a = types.SimpleNamespace(DUP=object())
    module_b = types.SimpleNamespace(DUP=object())

    def fake_import(module_name):
        if module_name == "pollyweb.a.A":
            return module_a
        if module_name == "pollyweb.b.B":
            return module_b
        raise ImportError(module_name)

    monkeypatch.setattr(pw, "import_module", fake_import)

    with pytest.raises(AttributeError, match="Ambiguous symbol 'DUP'"):
        _ = pw.DUP
