# Secret Inventory

| Config Item | Current Treatment | Target Treatment | Secret | Notes |
| --- | --- | --- | --- | --- |
| Azure Search admin key | eliminated | not allowed | yes | runtime uses RBAC only |
| Azure Search query key | eliminated | not allowed | yes | runtime uses RBAC only |
| Azure OpenAI API key | eliminated | not allowed | yes | runtime uses Entra token auth |
| `AZURE_KEY_VAULT_URI` | env config | env config | no | locator only |
| `APPLICATIONINSIGHTS_CONNECTION_STRING` | env config | env config | no | treated as non-secret platform config in this repo |
| `AEGISAP_RESUME_TOKEN_SECRET` | local-only helper | Key Vault in cloud | yes | raw env secret forbidden outside local and test |
| `AEGISAP_RESUME_TOKEN_SECRET_NAME` | env config | env config | no | names the Key Vault secret to load |
| `AEGISAP_POSTGRES_DSN` | local-only helper | not allowed in staging or production-like environments | yes | use Entra token auth outside local or test |

## Day 7 Rules

- No Search or OpenAI API keys in runtime env vars, code, or deployment manifests.
- Residual secrets should be read through Key Vault helpers.
- Local-only shortcuts are allowed for labs but must fail closed in cloud-like environments.
