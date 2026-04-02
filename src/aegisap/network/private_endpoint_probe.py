"""Private-endpoint connectivity probe for Day 12.

This module performs two distinct checks:

1. **DNS resolution check** — verifies that each AI-service hostname resolves
   to a *private* IP address (RFC-1918 range), indicating that the Private DNS
   zone is correctly linked to the VNET.  A public IP in the DNS response
   means traffic is bypassing the private endpoint.

2. **Public-endpoint reachability check** — attempts a direct HTTPS connection
   to each service's public hostname.  The probe expects a *timeout or refused*
   response; a successful TLS handshake means ``publicNetworkAccess`` is still
   enabled on the resource.

The probe writes two artifacts:

* ``build/day12/private_network_posture.json`` — full posture report used by
  ``gate_private_network_posture`` and the ``trace_correlation`` gate.
* ``build/day12/external_sink_disabled.json`` — boolean flag used by the static
  CI gate; only written when ALL external-sink checks pass.  Contains
  ``written_by: "verify_private_network_posture"`` for trust verification.

Usage (from scripts/verify_private_network_posture.py)::

    probe = NetworkPostureProbe.from_env()
    result = probe.run()
    probe.write_artifacts(result)
"""

from __future__ import annotations

import ipaddress
import json
import os
import socket
import ssl
from dataclasses import dataclass, field
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[4]

# Default service hostnames — override via AEGISAP_AI_HOSTNAMES env var
# (comma-separated list)
_DEFAULT_HOSTNAMES: list[str] = [
    "openai",   # will be formatted as {name}.openai.azure.com
    "search",   # {name}.search.windows.net
    "storage",  # {name}.blob.core.windows.net
]


def _is_private(ip: str) -> bool:
    """Return True if ``ip`` is in an RFC-1918 private range."""
    try:
        return ipaddress.ip_address(ip).is_private
    except ValueError:
        return False


@dataclass
class ServicePosture:
    hostname: str
    dns_private: bool
    dns_ip: str | None
    public_reachable: bool
    detail: str
    passed: bool = False

    def __post_init__(self) -> None:
        # Passed = DNS resolves to private AND public endpoint is NOT reachable
        self.passed = self.dns_private and not self.public_reachable


@dataclass
class PostureResult:
    services: list[ServicePosture] = field(default_factory=list)

    @property
    def all_passed(self) -> bool:
        return all(s.passed for s in self.services)

    def to_dict(self) -> dict:
        return {
            "all_passed": self.all_passed,
            "training_artifact": False,
            "authoritative_evidence": True,
            "execution_tier": 2,
            "written_by": "verify_private_network_posture",
            "note": "LIVE_DNS_PROBE",
            "services": [
                {
                    "hostname": s.hostname,
                    "dns_private": s.dns_private,
                    "dns_ip": s.dns_ip,
                    "public_reachable": s.public_reachable,
                    "passed": s.passed,
                    "detail": s.detail,
                }
                for s in self.services
            ],
        }


class NetworkPostureProbe:
    """Probe private networking posture for AegisAP AI service endpoints."""

    def __init__(
        self,
        hostnames: list[str],
        connect_timeout: float = 3.0,
    ) -> None:
        self._hostnames = hostnames
        self._timeout = connect_timeout

    @classmethod
    def from_env(cls) -> "NetworkPostureProbe":
        raw = os.environ.get("AEGISAP_AI_HOSTNAMES", "")
        if raw:
            hostnames = [h.strip() for h in raw.split(",") if h.strip()]
        else:
            # Build from AZURE_OPENAI_ENDPOINT etc. if full URLs provided
            hostnames = []
            for env_key in (
                "AZURE_OPENAI_ENDPOINT",
                "AZURE_SEARCH_ENDPOINT",
                "AZURE_STORAGE_ACCOUNT_URL",
            ):
                val = os.environ.get(env_key, "")
                if val:
                    # Extract hostname from URL
                    host = val.replace(
                        "https://", "").replace("http://", "").split("/")[0]
                    if host:
                        hostnames.append(host)
        if not hostnames:
            raise EnvironmentError(
                "Set AEGISAP_AI_HOSTNAMES (comma-separated) or the individual "
                "AZURE_*_ENDPOINT environment variables."
            )
        return cls(hostnames=hostnames)

    def _probe_dns(self, hostname: str) -> tuple[bool, str | None]:
        """Resolve hostname and return (is_private, resolved_ip)."""
        try:
            info = socket.getaddrinfo(hostname, None, socket.AF_INET)
            if not info:
                return False, None
            ip = info[0][4][0]
            return _is_private(ip), ip
        except (socket.gaierror, IndexError):
            return False, None

    def _probe_public_reachability(self, hostname: str) -> bool:
        """Return True if a TLS connection to port 443 succeeds (bad sign)."""
        ctx = ssl.create_default_context()
        try:
            with socket.create_connection(
                (hostname, 443), timeout=self._timeout
            ) as raw_sock:
                with ctx.wrap_socket(raw_sock, server_hostname=hostname):
                    return True
        except (OSError, ssl.SSLError, ConnectionRefusedError):
            return False

    def probe_service(self, hostname: str) -> ServicePosture:
        dns_private, dns_ip = self._probe_dns(hostname)
        public_reachable = self._probe_public_reachability(hostname)
        if dns_private and not public_reachable:
            detail = f"DNS → {dns_ip} (private); public endpoint not reachable. PASS"
        elif not dns_private:
            detail = (
                f"DNS → {dns_ip or 'unresolved'} (NOT private). "
                "Private DNS zone may not be linked to VNET."
            )
        else:
            detail = f"DNS → {dns_ip} (private) but public endpoint IS reachable. FAIL"
        return ServicePosture(
            hostname=hostname,
            dns_private=dns_private,
            dns_ip=dns_ip,
            public_reachable=public_reachable,
            detail=detail,
        )

    def run(self) -> PostureResult:
        """Probe all configured hostnames and return a PostureResult."""
        return PostureResult(
            services=[self.probe_service(h) for h in self._hostnames]
        )

    def write_artifacts(self, result: PostureResult) -> None:
        """Write the posture and external-sink artifacts to build/day12/."""
        out_dir = _ROOT / "build" / "day12"
        out_dir.mkdir(parents=True, exist_ok=True)

        # Full posture report — always written
        posture_path = out_dir / "private_network_posture.json"
        posture_path.write_text(json.dumps(result.to_dict(), indent=2))

        # External-sink disabled flag — only written when all checks pass
        if result.all_passed:
            sink_path = out_dir / "external_sink_disabled.json"
            sink_data = {
                "external_sink_disabled": True,
                "written_by": "verify_private_network_posture",
                "training_artifact": False,
                "authoritative_evidence": True,
                "execution_tier": 2,
                "note": "LIVE_DNS_PROBE",
                "services_checked": [s.hostname for s in result.services],
            }
            sink_path.write_text(json.dumps(sink_data, indent=2))
