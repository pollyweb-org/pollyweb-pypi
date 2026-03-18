"""PollyWeb DNS helpers."""

import base64
from dataclasses import dataclass
from typing import Optional

from pollyweb._crypto import (
    KEY_TYPE_LOADERS,
    load_dkim_public_key,
    signature_algorithm_for_dkim_key_type,
)


@dataclass(frozen = True)
class DnsQueryDiagnostic:
    """One DNS lookup result captured during verification."""

    Name: str
    Type: str
    ResponseCode: str
    AuthenticData: bool
    Answers: list[str]
    Error: str = ""


@dataclass(frozen = True)
class DnsVerificationDiagnostics:
    """DNSSEC diagnostics captured from the package verification path."""

    Domain: str
    PollyWebBranch: str
    Selector: str
    DkimName: str
    DnssecRequested: bool
    Nameservers: list[str]
    Queries: list[DnsQueryDiagnostic]
    Error: str = ""


class DnsLookupError(ValueError):
    """Raised when DNSSEC-backed verification lookups fail."""

    def __init__(
        self,
        message: str,
        *,
        diagnostics: DnsVerificationDiagnostics | None = None
    ) -> None:
        """Store the failure message together with package-owned diagnostics."""

        super().__init__(message)
        self.dns_diagnostics = diagnostics


def _parse_dkim_txt(txt: str) -> dict[str, str]:
    params = {}
    for part in txt.split(";"):
        part = part.strip()
        if "=" in part:
            k, v = part.split("=", 1)
            params[k.strip()] = v.strip()
    return params


def dkim_key_type_from_record(txt: str) -> str:
    """Return the DKIM key type declared by a TXT record."""
    key_type = _parse_dkim_txt(txt).get("k", "").lower()
    if key_type not in KEY_TYPE_LOADERS:
        raise ValueError(f"Unsupported DKIM key algorithm in record: {key_type or '<missing>'}")
    return key_type


def signature_algorithm_for_dkim_record(txt: str) -> str:
    """Return the preferred signature algorithm for a DKIM TXT record."""
    return signature_algorithm_for_dkim_key_type(dkim_key_type_from_record(txt))


def pollyweb_domain(domain: str) -> str:
    return f"pw.{domain}"


def dkim_dns_name(domain: str, selector: str) -> str:
    return f"{selector}._domainkey.{pollyweb_domain(domain)}"


DNSSEC_FALLBACK_NAMESERVERS = [
    "1.1.1.1",
    "1.0.0.1",
]


def _configure_dnssec_edns(
    resolver
) -> None:
    """Enable DNSSEC-aware EDNS options on a resolver."""

    import dns.flags

    resolver.use_edns(
        edns = 0,
        ednsflags = dns.flags.DO,
        payload = 4096)


def _response_has_ad_flag(
    answer
) -> bool:
    """Return whether a resolver answer was DNSSEC validated."""

    import dns.flags

    return bool(answer.response.flags & dns.flags.AD)


def _query_nameservers(
    resolver
) -> list[str]:
    """Return the configured nameservers for debug output."""

    return [str(item) for item in resolver.nameservers]


def _make_dns_query_diagnostic(
    answer,
    *,
    query_name: str,
    record_type: str
) -> DnsQueryDiagnostic:
    """Convert one resolver answer into a serializable diagnostic."""

    import dns.rcode

    response = getattr(answer, "response", None)
    response_code = ""

    if response is not None:
        try:
            response_code = dns.rcode.to_text(response.rcode())
        except (AttributeError, TypeError, ValueError):
            response_code = ""

    return DnsQueryDiagnostic(
        Name = query_name,
        Type = record_type,
        ResponseCode = response_code,
        AuthenticData = _response_has_ad_flag(
            answer),
        Answers = [record.to_text() for record in answer],
    )


def _iter_dnssec_resolvers():
    """Yield resolvers that can be used to request DNSSEC-validated answers."""

    import dns.resolver

    default_resolver = dns.resolver.Resolver()

    _configure_dnssec_edns(
        default_resolver)

    yield default_resolver

    for nameserver in DNSSEC_FALLBACK_NAMESERVERS:
        fallback_resolver = dns.resolver.Resolver(configure = False)
        fallback_resolver.nameservers = [nameserver]
        fallback_resolver.search = []
        fallback_resolver.port = 53

        _configure_dnssec_edns(
            fallback_resolver)

        yield fallback_resolver


