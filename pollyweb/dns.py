"""PollyWeb DNS helpers."""

import base64
from dataclasses import dataclass
from typing import Optional

from pollyweb._crypto import KEY_TYPE_LOADERS, load_dkim_public_key


def _parse_dkim_txt(txt: str) -> dict[str, str]:
    params = {}
    for part in txt.split(";"):
        part = part.strip()
        if "=" in part:
            k, v = part.split("=", 1)
            params[k.strip()] = v.strip()
    return params


def fetch_dkim_entry(domain: str, selector: str, *, require_dnssec: bool) -> Optional[tuple[str, bytes, str]]:
    import dns.flags
    import dns.resolver

    dns_name = f"{selector}._domainkey.pw.{domain}"
    try:
        answers = dns.resolver.resolve(dns_name, "TXT")
    except Exception:
        return None

    if require_dnssec and not (answers.response.flags & dns.flags.AD):
        raise ValueError(f"DNSSEC not enabled for {dns_name}")

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
