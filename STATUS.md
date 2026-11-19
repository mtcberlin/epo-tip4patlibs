---
goal: Course material with which PATLIB staff use the EPO TIP platform for patent analytics, and the source for the bookable mtc.berlin TIP offering.
next: Open the release PR develop → main, so the README front page and the teaser become public.
waits:
  - who: Arne
    what: the four commercial decisions of the offering (OPEN-DECISIONS.md §2)
    since: 2026-09-17
  - who: Arne
    what: yes or no to our own regression guard for the notebooks' module code (OPEN-DECISIONS.md §1)
    since: 2026-09-20
  - who: Arne
    what: licence line "EPO Internal Use" on a public repository (OPEN-DECISIONS.md §3)
    since: 2026-11-04
lane: Patents
updated: 2026-11-19 15:10
by: epo-tip4patlibs.studio
---
The five modules are complete and were delivered in Warsaw on 16–17 September 2026.
`develop` is 10 commits ahead of `main` (last release 25 September): the agent setup with CI
invariants, the TIP Explorer teaser, and the new README with the online offer. None of it is
public until Arne merges a release PR; none is open right now.
PR #37 (CLAUDE.md, from 2 November) conflicts with `develop` and looks superseded by #38.
Only checkable on TIP: the two query-library notebooks and `2_national-coverage.ipynb`
(`9_misc/plan/open-items.md` §2).
