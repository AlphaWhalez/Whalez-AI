# Security Stack (Phase-C)

## Overview
- **Vault**: Encrypted at rest under `.secrets/` (git-ignored) using Fernet derived via PBKDF2-SHA256.
- **Tokens**: JWT HS256 with explicit scopes, defaulting to `read:secrets`.

## Local Development
1. `export VAULT_MASTER_KEY="local-strong-key"`
2. `export TOKEN_SECRET="local-strong-token"`
3. `python -m scripts.ci.preflight_security`

## API Endpoints
- `POST /security/auth/token` → `{ "token": "..." }`
- `GET  /security/auth/verify` (Bearer) → `{ ok: true, payload: ... }`
- `POST /security/secrets/set` (Bearer `write:secrets`)
- `GET  /security/secrets/get?key=...` (Bearer `read:secrets`)

## CI Guidance
The GitHub Actions workflow runs `scripts/ci/preflight_security.py` which
initialises the vault, round-trips a value, and ensures token mint/verify works.

## Operations Notes
- Rotate `VAULT_MASTER_KEY` and `TOKEN_SECRET` via environment management (e.g.
  GitHub secrets). Re-deploy to apply changes.
- Vault files live under `.secrets/`; remove files to revoke stored values.
