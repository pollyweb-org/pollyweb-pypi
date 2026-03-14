"""Tests for pollyweb.dns."""

from unittest.mock import MagicMock, patch

import pytest

import pollyweb as pw
from pollyweb.dns import DNS, fetch_dkim_entry, fetch_dkim_entries


# ---------------------------------------------------------------------------
# DNS mock helpers
# ---------------------------------------------------------------------------

def _mock_resolver_with_edns(ad_flag: bool = True):
    """Return a mock resolver that tracks EDNS configuration."""
    import dns.flags

    resolver = MagicMock()
    resolver.edns_configured = False
    resolver.do_flag_set = False
    resolver.ad_flag_requested = False

    def use_edns(edns, ednsflags, payload):
        resolver.edns_configured = True
        resolver.do_flag_set = (ednsflags & dns.flags.DO) != 0
        resolver.edns_version = edns
        resolver.payload_size = payload

    def set_flags(flags):
        resolver.ad_flag_requested = (flags & dns.flags.AD) != 0

    resolver.use_edns = use_edns
    resolver.set_flags = set_flags

    # Mock response
    response = MagicMock()
    response.flags = dns.flags.AD if ad_flag else 0

    answer = MagicMock()
    answer.response = response

    # Mock TXT record
    txt = "v=DKIM1; k=ed25519; p=MCowBQYDK2VwAyEAGb9ECWmEzf6FQbrBZ9w7lshQhqowtrbLDFw4rXAxZuE="
    rdata = MagicMock()
    rdata.strings = [txt.encode("utf-8")]
    answer.__iter__ = lambda self: iter([rdata])

    resolver.resolve = MagicMock(return_value=answer)

    return resolver


# ---------------------------------------------------------------------------
# fetch_dkim_entry tests
# ---------------------------------------------------------------------------

class TestFetchDkimEntry:
    def test_require_dnssec_enables_edns_with_do_flag(self):
        """When require_dnssec=True, EDNS must be enabled with DO flag."""
        resolver = _mock_resolver_with_edns(ad_flag=True)

        with patch("dns.resolver.Resolver", return_value=resolver):
            result = fetch_dkim_entry("example.com", "pw1", require_dnssec=True)

        assert resolver.edns_configured is True
        assert resolver.do_flag_set is True
        assert resolver.edns_version == 0
        assert resolver.payload_size == 4096
        assert result is not None

    def test_require_dnssec_sets_ad_flag(self):
        """When require_dnssec=True, AD flag must be requested."""
        resolver = _mock_resolver_with_edns(ad_flag=True)

        with patch("dns.resolver.Resolver", return_value=resolver):
            result = fetch_dkim_entry("example.com", "pw1", require_dnssec=True)

        assert resolver.ad_flag_requested is True
        assert result is not None

    def test_require_dnssec_false_skips_edns_configuration(self):
        """When require_dnssec=False, EDNS should not be configured."""
        resolver = _mock_resolver_with_edns(ad_flag=False)

        with patch("dns.resolver.Resolver", return_value=resolver):
            result = fetch_dkim_entry("example.com", "pw1", require_dnssec=False)

        assert resolver.edns_configured is False
        assert resolver.do_flag_set is False
        assert result is not None

    def test_require_dnssec_raises_when_ad_flag_missing(self):
        """When require_dnssec=True but AD flag is not set, must raise."""
        resolver = _mock_resolver_with_edns(ad_flag=False)

        with patch("dns.resolver.Resolver", return_value=resolver):
            with pytest.raises(ValueError, match="DNSSEC validation failed"):
                fetch_dkim_entry("example.com", "pw1", require_dnssec=True)

    def test_require_dnssec_succeeds_when_ad_flag_present(self):
        """When require_dnssec=True and AD flag is set, should succeed."""
        resolver = _mock_resolver_with_edns(ad_flag=True)

        with patch("dns.resolver.Resolver", return_value=resolver):
            result = fetch_dkim_entry("example.com", "pw1", require_dnssec=True)

        assert result is not None
        selector, raw, txt = result
        assert selector == "pw1"
        assert isinstance(raw, bytes)
        assert "v=DKIM1" in txt

    def test_dns_lookup_failure_returns_none(self):
        """When DNS lookup fails, should return None."""
        import dns.resolver as _r

        with patch("dns.resolver.Resolver") as mock_resolver_class:
            mock_resolver = MagicMock()
            mock_resolver.resolve.side_effect = _r.NXDOMAIN
            mock_resolver_class.return_value = mock_resolver

            result = fetch_dkim_entry("nonexistent.com", "pw1", require_dnssec=False)

        assert result is None

    def test_constructs_correct_dns_name(self):
        """DNS query should use correct format: {selector}._domainkey.pw.{domain}"""
        resolver = _mock_resolver_with_edns(ad_flag=True)

        with patch("dns.resolver.Resolver", return_value=resolver):
            fetch_dkim_entry("example.com", "pw1", require_dnssec=True)

        resolver.resolve.assert_called_once_with("pw1._domainkey.pw.example.com", "TXT")


# ---------------------------------------------------------------------------
# fetch_dkim_entries tests
# ---------------------------------------------------------------------------

