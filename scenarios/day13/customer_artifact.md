# Customer Escalation - Day 13

Subject: The MCP server stopped advertising the payment-hold tool

Our partner integration can no longer see the governed write path in the MCP
contract. They are asking for direct orchestrator access unless we restore the
boundary today.

What we need:

- restore the intended MCP contract without bypassing the governed boundary
- prove the write path still preserves compensating-action safety
- document the partner impact and rollback plan in the Day 13 artifact packet
