"""Tests for pollyweb.dns.

Note: These tests use real DNS queries to validate DNSSEC behavior.
They require network access and may be slower than unit tests.
"""

import pytest

import pollyweb as pw
from pollyweb.dns import DNS, fetch_dkim_entry


# ---------------------------------------------------------------------------
# Real DNS integration tests
# ---------------------------------------------------------------------------

class TestFetchDkimEntryIntegration:
    """Integration tests using real DNS queries."""

    def test_nonexistent_domain_returns_none(self):
        """DNS lookup for nonexistent domain should return None."""
        result = fetch_dkim_entry("nonexistent-domain-12345.com", "pw1", require_dnssec=False)
        assert result is None

    def test_require_dnssec_with_cloudflare(self):
        """Test DNSSEC validation using Cloudflare DNS (1.1.1.1)."""
        # This test requires a domain with DNSSEC-signed DKIM records
        # Skip if no suitable test domain is available
        pytest.skip("Requires a test domain with DNSSEC-enabled DKIM records")


class TestDNSCheckIntegration:
    """Integration tests for DNS.check() using real DNS."""

    def test_check_nonexistent_domain(self):
        """Check should handle nonexistent domains gracefully."""
        dns = DNS(Name="nonexistent-domain-12345.com")
        report = dns.check()

        assert report["summary"]["compliant"] is False
        assert report["table"][0]["status"] == "missing"
        assert "No PollyWeb DKIM selectors found" in report["table"][0]["message"]

    def test_check_with_dnssec_validation(self):
        """Test DNS.check() with DNSSEC validation."""
        # This test requires a domain with DNSSEC-signed DKIM records
        # Skip if no suitable test domain is available
        pytest.skip("Requires a test domain with DNSSEC-enabled DKIM records")