def _resolve_with_dnssec_diagnostic(
    qname: str,
    rdtype: str,
    *,
    raise_on_no_answer: bool = True
):
    """Resolve one record and return the accepted answer plus its diagnostic."""

    last_answer = None
    last_diagnostic = None
    last_exception = None
    last_nameservers: list[str] = []

    for resolver in _iter_dnssec_resolvers():
        nameservers = _query_nameservers(
            resolver)

        try:
            answer = resolver.resolve(
                qname,
                rdtype,
                raise_on_no_answer = raise_on_no_answer)
        except Exception as exc:
            last_exception = exc
            last_nameservers = nameservers
            continue

        diagnostic = _make_dns_query_diagnostic(
            answer,
            query_name = qname,
            record_type = rdtype)
        last_answer = answer
        last_diagnostic = diagnostic
        last_nameservers = nameservers

        if _response_has_ad_flag(
            answer):
            return answer, diagnostic, nameservers

    if last_answer is not None and last_diagnostic is not None:
        return last_answer, last_diagnostic, last_nameservers

    raise ValueError(
        f"DNS lookup failed for {qname}: {last_exception}"
        if last_exception is not None
        else f"DNS lookup failed for {qname}")


def _resolve_with_dnssec(
    qname: str,
    rdtype: str,
    *,
    raise_on_no_answer: bool = True
):
    """Resolve a name and require a DNSSEC-validated answer from any trusted resolver."""

    answer, _, _ = _resolve_with_dnssec_diagnostic(
        qname,
        rdtype,
        raise_on_no_answer = raise_on_no_answer)

    if not _response_has_ad_flag(
        answer):
        raise ValueError(f"DNSSEC validation failed for {qname}")

    return answer


def validate_pollyweb_branch(domain: str) -> None:
    """Require DNSSEC validation for the delegated PollyWeb branch."""

    import dns.flags

    branch = pollyweb_domain(domain)
    try:
        answer = _resolve_with_dnssec(
            branch,
            "DS",
            raise_on_no_answer = False)
    except Exception as exc:
        raise ValueError(f"DNSSEC validation failed for {branch}: {exc}") from exc

    if not _response_has_ad_flag(
        answer):
        raise ValueError(f"DNSSEC validation failed for {branch}")


def resolve_dkim_with_dnssec(
    domain: str,
    selector: str
):
    """Resolve the trusted DKIM TXT answer together with package diagnostics."""

    branch = pollyweb_domain(domain)
    dkim_name = dkim_dns_name(domain, selector)
    diagnostics = DnsVerificationDiagnostics(
        Domain = domain,
        PollyWebBranch = branch,
        Selector = selector,
        DkimName = dkim_name,
        DnssecRequested = True,
        Nameservers = [],
        Queries = [],
    )

    try:
        branch_answer, branch_diagnostic, branch_nameservers = _resolve_with_dnssec_diagnostic(
            branch,
            "DS",
            raise_on_no_answer = False)
    except Exception as exc:
        failed = DnsVerificationDiagnostics(
            Domain = diagnostics.Domain,
            PollyWebBranch = diagnostics.PollyWebBranch,
            Selector = diagnostics.Selector,
            DkimName = diagnostics.DkimName,
            DnssecRequested = diagnostics.DnssecRequested,
            Nameservers = diagnostics.Nameservers,
            Queries = diagnostics.Queries,
            Error = str(exc),
        )
        raise DnsLookupError(
            f"DNSSEC validation failed for {branch}: {exc}",
            diagnostics = failed) from exc

    diagnostics = DnsVerificationDiagnostics(
        Domain = diagnostics.Domain,
        PollyWebBranch = diagnostics.PollyWebBranch,
        Selector = diagnostics.Selector,
        DkimName = diagnostics.DkimName,
        DnssecRequested = diagnostics.DnssecRequested,
        Nameservers = branch_nameservers,
        Queries = [branch_diagnostic],
    )

    if not branch_diagnostic.AuthenticData:
        raise DnsLookupError(
            f"DNSSEC validation failed for {branch}",
            diagnostics = diagnostics)

    try:
        dkim_answer, dkim_diagnostic, dkim_nameservers = _resolve_with_dnssec_diagnostic(
            dkim_name,
            "TXT")
    except Exception as exc:
        failed = DnsVerificationDiagnostics(
            Domain = diagnostics.Domain,
            PollyWebBranch = diagnostics.PollyWebBranch,
            Selector = diagnostics.Selector,
            DkimName = diagnostics.DkimName,
            DnssecRequested = diagnostics.DnssecRequested,
            Nameservers = diagnostics.Nameservers,
            Queries = diagnostics.Queries,
            Error = str(exc),
        )
        raise DnsLookupError(
            f"DKIM lookup failed for {dkim_name}: {exc}",
            diagnostics = failed) from exc

    nameservers = dkim_nameservers or diagnostics.Nameservers
    diagnostics = DnsVerificationDiagnostics(
        Domain = diagnostics.Domain,
        PollyWebBranch = diagnostics.PollyWebBranch,
        Selector = diagnostics.Selector,
        DkimName = diagnostics.DkimName,
        DnssecRequested = diagnostics.DnssecRequested,
        Nameservers = nameservers,
        Queries = diagnostics.Queries + [dkim_diagnostic],
    )

    if not dkim_diagnostic.AuthenticData:
        raise DnsLookupError(
            f"DNSSEC not enabled for {dkim_name}: cannot trust DKIM public key",
            diagnostics = diagnostics)

    return dkim_answer, diagnostics


