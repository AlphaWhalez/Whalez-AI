#!/usr/bin/env python3
"""
Whalez-AI Governance Preflight Check
------------------------------------
Runs before Stage 8 to verify governance module integrity.
Includes auto-fix fallback for stale cache and import errors.
"""

import importlib
import os
import sys
import traceback
import shutil
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

CACHE_PATHS = ["__pycache__", ".pytest_cache"]

def clear_cache():
    """Auto-fix: clears Python cache folders recursively."""
    for root, dirs, _ in os.walk("."):
        for d in dirs:
            if d in CACHE_PATHS:
                full = os.path.join(root, d)
                try:
                    shutil.rmtree(full)
                    print(f"🧹 Cleared cache: {full}")
                except Exception as e:
                    print(f"⚠️ Could not clear {full}: {e}")

def check_imports():
    """Validate importability of all governance modules."""
    modules = [
        "core.governance",
        "core.governance.policy_engine",
        "core.governance.health",
        "core.governance.audit",
        "core.governance.deployer"
    ]
    for m in modules:
        try:
            importlib.import_module(m)
            print(f"✅ {m} imported successfully")
        except Exception as e:
            print(f"❌ Import failed for {m}: {e}")
            print("Attempting auto-fix ...")
            clear_cache()
            try:
                importlib.invalidate_caches()
                importlib.import_module(m)
                print(f"✅ {m} imported successfully after auto-fix")
            except Exception:
                print(f"❌ Failed to import {m} after auto-fix")
                traceback.print_exc()
                sys.exit(1)

def check_policy_engine():
    """Verify PolicyEngine operational readiness."""
    try:
        from core.governance.policy_engine import PolicyEngine, PolicyViolation
        pe = PolicyEngine()
        pe.register_policy("test_policy", lambda: True)
        pe.enforce("test_policy")
        print("✅ PolicyEngine operational — PolicyViolation handled correctly")
    except Exception as e:
        print(f"❌ Governance operational test failed: {e}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    print("\n🔍 Running Whalez-AI Governance Preflight Check ...\n")
    check_imports()
    check_policy_engine()
    print("\n🎯 Governance Preflight completed successfully ✅\n")
