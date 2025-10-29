# CI smoke: verify imports, run evaluate(), then force a reconcile call
from core.orchestrator.recovery_agent import default_agent
from core.governance import PolicyEngine  # ensures package exports exist

def main():
    agent = default_agent()
    report = agent.evaluate()
    print("SELF-HEAL REPORT:", report)
    # Always attempt reconcile; it will be a noop if all healthy
    outcome = agent.reconcile()
    print("SELF-HEAL OUTCOME:", outcome)
    # Success criteria: no exception + outcome has action field
    assert "action" in outcome

if __name__ == "__main__":
    main()
