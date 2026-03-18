"""Tests for pollyweb.dns."""

import pytest

from pollyweb.dns import DNS, fetch_dkim_entry
from pollyweb.msg import MsgValidationError, _resolve_dkim_public_key


@pytest.mark.live_dns
class TestFetchDkimEntryIntegration:
    """Integration tests that use the network and real domains."""

    def test_require_dnssec_with_cloudflare(self):
        assert fetch_dkim_entry("cloudflare.com", "pw1", require_dnssec=True) is None

    @pytest.mark.parametrize(
        ("domain", "selector"),
        [
            ("pollyweb.org", "pw1"),
            ("any-hoster.pollyweb.org", "pw2"),
            ("any-streamer.pollyweb.org", "pw1"),
        ],
    )
    def test_pollyweb_domains_dns_must_validate_and_resolve(self, domain, selector):
        try:
            key, key_type = _resolve_dkim_public_key(domain, selector)
        except MsgValidationError as exc:
            pytest.fail(f"{domain} DNS is misconfigured: {exc}")

        assert key_type == "ed25519"
        assert key is not None


@pytest.mark.live_dns
class TestDNSCheckIntegration:
    """Integration tests for DNS.check() using real DNS."""

    def test_check_nonexistent_domain(self):
        dns = DNS(Name="nonexistent-domain-12345.com")
        report = dns.check()

        assert report["summary"]["compliant"] is False
        assert report["table"][0]["status"] == "error"
        assert "DNSSEC validation failed for pw.nonexistent-domain-12345.com" in report["table"][0]["message"]

    def test_check_with_dnssec_validation(self):
        dns = DNS(Name="google.com")
        report = dns.check()

        assert report["summary"]["compliant"] is False
        assert report["table"][0]["status"] == "error"
        assert "DNSSEC validation failed for pw.google.com" in report["table"][0]["message"]

    def test_check_reports_dnssec_branch_success_for_pollyweb_org(self):
        dns = DNS(Name="pollyweb.org")
        report = dns.check("pw1")

        assert report["summary"]["compliant"] is True
        assert report["table"][0]["status"] == "ok"
        assert report["table"][0]["compliant"] is True
        assert report["table"][0]["message"] is None
