
from typing import Callable, Dict, Any

class PolicyViolation(Exception):
    """Raised when a policy check fails."""

class PolicyEngine:
    def __init__(self, audit=None):
        self._policies: Dict[str, Callable[[Dict[str,Any]], None]] = {}
        self.audit = audit

    def policy(self, name: str):
        def _decorator(fn: Callable[[Dict[str,Any]], None]):
            self._policies[name] = fn
            if self.audit:
                self.audit.log("policy.registered", name=name)
            return fn
        return _decorator

    def enforce(self, service: Dict[str,Any]):
        for name, fn in self._policies.items():
            try:
                fn(service)
            except PolicyViolation as e:
                if self.audit:
                    self.audit.log("policy.violation", policy=name, reason=str(e))
                raise
        if self.audit:
            self.audit.log("policy.pass", policies=list(self._policies))
