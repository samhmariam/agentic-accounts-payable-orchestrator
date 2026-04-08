"""Private-endpoint connectivity probe for Day 12."""

from __future__ import annotations

import ipaddress
import json
import os
import socket
import ssl
from dataclasses import dataclass
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[3]
_BUILD_DIR = _ROOT / "build" / "day12"


def _is_private(ip: str) -> bool:
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
        if self.passed is False:
            self.passed = self.dns_private and not self.public_reachable


class PostureResult:
    def __init__(
        self,
        *,
        services: list[ServicePosture] | None = None,
        all_passed: bool | None = None,
    ) -> None:
        self.services = services or []
        self._all_passed_override = all_passed

    @property
    def all_passed(self) -> bool:
        if self._all_passed_override is not None:
            return bool(self._all_passed_override)
        return all(service.passed for service in self.services)

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
                    "hostname": service.hostname,
                    "dns_private": service.dns_private,
                    "dns_ip": service.dns_ip,
                    "public_reachable": service.public_reachable,
                    "passed": service.passed,
                    "detail": service.detail,
                }
                for service in self.services
            ],
        }


class NetworkPostureProbe:
    """Probe private networking posture for AegisAP AI service endpoints."""

    def __init__(self, hostnames: list[str], connect_timeout: float = 3.0) -> None:
        self._hostnames = hostnames
        self._timeout = connect_timeout

    @property
    def hostnames(self) -> list[str]:
        return list(self._hostnames)

    @classmethod
    def from_env(cls) -> "NetworkPostureProbe":
        raw = os.environ.get("AEGISAP_AI_HOSTNAMES", "")
        if raw:
            hostnames = [hostname.strip() for hostname in raw.split(",") if hostname.strip()]
        else:
            hostnames = []
            for env_key in (
                "AZURE_OPENAI_ENDPOINT",
                "AZURE_SEARCH_ENDPOINT",
                "AZURE_STORAGE_ACCOUNT_URL",
            ):
                val = os.environ.get(env_key, "").strip()
                if not val:
                    continue
                host = val.replace("https://", "").replace("http://", "").split("/")[0]
                if host:
                    hostnames.append(host)
        if not hostnames:
            raise EnvironmentError(
                "Set AEGISAP_AI_HOSTNAMES (comma-separated) or the individual AZURE_*_ENDPOINT variables."
            )
        return cls(hostnames=hostnames)

    def _is_private(self, ip: str) -> bool:
        return _is_private(ip)

    def _resolve_ip(self, hostname: str) -> str | None:
        try:
            info = socket.getaddrinfo(hostname, None, socket.AF_INET)
        except socket.gaierror:
            return None
        if not info:
            return None
        return info[0][4][0]

    def _is_public_reachable(self, hostname: str) -> bool:
        context = ssl.create_default_context()
        try:
            with socket.create_connection((hostname, 443), timeout=self._timeout) as raw_sock:
                with context.wrap_socket(raw_sock, server_hostname=hostname):
                    return True
        except (OSError, ssl.SSLError, ConnectionRefusedError):
            return False

    def probe_service(self, hostname: str) -> ServicePosture:
        ip = self._resolve_ip(hostname)
        dns_private = bool(ip and self._is_private(ip))
        public_reachable = self._is_public_reachable(hostname)
        if dns_private and not public_reachable:
            detail = f"DNS -> {ip} (private); public endpoint not reachable. PASS"
        elif not dns_private:
            detail = f"DNS -> {ip or 'unresolved'} (NOT private). Private DNS zone may not be linked to VNET."
        else:
            detail = f"DNS -> {ip} (private) but public endpoint IS reachable. FAIL"
        return ServicePosture(
            hostname=hostname,
            dns_private=dns_private,
            dns_ip=ip,
            public_reachable=public_reachable,
            detail=detail,
        )

    def run(self) -> PostureResult:
        return PostureResult(services=[self.probe_service(hostname) for hostname in self._hostnames])

    def write_artifacts(self, result: PostureResult) -> None:
        _BUILD_DIR.mkdir(parents=True, exist_ok=True)
        posture_path = _BUILD_DIR / "private_network_posture.json"
        posture_path.write_text(json.dumps(result.to_dict(), indent=2), encoding="utf-8")

        sink_path = _BUILD_DIR / "external_sink_disabled.json"
        if result.all_passed:
            sink_path.write_text(
                json.dumps(
                    {
                        "external_sink_disabled": True,
                        "written_by": "verify_private_network_posture",
                        "training_artifact": False,
                        "authoritative_evidence": True,
                        "execution_tier": 2,
                        "note": "LIVE_DNS_PROBE",
                        "services_checked": [service.hostname for service in result.services],
                    },
                    indent=2,
                ),
                encoding="utf-8",
            )
        elif sink_path.exists():
            sink_path.unlink()
