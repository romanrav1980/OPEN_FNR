# OPEN FNR CI/CD Release Gate Strategy

Status: DEP-2 foundation  
Date: 2026-05-29

## 1. Purpose

This document fixes the release gates required before any deployment candidate can move toward STAGE or PROD.

## 2. Required Gates

| Gate | Evidence |
| --- | --- |
| Backend and quality tests | `.github/workflows/ci.yml` job `backend-and-quality` runs `python -m pytest`. |
| Frontend build | `.github/workflows/ci.yml` job `frontend` runs `npm ci` and `npm run build`. |
| Compose config validation | `.github/workflows/ci.yml` job `compose-config` validates DEV, TEST and STAGE compose config. |
| Environment topology | `tests/deployment/test_environment_topology.py` validates DEV/TEST/STAGE/PROD templates. |
| Secret safety | `tests/quality/test_no_committed_secrets.py`. |
| Network config safety | `tests/quality/test_no_hardcoded_network_config.py`. |
| Encoding safety | `tests/quality/test_text_encoding.py`. |

## 3. Release Artifact Rules

- Release notes must use `docs/release/RELEASE_NOTES_TEMPLATE.md`.
- Every release candidate must reference commit SHA, sprint range, test evidence and rollback plan.
- Failed migration, failed tests or missing release notes block promotion.
- Release artifacts must not contain environment secrets.

## 4. Acceptance Criteria

DEP-2 foundation is accepted when:

- CI workflow contains backend, frontend and compose validation jobs;
- release notes template exists;
- release gate tests pass;
- full regression passes.