class TestFetchDkimEntries:
    def test_fetches_sequential_selectors(self):
        """Should fetch pw1, pw2, pw3... until one fails."""
        def mock_fetch(domain, selector, *, require_dnssec):
            if selector in ["pw1", "pw2", "pw3"]:
                return (selector, b"key", f"v=DKIM1; k=ed25519; p={selector}")
            return None

        with patch("pollyweb.dns.fetch_dkim_entry", side_effect=mock_fetch):
            entries = fetch_dkim_entries("example.com", require_dnssec=True)

        assert len(entries) == 3
        assert entries[0][0] == "pw1"
        assert entries[1][0] == "pw2"
        assert entries[2][0] == "pw3"

    def test_stops_at_first_missing_selector(self):
        """Should stop when a selector is not found."""
        def mock_fetch(domain, selector, *, require_dnssec):
            if selector == "pw1":
                return (selector, b"key", "v=DKIM1; k=ed25519; p=abc")
            return None

        with patch("pollyweb.dns.fetch_dkim_entry", side_effect=mock_fetch):
            entries = fetch_dkim_entries("example.com", require_dnssec=True)

        assert len(entries) == 1
        assert entries[0][0] == "pw1"

    def test_returns_empty_list_when_no_selectors_found(self):
        """Should return empty list when pw1 doesn't exist."""
        with patch("pollyweb.dns.fetch_dkim_entry", return_value=None):
            entries = fetch_dkim_entries("example.com", require_dnssec=True)

        assert entries == []

    def test_passes_require_dnssec_to_fetch_dkim_entry(self):
        """Should pass require_dnssec parameter to fetch_dkim_entry."""
        with patch("pollyweb.dns.fetch_dkim_entry", return_value=None) as mock_fetch:
            fetch_dkim_entries("example.com", require_dnssec=True)

        mock_fetch.assert_called_with("example.com", "pw1", require_dnssec=True)


# ---------------------------------------------------------------------------
# DNS.check tests
# ---------------------------------------------------------------------------

class TestDNSCheck:
    def test_check_with_selector_validates_single_entry(self):
        """When selector is provided, should check only that selector."""
        dns = DNS(Name="example.com")

        with patch("pollyweb.dns.fetch_dkim_entry", return_value=("pw1", b"key", "v=DKIM1; k=ed25519; p=abc")):
            report = dns.check(selector="pw1")

        assert report["summary"]["domain"] == "example.com"
        assert report["summary"]["selector"] == "pw1"
        assert report["summary"]["compliant"] is True
        assert len(report["table"]) == 1
        assert report["table"][0]["selector"] == "pw1"
        assert report["table"][0]["status"] == "ok"

    def test_check_without_selector_validates_all_entries(self):
        """When no selector provided, should check all pw* selectors."""
        dns = DNS(Name="example.com")

        entries = [
            ("pw1", b"key1", "v=DKIM1; k=ed25519; p=abc"),
            ("pw2", b"key2", "v=DKIM1; k=ed25519; p=def"),
        ]

        with patch("pollyweb.dns.fetch_dkim_entries", return_value=entries):
            report = dns.check()

        assert report["summary"]["compliant"] is True
        assert len(report["table"]) == 2
        assert report["table"][0]["selector"] == "pw1"
        assert report["table"][1]["selector"] == "pw2"

    def test_check_detects_reused_keys(self):
        """Should detect when the same public key is used in multiple selectors."""
        dns = DNS(Name="example.com")

        entries = [
            ("pw1", b"same-key", "v=DKIM1; k=ed25519; p=abc"),
            ("pw2", b"same-key", "v=DKIM1; k=ed25519; p=abc"),
        ]

        with patch("pollyweb.dns.fetch_dkim_entries", return_value=entries):
            report = dns.check()

        assert report["summary"]["compliant"] is False
        assert report["table"][1]["status"] == "error"
        assert "reused" in report["table"][1]["message"].lower()

    def test_check_handles_missing_entries(self):
        """Should report when no DKIM entries are found."""
        dns = DNS(Name="example.com")

        with patch("pollyweb.dns.fetch_dkim_entries", return_value=[]):
            report = dns.check()

        assert report["summary"]["compliant"] is False
        assert len(report["table"]) == 1
        assert report["table"][0]["status"] == "missing"
        assert "No PollyWeb DKIM selectors found" in report["table"][0]["message"]

    def test_check_handles_dnssec_validation_error(self):
        """Should handle DNSSEC validation errors gracefully."""
        dns = DNS(Name="example.com")

        with patch("pollyweb.dns.fetch_dkim_entry", side_effect=ValueError("DNSSEC validation failed")):
            report = dns.check(selector="pw1")

        assert report["summary"]["compliant"] is False
        assert report["table"][0]["status"] == "error"
        assert "DNSSEC validation failed" in report["table"][0]["message"]

    def test_check_uses_require_dnssec_true(self):
        """DNS.check should always use require_dnssec=True."""
        dns = DNS(Name="example.com")

        with patch("pollyweb.dns.fetch_dkim_entry", return_value=None) as mock_fetch:
            dns.check(selector="pw1")

        mock_fetch.assert_called_once_with("example.com", "pw1", require_dnssec=True)

    def test_check_without_selector_uses_require_dnssec_true(self):
        """DNS.check should always use require_dnssec=True for all entries."""
        dns = DNS(Name="example.com")

        with patch("pollyweb.dns.fetch_dkim_entries", return_value=[]) as mock_fetch:
            dns.check()

        mock_fetch.assert_called_once_with("example.com", require_dnssec=True)
