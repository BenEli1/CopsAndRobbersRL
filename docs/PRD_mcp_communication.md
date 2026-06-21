# PRD - MCP Communication

> **Implementation status (2026-06-21):** separate FastMCP cop/thief services, strict local-observation/action schemas, configurable localhost ports, environment-token validation, bounded retry, local fallback, and a CLI contract smoke are implemented. A real two-process streamable-HTTP action smoke passed on ports 8101/8102. Cloud deployment, rate/queue limiting, and a full six-game remote match remain pending.

## 1. Purpose

Provide two independent agent decision services - one cop and one thief - without moving game rules out of the SDK/environment. Localhost operation is mandatory before optional cloud deployment.

## 2. Architecture and ownership

- `cop_server` loads only the cop inference policy and exposes cop health/metadata/action tools.
- `thief_server` loads only the thief inference policy and exposes equivalent thief tools.
- The match process owns the environment and requests decisions through `RemotePolicy` adapters.
- MCP services do not own positions, scoring, turn order, opponent-private data, Gmail, or match aggregation.
- All outbound calls pass through `ApiGatekeeper` for concurrency, timeout, rate, queue, retry, and redacted logs.

Local defaults are `127.0.0.1:8101` for cop and `127.0.0.1:8102` for thief. Hosts and ports are configuration, never constants in service logic.

## 3. Configuration

```yaml
schema_version: "1.00"
transport: streamable-http
cop:
  host: 127.0.0.1
  port: 8101
thief:
  host: 127.0.0.1
  port: 8102
auth:
  enabled: false
  token_env: MARL_MCP_TOKEN
timeouts:
  action_seconds: 5
retry:
  max_attempts: 2
```

The real token exists only in the environment. Config stores its variable name. Authentication is disabled in the zero-secret default config; when enabled, both client and server fail closed if the named environment variable is missing, and comparison is constant-time.

## 4. Tool contracts

### `health`

Returns service role, API/schema version, policy/checkpoint version, readiness, and correlation ID. It returns no secret or private opponent state.

### `choose_action`

The implemented request fields are `schema_version`, `request_id`, `role`, and a local observation payload. The response echoes schema/request/role and returns a typed movement action plus a nullable barrier target. Match IDs, deadlines, history, policy metadata, and latency diagnostics are future-compatible additions rather than fabricated current fields.

Servers validate exact keys, schema version, role, local cell values, and response action. They reject global-state keys, absolute cop/thief coordinates, another role's observation, unsupported remote barrier targets, and arbitrary file/model paths. Request-size limits and monotonic step tracking remain future hardening.

### Optional `metadata`

Returns model architecture identifier, observation/action schema versions, and checkpoint hash. It must not return weights or environment variables.

## 5. Authentication and security

- Shared-token validation is configurable for localhost and required when `auth.enabled` is true. A cloud version must replace the tool-argument placeholder with transport-level OAuth/Bearer authorization.
- Compare tokens in constant-time where supported; reject missing/invalid tokens with no policy output.
- Tokens are revocable and separately provisioned in cloud; rotation does not require code changes.
- Logs redact authorization headers and avoid full observations unless a safe debug fixture is enabled.
- Cloud adds TLS, secret-manager injection, least-privilege identity, network restrictions, origin controls where relevant, request-size limits, and audit logs.
- Never expose pickle loading or user-controlled checkpoint paths over MCP.

## 6. Failure modes

| Failure | Required behavior |
|---|---|
| Service unavailable / connection refused | Bounded retry through gatekeeper; then `TechnicalFailure`. |
| Timeout | Cancel/ignore late response, retry only within step deadline, never apply stale action. |
| Invalid token | Fail closed, no retry with same credentials, sanitized audit event. |
| Malformed request | Structured validation error; no policy invocation. |
| Invalid action response | Reject response; technical failure, not random fallback. |
| Wrong role/request/step ID | Reject as stale/cross-wired response. |
| Model not loaded | Health reports not ready; action requests rejected. |
| Rate/queue limit | Queue within bounds or return backpressure; never unbounded memory growth. |
| Mid-sub-game disconnect | Abort that sub-game as technical failure and retry according to match policy; do not score it. |
| Duplicate request | Idempotency cache may return the original action for the same request/checkpoint; it must never run a second stateful update. |

## 7. Local-first validation

The implemented CLI smoke exercises schemas, gatekeepers, and both role tools in process and reports whether the optional SDK is installed. A separate manual integration smoke started both FastMCP processes on distinct ports and invoked each through the official streamable-HTTP client. Completing a six-valid-sub-game remote match, authenticated network smoke, restart, duplicate/stale ID, and backpressure evidence remain acceptance work.

## 8. Cloud-ready design

Transport and service interfaces stay unchanged; deployment config supplies external URLs. Services load immutable inference checkpoints in evaluation mode. A deployment must expose health/readiness probes and pin dependency/model versions. Cloud is optional: if not completed and verified, docs must state that only localhost is implemented.

## 9. Acceptance criteria

- **MCP-AC-1:** Two independently startable services use distinct configured localhost ports and correct role-specific policies.
- **MCP-AC-2:** Every action input contains local observation/history only; global-state and opponent-private fields fail validation.
- **MCP-AC-3:** Valid token requests succeed; missing/invalid tokens reveal no action and secrets never appear in logs.
- **MCP-AC-4:** Gatekeeper enforces configured concurrency, rate, bounded queue, timeout, and retry behavior.
- **MCP-AC-5:** Stale, cross-role, malformed, oversized, and invalid-action responses cannot mutate the environment.
- **MCP-AC-6:** A six-valid-game local match completes using both services; injected outages produce unscored technical failures and documented recovery.
- **MCP-AC-7:** Optional cloud claims require TLS/auth/revocation/readiness evidence; otherwise cloud remains future work.

## 10. Alternatives and constraints

A single shared server was rejected because the assignment asks for two independent endpoints and failure isolation is weaker. Direct REST can be a transport adapter, but the documented external contract remains MCP. Public anonymous deployment is prohibited. FastMCP/Prefect are suggested course technologies, not permission to couple domain logic to one framework.
