"""PollyWeb DNS helpers."""

import base64
from dataclasses import dataclass
from typing import Optional

from pollyweb._crypto import (
    KEY_TYPE_LOADERS,
    load_dkim_public_key,
    signature_algorithm_for_dkim_key_type,
)


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


def _resolve_with_dnssec(
    qname: str,
    rdtype: str,
    *,
    raise_on_no_answer: bool = True
):
    """Resolve a name and require a DNSSEC-validated answer from any trusted resolver."""

    last_answer = None
    last_exception = None

    for resolver in _iter_dnssec_resolvers():
        try:
            answer = resolver.resolve(
                qname,
                rdtype,
                raise_on_no_answer = raise_on_no_answer)
        except Exception as exc:
            last_exception = exc
            continue

        last_answer = answer

        if _response_has_ad_flag(
            answer):
            return answer

    if last_exception is not None and last_answer is None:
        raise last_exception

    if last_answer is not None:
        return last_answer

    raise ValueError(f"DNS lookup failed for {qname}")


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
