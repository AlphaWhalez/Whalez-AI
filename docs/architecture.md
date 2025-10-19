# Architecture Overview

The Whalez-AI Sovereign Stack is organized into three primary layers:

1. **Core Services** – identity, affirmation logging and deterministic domain
   derivation. These modules live under `core/` and are pure-Python utilities.
2. **Agents** – lightweight actors that expose APIs, record deployments or
   enforce defensive controls. Agents are located under `src/agents/`.
3. **Virtual Machine** – a small state machine located under `src/vm/` that
   produces deterministic block files for the ledger.

The `run_whalez.py` launcher ties the layers together. When executed it:

1. Loads the identity configuration and records a subdomain affirmation.
2. Initializes security monitoring and the interface agent.
3. Writes a deployment proof via the self-hosting agent.
4. Starts the HTTP server for the UI.

Supporting documentation and frontend assets live in `docs/` and `web/` respectively.
