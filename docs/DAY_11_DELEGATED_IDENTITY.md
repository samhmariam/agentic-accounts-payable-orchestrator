# DAY 11 — Delegated Identity & OBO

> **Status:** Part of AegisAP curriculum v3 (Days 11-14 extension)  
> **WAF:** Security · Reliability  
> **Notebook:** `notebooks/day_11_delegated_identity_obo.py`  
> **New gates:** `gate_delegated_identity` · `gate_obo_app_identity` · `gate_obo_exchange` · `gate_actor_binding`

---

## Summary

Day 11 implements the identity planes that Days 1-10 deferred:

1. **On-Behalf-Of (OBO) flow** — the orchestrator acquires downstream API tokens using
   the human operator's identity, not a shared service principal.
2. **Actor verification** — Entra group membership check via Microsoft Graph to confirm
   the invoking human is an approved AP approver before escalations execute.

## Architecture

```
Human (Approver) → APIM → ACA Orchestrator
                               │
                [OBO exchange: user token → downstream token]
                               │
                    Azure OpenAI / AI Search / Graph
```

## Source Modules

| Module | Key class | Description |
|---|---|---|
| `src/aegisap/identity/obo.py` | `OboTokenProvider` | MSAL OBO exchange |
| `src/aegisap/identity/actor_verifier.py` | `ActorVerifier` | Entra group check via Graph |

## Gate Artifacts

| Artifact | Path | Gate |
|---|---|---|
| OBO contract | `build/day11/obo_contract.json` | `gate_delegated_identity` (composite) |

## Script

```bash
python scripts/verify_delegated_identity_contract.py
```

Required env: `AZURE_TENANT_ID`, `AZURE_CLIENT_ID`, `AZURE_CLIENT_SECRET`,
`AZURE_USER_ASSERTION`, `AEGISAP_APPROVER_GROUP_ID`

## Security Concerns

- **Authority confusion** — always validate the `iss` and `aud` claims of the incoming
  user token before passing it to OBO. Never pass an arbitrary string as `user_assertion`.
- **Token caching** — MSAL caches OBO tokens by hash of the user assertion. Revoked
  tokens may still be served from cache until TTL. Set `cache_enable_shared_cache=False`
  in production to prevent cross-request contamination.
- **Scope creep** — request only the minimum scopes needed. Do not use
  `https://graph.microsoft.com/.default` if only reading group membership.
