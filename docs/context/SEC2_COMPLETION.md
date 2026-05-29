# SEC-2 Completion Note

Status: completed foundation  
Date: 2026-05-29  
Sprint: SEC-2 RBAC And Object-Level Access

## Scope Completed

- Object-level access specification added:
  - `OBJECT_LEVEL_ACCESS_SPEC.md`.
- Shared policy now supports supplier scope:
  - `Principal.suppliers`;
  - `has_object_scope(..., supplier_id=...)`;
  - `assert_object_scope(..., supplier_id=...)`.
- Security API added:
  - `GET /security/object-access-check`.
- Existing `GET /security/access-check` now supports optional `supplier_id`.
- Tests cover:
  - scoped supplier allow path;
  - wrong supplier deny path;
  - existing region/category compatibility.

## Evidence

- Targeted tests cover policy and security API behavior.
- Targeted tests: 34 passed.
- Full regression: 512 passed, 1 local `.pytest_cache` permission warning.

## Deferred

- Applying JWT-derived user scopes to every business endpoint.
- Persistent user/role/scope repository.
- UI administration for supplier scope.

These are deferred to SEC-3/SEC-4/UI productization because SEC-2 establishes the shared object policy boundary.
