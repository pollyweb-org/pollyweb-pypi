"""Tests for pollyweb.dns.

Note: These tests use real DNS queries to validate DNSSEC behavior.
They require network access and may be slower than unit tests.
"""

import pytest
from unittest.mock import Mock, patch

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
        # Test with cloudflare.com which has DNSSEC enabled
        # This should fail if the domain doesn't have the expected DKIM record
        # but succeed in validating DNSSEC if the record exists
        result = fetch_dkim_entry("cloudflare.com", "pw1", require_dnssec=True)
        # We expect None (no pw1._domainkey.pw.cloudflare.com record)
        # but DNSSEC validation should not raise an error
        assert result is None

    def test_dnssec_validation_fails_without_ad_flag(self):
        """Test that DNSSEC validation fails when AD flag is not set."""
        with patch('dns.resolver.Resolver') as mock_resolver_class:
            mock_resolver = Mock()
            mock_resolver_class.return_value = mock_resolver
            
            # Create a mock response without the AD flag
            mock_response = Mock()
            mock_response.flags = 0  # No AD flag
            
            mock_answers = Mock()
            mock_answers.response = mock_response
            mock_answers.__iter__ = Mock(return_value=iter([]))
            
            mock_resolver.resolve.return_value = mock_answers
            
            # This should raise ValueError because AD flag is missing
            with pytest.raises(ValueError, match="DNSSEC validation failed"):
                fetch_dkim_entry("example.com", "pw1", require_dnssec=True)


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
        # Test with google.com which has DNSSEC enabled
        dns = DNS(Name="google.com")
        report = dns.check()
        
        # We expect no PollyWeb DKIM records, but DNSSEC validation should work
        assert report["summary"]["compliant"] is False
        assert report["table"][0]["status"] == "missing"
