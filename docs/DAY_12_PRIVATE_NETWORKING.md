# DAY 12 — Private Networking Constraints

> **Status:** Part of AegisAP curriculum v3 (Days 11-14 extension)  
> **WAF:** Security · Reliability  
> **Notebook:** `notebooks/day_12_private_networking_constraints.py`  
> **New gates:** `gate_private_network_static` · `gate_private_network_posture`

---

## Summary

Day 12 implements the NFR from Day 2: all AI services must have
`publicNetworkAccess=Disabled` and be reachable only via Private Endpoints inside
a VNET-injected Container Apps environment.

## Architecture

See [DAY_02_STATE_FLOW.md](DAY_02_STATE_FLOW.md) for the NFR origin.

Four required layers:
1. VNET injection for ACA (`internal: true`)
2. `publicNetworkAccess=Disabled` on every AI service
3. Private Endpoints per service
4. Private DNS zones linked to the VNet

## Bicep Modules

| File | Purpose |
|---|---|
| `infra/network/vnet.bicep` | VNet with 3 subnets (ACA, PE, Functions) |
| `infra/network/private_dns.bicep` | 5 DNS zones + VNet links |
| `infra/network/private_endpoints.bicep` | PEs for OpenAI, Search, Storage, Key Vault |
| `infra/network/private_aca.bicep` | VNET-injected ACA environment |

## Gate Artifacts

| Artifact | Path | Gate | Written when |
|---|---|---|---|
| Posture report | `build/day12/private_network_posture.json` | `gate_private_network_posture` | Always |
| Static trust file | `build/day12/external_sink_disabled.json` | `gate_private_network_static` | Only if all_passed |

## Scripts

```bash
# Live probe (run from inside the VNet or with VPN)
python scripts/verify_private_network_posture.py

# ARM API data residency check  
python scripts/verify_private_network_static.py
```

## Common Failure Modes

See `evals/failure_drills/drill_03_dns_misconfiguration.json` and
`evals/failure_drills/drill_04_public_endpoint_reenabled.json`.

<!-- CAPSTONE_B -->

---

## FDE Rubric — Day 12 (100 points)

| Dimension | Points |
|---|---|
| Network posture design | 30 |
| Static vs live proof understanding | 20 |
| Dependency management realism | 20 |
| Security exception handling | 15 |
| Oral defense | 15 |

**Pass bar: 80.  Elite bar: 90.**

**Zero-tolerance conditions:** (1) public endpoint described as acceptable in production; (2) security exception granted with no expiry or compensating control. Either condition overrides total to 0.

**Capstone B day** — primary deliverables are in the claims intake transfer domain.

## Oral Defense Prompts

1. Which network dependency has the longest lead time and what is your plan if it is not resolved before production cutover?
2. You temporarily enable a public endpoint in dev. Walk through every compensating control, the expiry date, and who holds the removal obligation.
3. Who approves a security exception in your enterprise, what evidence is mandatory in the request, and what happens at expiry if no renewal is filed?

## Artifact Scaffolds

- `docs/curriculum/artifacts/day12/NETWORK_DEPENDENCY_REGISTER.md`
- `docs/curriculum/artifacts/day12/SECURITY_EXCEPTION_REQUEST.md`
- `docs/curriculum/artifacts/day12/EGRESS_CONTROL_POLICY.md`