def fetch_dkim_entry(domain: str, selector: str, *, require_dnssec: bool) -> Optional[tuple[str, bytes, str]]:
    import dns.resolver

    dns_name = dkim_dns_name(domain, selector)
    try:
        if require_dnssec:
            validate_pollyweb_branch(domain)
    except ValueError:
        raise
    except Exception:
        return None

    try:
        if require_dnssec:
            answers = _resolve_with_dnssec(
                dns_name,
                "TXT")
        else:
            resolver = dns.resolver.Resolver()
            answers = resolver.resolve(dns_name, "TXT")
    except Exception:
        return None

    if require_dnssec and not _response_has_ad_flag(
        answers):
        raise ValueError(f"DNSSEC validation failed for {dns_name}")

    for rdata in answers:
        txt = b"".join(rdata.strings).decode("utf-8")
        params = _parse_dkim_txt(txt)
        if params.get("v") != "DKIM1":
            raise ValueError(f"Unsupported DKIM version in {dns_name}")
        key_type = params.get("k", "").lower()
        if key_type not in KEY_TYPE_LOADERS:
            raise ValueError(f"Unsupported DKIM key algorithm in {dns_name}")
        p = params.get("p", "")
        if not p:
            continue
        try:
            raw = base64.b64decode(p)
            load_dkim_public_key(key_type, p)
            return selector, raw, txt
        except Exception as exc:
            raise ValueError(f"Invalid {key_type} key in {dns_name}: {exc}") from exc
    return None


def fetch_dkim_entries(domain: str, *, require_dnssec: bool) -> list[tuple[str, bytes, str]]:
    entries = []
    i = 1
    while True:
        result = fetch_dkim_entry(domain, f"pw{i}", require_dnssec=require_dnssec)
        if result is None:
            break
        entries.append(result)
        i += 1
    return entries


@dataclass(frozen=True)
class DNS:
    Name: str

    def check(self, selector: Optional[str] = None) -> dict:
        """Return a table-friendly validation report for PollyWeb DKIM DNS records."""
        report = {
            "summary": {
                "domain": self.Name,
                "selector": selector,
                "compliant": False,
            },
            "table": [],
        }

        try:
            if selector is not None:
                entry = fetch_dkim_entry(self.Name, selector, require_dnssec=True)
                report["summary"]["compliant"] = entry is not None
                report["table"].append({
                    "selector": selector,
                    "status": "ok" if entry is not None else "missing",
                    "compliant": entry is not None,
                    "record": entry[2] if entry is not None else None,
                    "message": None,
                })
                return report

            entries = fetch_dkim_entries(self.Name, require_dnssec=True)
            if not entries:
                report["table"].append({
                    "selector": None,
                    "status": "missing",
                    "compliant": False,
                    "record": None,
                    "message": "No PollyWeb DKIM selectors found",
                })
                return report

            seen_keys = set()
            for entry_selector, raw, txt in entries:
                if raw in seen_keys:
                    report["table"].append({
                        "selector": entry_selector,
                        "status": "error",
                        "compliant": False,
                        "record": txt,
                        "message": f"Public key reused in DKIM entry '{entry_selector}' for {self.Name}",
                    })
                    return report
                seen_keys.add(raw)
                report["table"].append({
                    "selector": entry_selector,
                    "status": "ok",
                    "compliant": True,
                    "record": txt,
                    "message": None,
                })

            report["summary"]["compliant"] = True
            return report
        except ValueError as exc:
            report["table"].append({
                "selector": selector,
                "status": "error",
                "compliant": False,
                "record": None,
                "message": str(exc),
            })
            return report
