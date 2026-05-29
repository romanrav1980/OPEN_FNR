# OPEN FNR Production Authentication Specification

Status: SEC-1 foundation  
Date: 2026-05-29  
Related sprint: SEC-1 OIDC/JWT Authentication

## 1. Purpose

This document fixes the production authentication boundary for OPEN FNR APIs.

## 2. Requirements

| Area | Requirement |
| --- | --- |
| Protocol | OIDC/JWT bearer token authentication. |
| Signature | RS256 verification through configured JWKS. |
| Issuer | `OPEN_FNR_OIDC_ISSUER` must match token `iss` when configured. |
| Audience | `OPEN_FNR_OIDC_AUDIENCE` must match token `aud` when configured. |
| Expiration | `exp` is mandatory and expired tokens are rejected. |
| Not before | `nbf` is respected with `OPEN_FNR_OIDC_CLOCK_SKEW_SECONDS`. |
| DEV bypass | Allowed only in `dev` and `test` runtime modes when explicitly enabled. |
| STAGE/PROD | JWKS URL is mandatory when auth is enabled and DEV bypass is disabled. |

## 3. Configuration

| Setting | Purpose |
| --- | --- |
| `OPEN_FNR_AUTH_ENABLED` | Enables authentication middleware. |
| `OPEN_FNR_AUTH_DEV_BYPASS_ENABLED` | Allows controlled DEV/TEST header bypass only. |
| `OPEN_FNR_OIDC_ISSUER` | Expected IdP issuer. |
| `OPEN_FNR_OIDC_AUDIENCE` | Expected API audience. |
| `OPEN_FNR_OIDC_JWKS_URL` | JWKS source for RS256 verification. |
| `OPEN_FNR_OIDC_CLOCK_SKEW_SECONDS` | Allowed `nbf` and expiration clock skew. |

## 4. Public Paths

The following paths remain public:

- `/health`;
- `/ready`;
- `/metadata`;
- `/docs`;
- `/redoc`;
- `/openapi.json`;
- `/auth/idp-readiness`.

## 5. Acceptance Criteria

SEC-1 foundation is accepted when:

- APIs reject missing bearer tokens when auth is enabled;
- DEV bypass is not accepted in STAGE/PROD runtime modes;
- JWT validation rejects missing `exp`, expired tokens, wrong audience, wrong issuer and future `nbf` beyond clock skew;
- RS256 signature verification is tested with JWKS;
- readiness endpoint reports missing IdP settings before STAGE/PROD rollout;
- no IdP URL, host, port or secret is hardcoded.
