"""Agent registry for the Whalez-AI stack."""

from .interface_agent import InterfaceAgent
from .self_hosting_agent import SelfHostingAgent
from .security_agent import SecurityAgent
from .treasury_agent import TreasuryAgent
from .ledger_agent import LedgerAgent
from .field_agent import FieldAgent
from .governance_agent import GovernanceAgent

__all__ = [
    "InterfaceAgent",
    "SelfHostingAgent",
    "SecurityAgent",
    "TreasuryAgent",
    "LedgerAgent",
    "FieldAgent",
    "GovernanceAgent",
]
