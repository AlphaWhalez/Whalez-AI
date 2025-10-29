"""Policy engine utilities for Whalez-AI governance."""


class PolicyViolation(Exception):
    """Raised when an action violates a governance policy."""


__all__ = ["PolicyViolation"]
