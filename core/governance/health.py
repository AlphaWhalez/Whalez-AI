"""Health and SLO evaluation for services managed by the orchestrator."""

from __future__ import annotations

from dataclasses import dataclass
from time import monotonic, sleep
from typing import Dict, Iterable, List, Optional, Tuple
from urllib import request, error
import ssl

DEFAULT_HOST = "127.0.0.1"


@dataclass
class ProbeResult:
    success: bool
    status_code: Optional[int]
    latency_ms: float
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, object]:
        return {
            "success": self.success,
            "status_code": self.status_code,
            "latency_ms": round(self.latency_ms, 2),
            "error": self.error,
        }


class HealthMonitor:
    def __init__(self, *, tls_host: Optional[str] = None) -> None:
        self.tls_host = tls_host or DEFAULT_HOST
        self._ssl_context = ssl._create_unverified_context()

    # ------------------------------------------------------------------
    def _url_for(self, service, instance_info: Dict[str, object]) -> str:
        health = service.health
        if health is None:
            raise ValueError(f"service '{service.name}' has no health configuration")
        scheme = "https" if health.probe_type == "https" else "http"
        port = None
        # try instance info override first
        if instance_info:
            port = instance_info.get("port") or instance_info.get("ports", [None])[0]
        if not port and service.ports:
            port = service.ports[0]
        if not port:
            raise ValueError(f"service '{service.name}' has no port defined for health probe")
        host = instance_info.get("host") if instance_info else None
        host = host or (self.tls_host if scheme == "https" else DEFAULT_HOST)
        path = health.path.lstrip("/")
        return f"{scheme}://{host}:{port}/{path}"

    def _probe_once(
        self,
        service,
        instance_info: Dict[str, object],
        timeout_seconds: float,
    ) -> ProbeResult:
        url = self._url_for(service, instance_info)
        start = monotonic()
        try:
            req = request.Request(url, method="GET")
            ctx = self._ssl_context if url.startswith("https") else None
            with request.urlopen(req, timeout=timeout_seconds, context=ctx) as resp:
                resp.read(128)  # drain small portion to ensure success
                latency_ms = (monotonic() - start) * 1000.0
                return ProbeResult(True, getattr(resp, "status", None), latency_ms)
        except error.HTTPError as exc:  # considered unhealthy if >=400
            latency_ms = (monotonic() - start) * 1000.0
            return ProbeResult(False, exc.code, latency_ms, error=str(exc))
        except Exception as exc:  # pragma: no cover - networking can vary
            latency_ms = (monotonic() - start) * 1000.0
            return ProbeResult(False, None, latency_ms, error=str(exc))

    # ------------------------------------------------------------------
    def evaluate_slo(self, results: Iterable[ProbeResult], slo: Dict[str, str]) -> Tuple[bool, Dict[str, object]]:
        results = list(results)
        if not slo:
            return True, {"checked": False}
        total = len(results)
        success_count = sum(1 for r in results if r.success)
        success_rate = (success_count / total) * 100 if total else 0
        latency_p95 = 0.0
        if results:
            latencies = sorted(r.latency_ms for r in results)
            index = min(int(0.95 * len(latencies)) - 1, len(latencies) - 1)
            latency_p95 = latencies[index]
        slo_report = {
            "checked": True,
            "success_rate": round(success_rate, 2),
            "latency_p95_ms": round(latency_p95, 2),
        }
        ok = True
        for key, rule in slo.items():
            rule = rule.strip()
            if key == "success_rate":
                threshold = float(rule.strip("%>="))
                if success_rate < threshold:
                    ok = False
            elif key == "latency_p95_ms":
                threshold = float(rule.strip("<= "))
                if latency_p95 > threshold:
                    ok = False
        return ok, slo_report

    # ------------------------------------------------------------------
    def wait_for_healthy(
        self,
        service,
        instance_info: Dict[str, object],
        pause_seconds: float = 0.0,
    ) -> Tuple[bool, Dict[str, object]]:
        health = service.health
        if health is None:
            return True, {"skipped": True}
        attempts: List[ProbeResult] = []
        timeout = health.timeout_seconds
        interval = max(1.0, health.interval_seconds)
        # quick warm-up loop
        for _ in range(3):
            result = self._probe_once(service, instance_info, timeout)
            attempts.append(result)
            if result.success:
                break
            sleep(interval)
        if not attempts[-1].success:
            return False, {
                "reason": "probe_failed",
                "attempts": [r.to_dict() for r in attempts],
            }
        if pause_seconds:
            deadline = monotonic() + pause_seconds
            slo_samples: List[ProbeResult] = []
            while monotonic() < deadline:
                slo_samples.append(self._probe_once(service, instance_info, timeout))
                sleep(interval)
            attempts.extend(slo_samples)
        ok, slo_report = self.evaluate_slo(attempts, health.slo)
        slo_report["attempts"] = [r.to_dict() for r in attempts]
        return ok, slo_report


__all__ = ["HealthMonitor", "ProbeResult"]
