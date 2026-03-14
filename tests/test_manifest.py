"""Tests for pollyweb.manifest."""

import pollyweb as pw
import pytest

from pollyweb.manifest import SCHEMA, WIRE_SCHEMA_KEY


class TestManifest:
    def test_minimal_manifest(self):
        manifest = pw.Manifest(About={"Domain": "example.dom"})
        assert manifest.Schema == SCHEMA
        assert manifest.About["Domain"] == "example.dom"
        assert manifest.About["Language"] == "en-us"
        assert manifest.Trust == []

    def test_schema_string_normalizes(self):
        manifest = pw.Manifest(Schema=".MANIFEST", About={"Domain": "example.dom"})
        assert manifest.Schema == "pollyweb.org/MANIFEST:1.0"
        assert isinstance(manifest.Schema, pw.Schema)

    def test_unsupported_schema_rejected(self):
        with pytest.raises(pw.ManifestValidationError, match="Unsupported schema"):
            pw.Manifest(Schema="example.org/MANIFEST:1.0", About={"Domain": "example.dom"})

    def test_about_domain_is_required(self):
        with pytest.raises(pw.ManifestValidationError, match="About.Domain must be a domain string"):
            pw.Manifest(About={"Domain": "not a domain"})

    def test_about_icons_must_be_absolute_uris(self):
        with pytest.raises(pw.ManifestValidationError, match="About.SmallIcon must be an absolute URI"):
            pw.Manifest(About={"Domain": "example.dom", "SmallIcon": "/icon.png"})

    def test_about_translations_are_validated(self):
        manifest = pw.Manifest(
            About={
                "Domain": "example.dom",
                "Translations": [
                    {"Language": "pt-br", "Title": "Exemplo"},
                ],
            }
        )
        assert manifest.About["Translations"][0]["Language"] == "pt-br"

    def test_manifest_round_trip_dict(self):
        manifest = pw.Manifest(
            About={"Domain": "example.dom", "Title": "Example"},
            Trust=[{"Action": "GRANT", "Domain": "pollyweb.org", "Query": ".HELPER/*"}],
        )
        assert pw.Manifest.from_dict(manifest.to_dict()) == manifest

    def test_to_dict_uses_wire_schema_key(self):
        manifest = pw.Manifest(About={"Domain": "example.dom"})
        payload = manifest.to_dict()
        assert payload[WIRE_SCHEMA_KEY] == "pollyweb.org/MANIFEST:1.0"
        assert "Schema" not in payload

    def test_from_dict_accepts_schema_alias(self):
        manifest = pw.Manifest.from_dict(
            {
                "Schema": "pollyweb.org/MANIFEST:1.0",
                "About": {"Domain": "example.dom"},
            }
        )
        assert manifest.Schema == SCHEMA

    def test_parse_json(self):
        manifest = pw.Manifest.parse(
            '{"\\ud83e\\udd1d":"pollyweb.org/MANIFEST:1.0","About":{"Domain":"example.dom"}}'
        )
        assert manifest.About["Domain"] == "example.dom"

    def test_parse_yaml(self):
        manifest = pw.Manifest.parse(
            """
\U0001F91D: pollyweb.org/MANIFEST:1.0
About:
  Domain: example.dom
  Title: Example
"""
        )
        assert manifest.About["Title"] == "Example"

    def test_parse_bytes(self):
        manifest = pw.Manifest.parse(
            b'{"\\ud83e\\udd1d":"pollyweb.org/MANIFEST:1.0","About":{"Domain":"example.dom"}}'
        )
        assert manifest.About["Domain"] == "example.dom"

    def test_load_alias(self):
        manifest = pw.Manifest.load({"About": {"Domain": "example.dom"}})
        assert manifest.About["Domain"] == "example.dom"
