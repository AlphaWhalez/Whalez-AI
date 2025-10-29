"""Policy enforcement for the Stage 7 governance layer."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional
import yaml

try:  # Stage 6 TLS bootstrap
    from core.domain_authority import manager as domain_manager
except Exception:  # pragma: no cover - optional dependency during docs builds
    domain_manager = None


@dataclass
class PolicyLimits:
    max_concurrent_rollouts: int = 1
    max_restarts_per_hour: int = 3
    cpu_quota_hint: str = "soft"


@dataclass
class PolicySecurity:
    tls_required: bool = True
    signed_artifacts_only: bool = False


@dataclass
class PolicyApprovals:
    require_manual_for_major: bool = True


@dataclass
class PolicyDocument:
    allowed_adapters: List[str] = field(default_factory=list)
    limits: PolicyLimits = field(default_factory=PolicyLimits)
    approvals: PolicyApprovals = field(default_factory=PolicyApprovals)
    security: PolicySecurity = field(default_factory=PolicySecurity)

    @classmethod
    def from_dict(cls, payload: Dict[str, object]) -> "PolicyDocument":
        allow = payload.get("allow") or {}
        limits = payload.get("limits") or {}
        approvals = payload.get("approvals") or {}
        security = payload.get("security") or {}
        return cls(
            allowed_adapters=[str(x) for x in allow.get("adapters", [])],
            limits=PolicyLimits(
                max_concurrent_rollouts=int(limits.get("max_concurrent_rollouts", 1)),
                max_restarts_per_hour=int(limits.get("max_restarts_per_hour", 3)),
                cpu_quota_hint=str(limits.get("cpu_quota_hint", "soft")),
            ),
            approvals=PolicyApprovals(
                require_manual_for_major=bool(approvals.get("require_manual_for_major", True))
            ),
            security=PolicySecurity(
                tls_required=bool(security.get("tls_required", True)),
                signed_artifacts_only=bool(security.get("signed_artifacts_only", False)),
            ),
        )


def _version_parts(version: str) -> List[int]:
    parts: List[int] = []
    for part in version.split("."):
        try:
            parts.append(int(part))
        except ValueError:
            parts.append(0)
    return parts or [0]


def _is_major_bump(current: Optional[str], candidate: Optional[str]) -> bool:
    if not current or not candidate:
        return False
    cur_major = _version_parts(current)[0]
    cand_major = _version_parts(candidate)[0]
    return cand_major > cur_major


class PolicyViolation(Exception):
    pass


class PolicyEngine:
    """Central policy guard used by the orchestrator and deployer."""

    def __init__(self, path: Path | str = Path("config/policies.yaml")) -> None:
        self.path = Path(path)
        self.document = self._load()

    def _load(self) -> PolicyDocument:
        if not self.path.exists():
            raise FileNotFoundError(self.path)
        payload = yaml.safe_load(self.path.read_text(encoding="utf-8")) or {}
        return PolicyDocument.from_dict(payload)

    # --- Security gates -------------------------------------------------

    def ensure_tls_ready(self) -> Optional[Dict[str, object]]:
        if not self.document.security.tls_required:
            return None
        if domain_manager is None:  # pragma: no cover - docs builds
            raise PolicyViolation("TLS manager unavailable")
        tls_info = domain_manager.main()
        if not tls_info:
            raise PolicyViolation("TLS bootstrap did not return configuration")
        return tls_info

    # --- Adapter policy -------------------------------------------------

    def validate_adapter(self, adapter_name: str) -> None:
        allowed = self.document.allowed_adapters
        if allowed and adapter_name not in allowed:
            raise PolicyViolation(f"adapter '{adapter_name}' not permitted by policy")

    # --- Rollout policy -------------------------------------------------

    def check_rollout_limits(self, active_rollouts: int) -> None:
        limit = self.document.limits.max_concurrent_rollouts
        if active_rollouts > limit:
            raise PolicyViolation(
                f"max concurrent rollouts reached ({active_rollouts}/{limit})"
            )

    def requires_manual_approval(self, current_version: Optional[str], next_version: Optional[str]) -> bool:
        if not self.document.approvals.require_manual_for_major:
            return False
        return _is_major_bump(current_version, next_version)

    def guard_version_transition(
        self, *,
        service: str,
        current_version: Optional[str],
        next_version: Optional[str],
        approved: bool,
    ) -> None:
        if self.requires_manual_approval(current_version, next_version) and not approved:
            raise PolicyViolation(
                f"manual approval required for major upgrade of {service} ({current_version}→{next_version})"
            )

    # --- Artifact policy ------------------------------------------------

    def guard_artifact(self, *, signed: bool) -> None:
        if self.document.security.signed_artifacts_only and not signed:
            raise PolicyViolation("unsigned artifact blocked by policy")


__all__ = ["PolicyEngine", "PolicyViolation", "PolicyDocument"]
