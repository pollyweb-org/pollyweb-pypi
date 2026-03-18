"""Tests for pollyweb.dns."""

from unittest.mock import MagicMock, patch

import pytest

from pollyweb.dns import DNS, fetch_dkim_entry, resolve_dkim_with_dnssec
from pollyweb.msg import MsgValidationError, _resolve_dkim_public_key


def _dns_answer(
    *records: str,
    ad_flag: bool
):
    """Build a fake resolver answer with optional DNSSEC authentication."""

    import dns.flags
    import dns.rcode

    response = MagicMock()
    response.flags = dns.flags.AD if ad_flag else 0
    response.rcode.return_value = dns.rcode.NOERROR

    answer = MagicMock()
    answer.response = response
    answer.__iter__ = lambda self: iter(
        [MagicMock(to_text = lambda value = record: value) for record in records]
    )
    return answer


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
            key, key_type, _ = _resolve_dkim_public_key(domain, selector)
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


def test_resolve_dkim_with_dnssec_uses_fallback_resolver_when_primary_lacks_ad():
    primary_resolver = MagicMock()
    primary_resolver.nameservers = ["192.0.2.1"]
    primary_resolver.resolve.side_effect = [
        _dns_answer(
            "48567 13 2 PRIMARY",
            ad_flag = False),
        _dns_answer(
            '"v=DKIM1; k=ed25519; p=PRIMARY"',
            ad_flag = False),
    ]

    fallback_resolver = MagicMock()
    fallback_resolver.nameservers = ["8.8.8.8"]
    fallback_resolver.resolve.side_effect = [
        _dns_answer(
            "48567 13 2 FALLBACK",
            ad_flag = True),
        _dns_answer(
            '"v=DKIM1; k=ed25519; p=FALLBACK"',
            ad_flag = True),
    ]

    with patch(
        "pollyweb.dns._iter_dnssec_resolvers",
        side_effect = lambda: iter([primary_resolver, fallback_resolver]),
    ):
        answer, diagnostics = resolve_dkim_with_dnssec(
            "sender.dom",
            "pw1")

    assert diagnostics.Nameservers == ["8.8.8.8"]
    assert diagnostics.Queries[0].AuthenticData is True
    assert diagnostics.Queries[1].AuthenticData is True
    assert diagnostics.Queries[1].Answers == ['"v=DKIM1; k=ed25519; p=FALLBACK"']
    assert list(answer)[0].to_text() == '"v=DKIM1; k=ed25519; p=FALLBACK"'
