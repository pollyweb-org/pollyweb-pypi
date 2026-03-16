"""Tests for shared Struct helpers."""

from __future__ import annotations

import pytest

from pollyweb.struct import Struct


def test_struct_assert_trims_and_applies_defaults():
    """Struct.assert should trim strings and apply schema defaults."""

    payload = Struct.wrap(
        {
            "Domain": " example.com "})

    validated = getattr(
        payload,
        "assert")(
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


def test_struct_assert_rejects_blank_required_string():
    """Struct.assert should reject blank required strings after trimming."""

    payload = Struct.wrap(
        {
            "Domain": "   "})

    with pytest.raises(
        TypeError,
        match = "Missing Domain."):
        getattr(
            payload,
            "assert")(
                {
                    "type": "object",
                    "properties": {
                        "Domain": {
                            "type": "string",
                            "minLength": 1}},
                    "required": ["Domain"]})
