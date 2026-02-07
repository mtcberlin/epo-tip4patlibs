# Engineering Backlog

This backlog collects cross-cutting or future action items that emerge from reviews and planning.

Routing guidance:

- Use this file for non-urgent optimizations, refactors, or follow-ups that span multiple stories/epics.
- Must-fix items to ship a story belong in that story's `Tasks / Subtasks`.
- Same-epic improvements may also be captured under the epic Tech Spec `Post-Review Follow-ups` section.

| Date | Story | Epic | Type | Severity | Owner | Status | Notes |
| ---- | ----- | ---- | ---- | -------- | ----- | ------ | ----- |
| 2026-01-12 | 3.2 | 3 | TechDebt | Low | TBD | Open | Fix SQLAlchemy SAWarning in `get_trend_data()` SME filter at `tip4patlibs_core.py:473`. Warning: "Coercing Subquery object into a select() for use in IN(); please pass a select() construct explicitly". Wrap subquery with `.select()` to use modern SQLAlchemy pattern. |
