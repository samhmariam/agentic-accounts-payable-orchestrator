"""Actor verification — confirm that an approval token's OID belongs to the
expected Entra group before committing the approval.

This guard closes the authority-confusion threat class introduced in Day 1:
an invoice routed via Service Bus could arrive with a forged ``actor_oid``
claiming to be a finance director.  The verifier re-checks group membership
directly against the Microsoft Graph API using its own managed-identity
credential, independent of the submitted token.

Usage::

    verifier = ActorVerifier.from_env()
    result = verifier.verify(oid="<entra-user-oid>", required_group_id="<group-object-id>")
    if not result.is_member:
        raise PermissionError("Approval actor is not in the required Entra group")

Environment variables required:
    AZURE_TENANT_ID              — Entra tenant
    AEGISAP_APPROVER_GROUP_ID    — Object ID of the Entra group allowed to approve
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field

import requests
from azure.identity import DefaultAzureCredential


@dataclass
class ActorVerificationResult:
    oid: str
    group_id: str
    is_member: bool
    detail: str
    evidence: dict = field(default_factory=dict)


class ActorVerifier:
    """Verifies Entra group membership for an approval actor.

    Uses the Microsoft Graph transitiveMemberOf API so nested group
    membership is resolved correctly.
    """

    GRAPH_BASE = "https://graph.microsoft.com/v1.0"
    GRAPH_SCOPE = "https://graph.microsoft.com/.default"

    def __init__(self, required_group_id: str) -> None:
        self._required_group_id = required_group_id
        self._credential = DefaultAzureCredential()

    @classmethod
    def from_env(cls) -> "ActorVerifier":
        group_id = os.environ["AEGISAP_APPROVER_GROUP_ID"]
        return cls(required_group_id=group_id)

    def _get_graph_token(self) -> str:
        token = self._credential.get_token(self.GRAPH_SCOPE)
        return token.token

    def verify(
        self,
        oid: str,
        required_group_id: str | None = None,
    ) -> ActorVerificationResult:
        """Check whether ``oid`` is a transitive member of the required group.

        Args:
            oid: The Entra user object ID from the OBO token claims.
            required_group_id: Overrides the instance default if provided.

        Returns:
            ActorVerificationResult with is_member flag and evidence.
        """
        group_id = required_group_id or self._required_group_id
        token = self._get_graph_token()
        headers = {"Authorization": f"Bearer {token}"}
        url = (
            f"{self.GRAPH_BASE}/users/{oid}/transitiveMemberOf"
            f"/microsoft.graph.group?$filter=id eq '{group_id}'&$select=id,displayName"
        )
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        members = data.get("value", [])
        is_member = any(g.get("id") == group_id for g in members)
        detail = (
            f"OID {oid} IS a member of group {group_id}"
            if is_member
            else f"OID {oid} is NOT a member of group {group_id}"
        )
        return ActorVerificationResult(
            oid=oid,
            group_id=group_id,
            is_member=is_member,
            detail=detail,
            evidence={"graph_response_count": len(
                members), "group_id": group_id},
        )
