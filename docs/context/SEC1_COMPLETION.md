# SEC-1 Completion Note

Status: completed foundation  
Date: 2026-05-29  
Sprint: SEC-1 OIDC/JWT Authentication

## Scope Completed

- Production authentication specification added:
  - `PRODUCTION_AUTHENTICATION_SPEC.md`.
- JWT validation hardened:
  - `exp` is mandatory;
  - expired tokens are rejected;
  - future `nbf` is rejected outside configured clock skew.
- Config added:
  - `OPEN_FNR_OIDC_CLOCK_SKEW_SECONDS`.
- DEV bypass boundary verified:
  - allowed only in DEV/TEST;
  - rejected in STAGE even if bypass flag is accidentally true.

## Evidence

- Targeted tests cover auth disabled mode, IdP readiness, bearer requirement, DEV bypass, issuer/audience, RS256 JWKS, missing expiration and future `nbf`.
- Targeted tests: 35 passed.
- Full regression: 509 passed, 1 local `.pytest_cache` permission warning.

## Deferred

- User/group synchronization from enterprise IdP.
- Token introspection endpoint.
- Refresh/session management for the frontend.

These are deferred to SEC-2/SEC-3/UI productization because SEC-1 establishes the backend API authentication boundary.
