"""Tests for shared Struct helpers."""

from __future__ import annotations

import pytest

from pollyweb.struct import Struct


def test_struct_schema_trims_and_applies_defaults():
    """Struct.schema should trim strings and apply schema defaults."""

    payload = Struct.wrap(
        {
            "Domain": " example.com "})

    validated = payload.schema(
        {
            "type": "object",
            "properties": {
                "Domain": {
                    "type": "string",
                    "minLength": 1},
                "Language": {
                    "type": "string",
                    "default": "en-us"}},
            "required": ["Domain"]})

    assert validated.to_dict() == {
        "Domain": "example.com",
        "Language": "en-us"}


def test_struct_schema_rejects_blank_required_string():
    """Struct.schema should reject blank required strings after trimming."""

    payload = Struct.wrap(
        {
            "Domain": "   "})

    with pytest.raises(
        TypeError,
        match = "Missing Domain."):
        payload.schema(
            {
                "type": "object",
                "properties": {
                    "Domain": {
                        "type": "string",
                        "minLength": 1}},
                "required": ["Domain"]})


def test_struct_schema_accepts_compact_schema():
    """Struct.schema should expand the compact PollyWeb schema form."""

    payload = Struct.wrap(
        {
            "Consumer": " consumer.example.com ",
            "Binds": [
                {
                    "Vault": " vault.example.com ",
                    "Schema": " air.example.com/SSR/WCHR:2.1 "}],
        })

    validated = payload.schema(
        {
            "Consumer": "str!",
            "Binds": [{
                "Vault": "str!",
                "Schema": "str!"
            }]
        })

    assert validated.to_dict() == {
        "Consumer": "consumer.example.com",
        "Binds": [
            {
                "Vault": "vault.example.com",
                "Schema": "air.example.com/SSR/WCHR:2.1"}]}


def test_struct_schema_compact_optional_field():
    """Struct.schema should allow optional fields via the question mark suffix."""

    payload = Struct.wrap(
        {
            "Domain": "example.com"})

    validated = payload.schema(
        {
            "Domain": "str!",
            "Language?": "str"
        })

    assert validated.to_dict() == {
        "Domain": "example.com"}
