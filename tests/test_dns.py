"""Tests for pollyweb.dns."""

from unittest.mock import Mock, patch

import pytest

from pollyweb.dns import DNS, fetch_dkim_entry
from pollyweb.msg import MsgValidationError, _resolve_dkim_public_key


def _make_txt_answer(*, txt_records=(), ad_flag=True):
    import dns.flags

    response = Mock()
    response.flags = dns.flags.AD if ad_flag else 0

    answer = Mock()
    answer.response = response
    answer.__iter__ = Mock(return_value=iter(txt_records))
    return answer


def _make_txt_rdata(txt):
    rdata = Mock()
    rdata.strings = [txt.encode("utf-8")]
    return rdata


class TestFetchDkimEntry:
    """Unit tests for DNS lookup and DNSSEC enforcement."""

    def test_returns_parsed_record_when_dnssec_validates(self):
        txt = "v=DKIM1; k=ed25519; p=MCowBQYDK2VwAyEA5lWUPm7x4TuCk8P3x51rZ6Q4e9M7jvY0q2Lx5f7mS8U="
        with patch("dns.resolver.Resolver") as mock_resolver_class:
            mock_resolver = Mock()
            mock_resolver_class.return_value = mock_resolver
            mock_resolver.resolve.side_effect = [
                _make_txt_answer(ad_flag=True),
                _make_txt_answer(txt_records=[_make_txt_rdata(txt)], ad_flag=True),
            ]

            selector, raw, record = fetch_dkim_entry("example.com", "pw1", require_dnssec=True)

        mock_resolver.use_edns.assert_called_once()
        assert mock_resolver.resolve.call_args_list == [
            (("pw.example.com", "DS"), {"raise_on_no_answer": False}),
            (("pw1._domainkey.pw.example.com", "TXT"), {}),
        ]
        assert selector == "pw1"
        assert isinstance(raw, bytes)
        assert record == txt

    def test_dnssec_validation_fails_without_ad_flag_on_pollyweb_branch(self):
        with patch("dns.resolver.Resolver") as mock_resolver_class:
            mock_resolver = Mock()
            mock_resolver_class.return_value = mock_resolver
            mock_resolver.resolve.return_value = _make_txt_answer(ad_flag=False)

            with pytest.raises(ValueError, match="DNSSEC validation failed"):
                from pollyweb.dns import validate_pollyweb_branch

                validate_pollyweb_branch(mock_resolver, "example.com")

    def test_raises_when_pollyweb_branch_dnssec_validation_fails(self):
        with patch("dns.resolver.Resolver") as mock_resolver_class:
            mock_resolver = Mock()
            mock_resolver_class.return_value = mock_resolver
            mock_resolver.resolve.return_value = _make_txt_answer(ad_flag=False)

            with pytest.raises(ValueError, match="DNSSEC validation failed for pw.example.com"):
                fetch_dkim_entry("example.com", "pw1", require_dnssec=True)

    def test_nonexistent_domain_returns_none(self):
        with patch("dns.resolver.Resolver") as mock_resolver_class:
            mock_resolver = Mock()
            mock_resolver_class.return_value = mock_resolver
            mock_resolver.resolve.side_effect = Exception("NXDOMAIN")

            result = fetch_dkim_entry("nonexistent-domain-12345.com", "pw1", require_dnssec=False)

        assert result is None


@pytest.mark.live_dns
class TestFetchDkimEntryIntegration:
    """Integration tests that use the network and real domains."""

    def test_require_dnssec_with_cloudflare(self):
        with pytest.raises(ValueError, match=r"DNSSEC validation failed for pw\.cloudflare\.com"):
            fetch_dkim_entry("cloudflare.com", "pw1", require_dnssec=True)

    def test_pollyweb_org_dns_must_validate_and_resolve(self):
        try:
            key, key_type = _resolve_dkim_public_key("pollyweb.org", "pw1")
        except MsgValidationError as exc:
            pytest.fail(f"pollyweb.org DNS is misconfigured: {exc}")

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

    def test_check_reports_dnssec_branch_failure_for_pollyweb_org(self):
        dns = DNS(Name="pollyweb.org")
        report = dns.check("pw1")

        assert report["summary"]["compliant"] is False
        assert report["table"][0]["status"] == "error"
        assert "DNSSEC validation failed for pw.pollyweb.org" in report["table"][0]["message"]
        assert "SERVFAIL" in report["table"][0]["message"]
