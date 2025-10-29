# Stage 7 – Autonomous Service Governance & Deployment

This runbook explains how to declare desired state, drive deployments, and
investigate outcomes for the Stage 7 orchestration layer.

## 1. Configuration quick start

Two YAML files define governance behaviour:

- `config/services.yaml` – the desired state for each service (command, ports,
  rollout, health).
- `config/policies.yaml` – guardrails such as allowed adapters, rollout limits,
  and TLS requirements.

Whenever you change either file the orchestrator will reload them on the next
reconcile cycle.  Use semantic environment variables such as `VERSION` inside
the service definition so that policy checks can differentiate major releases.

### Health probes and SLOs

`health.probe` controls how the orchestrator verifies new instances.  Supported
probe types are `http` and `https`; the orchestrator automatically targets
`127.0.0.1` for HTTP services and the Stage‑6 TLS host for HTTPS.  `health.slo`
values accept comparator strings such as `">=99%"` for success rate or
"`<=250`" for p95 latency (milliseconds).

### Rollout strategies

- **Blue‑green** swaps between a `blue` and `green` slot once the standby slot is
  healthy and passes SLOs.
- **Canary** launches a `canary` variant, waits for the pause window, then
  promotes it to primary if everything looks good.

## 2. Operating the orchestrator

### Linux / macOS

```bash
scripts/linux/start_orchestrator.sh       # default: loop every 30s in dry‑run mode
GOVERNANCE_EXECUTE=1 scripts/linux/start_orchestrator.sh --loop 10
```

### Windows

```bat
scripts\windows\start_orchestrator.bat   # default loop and dry‑run
set GOVERNANCE_EXECUTE=1
scripts\windows\start_orchestrator.bat --loop 10
```

Dry‑run mode records audit events and state transitions without spawning real
processes.  Set `GOVERNANCE_EXECUTE=1` to allow the local adapter to fork the
service commands defined in `services.yaml`.

### TLS validation

On start the orchestrator calls the Stage‑6 Domain Authority to confirm that the
self‑managed TLS certs are provisioned.  If TLS is unhealthy it refuses to
progress rollouts and logs an audit event (`rollout_blocked`).

## 3. Audit trail and observability

- Structured JSONL: `logs/audit/deploy_YYYYMMDD.jsonl`
- Machine friendly state snapshots: `logs/governance/state.json`
- Operator friendly summary (surface in the web dashboard):
  `logs/governance/summary.json`

Each audit entry contains the action, service name, adapter, strategy, and any
SLO report or failure reason.  Use `tail -f logs/audit/deploy_*.jsonl` during a
rollout to watch decisions in real time.

## 4. Manual approvals

Set `approvals.require_manual_for_major` in `policies.yaml` to require human
approval when increasing the major version of a service.  The orchestrator looks
for a `VERSION` environment variable in the service definition to determine the
current revision.  Supply `--approve service_name` to the orchestrator when you
want to override the guard (future extension – for now edit the config or bump
version numbers intentionally).

## 5. Troubleshooting

| Symptom | Likely cause | Remedy |
| --- | --- | --- |
| `rollout_blocked` audit entry | TLS bootstrap failed or adapter denied | Confirm Stage 6 TLS via `python -m core.tls_engine.bootstrap` and check adapter list |
| Status stays `failed` | Health probe never succeeded | Verify `health.probe.path` and confirm service listens on the declared port |
| Canary never promotes | Pause window expires with SLO failure | Inspect audit entry for success rate / latency numbers |

If a rollout behaves unexpectedly, compare `config/services.yaml` with the audit
log to ensure the orchestrator saw the latest desired state.
