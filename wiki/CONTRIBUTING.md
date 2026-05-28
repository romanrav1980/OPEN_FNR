# Documentation Guide

## Style

- Use Markdown.
- Prefer short sections.
- Link to canonical documents instead of duplicating large blocks.
- Keep decisions explicit.
- Keep open questions visible.
- Use tables for ownership, scope and acceptance criteria.
- Use Mermaid only where it clarifies flow.

## Page Types

| Type | Use |
| --- | --- |
| Canonical spec | stable project requirement |
| Wiki page | navigation, summary, glossary, decision list |
| ADR | decision and rationale |
| Open question | unresolved item |
| Runbook | operational procedure |

## Naming

Use uppercase root documents:

```text
TECHNICAL_SPEC.md
DATA_GOVERNANCE.md
```

Use wiki pages for navigation:

```text
wiki/HOME.md
wiki/MAP.md
wiki/DECISIONS.md
```

## Update Rule

When a strategic decision changes:

1. update the canonical document;
2. update [DECISIONS.md](DECISIONS.md);
3. update [OPEN_QUESTIONS.md](OPEN_QUESTIONS.md), if the question is closed;
4. update [MAP.md](MAP.md), if a new page appears.

