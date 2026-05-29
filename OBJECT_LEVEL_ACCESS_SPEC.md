# OPEN FNR Object-Level Access Specification

Status: SEC-2 foundation  
Date: 2026-05-29  
Related sprint: SEC-2 RBAC And Object-Level Access

## 1. Purpose

This document fixes the shared RBAC and object-level access boundary for OPEN FNR APIs.

## 2. Scope Dimensions

Object access is evaluated through:

- role;
- region;
- category;
- supplier id when the object is supplier-sensitive;
- active user flag.

Admin role bypasses role checks but still flows through explicit policy helpers for auditable behavior.

## 3. Shared Policy Helpers

| Helper | Purpose |
| --- | --- |
| `has_any_role()` | Checks role membership with Admin override. |
| `assert_any_role()` | Raises API 403 on role denial. |
| `has_object_scope()` | Checks region, category and optional supplier scope. |
| `assert_object_scope()` | Raises API 403 on object-scope denial. |
| `assert_service_account()` | Checks service account identity for integration actions. |

## 4. API Boundary

| Endpoint | Purpose |
| --- | --- |
| `GET /security/access-check` | Compatibility check for role + object scope. |
| `GET /security/policy-check` | Shared policy v1 check for role, region and category. |
| `GET /security/object-access-check` | Shared policy v2 check including supplier-sensitive object access. |

## 5. Acceptance Criteria

SEC-2 foundation is accepted when:

- shared policy supports supplier scope;
- supplier-sensitive object access is denied for users outside supplier scope;
- access checks return 403 on policy denial;
- existing region/category behavior remains compatible;
- tests cover positive and negative supplier object paths.
