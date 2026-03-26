# Identity Matrix

| Principal | Host Resource | Resource Accessed | Operation | Role | Why |
| --- | --- | --- | --- | --- | --- |
| Runtime API identity | Container App system-assigned identity | Azure OpenAI | invoke model | `Cognitive Services OpenAI User` | execute Day 1 and Day 4 runtime calls |
| Runtime API identity | Container App system-assigned identity | Azure AI Search | query | `Search Index Data Reader` | retrieve evidence only |
| Runtime API identity | Container App system-assigned identity | Storage account | read blobs | `Storage Blob Data Reader` | read evidence documents |
| Runtime API identity | Container App system-assigned identity | Key Vault | read residual secrets | `Key Vault Secrets User` | fetch resume token secret by name |
| Pull identity | Container App user-assigned identity | ACR | pull image | `AcrPull` | registry access only |
| Pull identity | Container App user-assigned identity | Key Vault | secret reference plumbing | `Key Vault Secrets User` | future-proof for platform-managed secret refs |
| Jobs identity scaffold | user-assigned identity | future replay or batch workloads | read only by default | scoped later | split replay from runtime blast radius |
| Search admin identity scaffold | user-assigned identity | Azure AI Search | index and schema admin | `Search Service Contributor`, `Search Index Data Contributor` | keep indexing off runtime |
| Developer principal | human identity | bootstrap resources | provision and seed | bootstrap roles from Day 0 | local setup and troubleshooting |
