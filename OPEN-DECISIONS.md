# Open decisions

For Arne, one at a time. Each item has a default that works fine as the answer. "Später" is
valid too. The answer goes on the item's `Answer:` line, in his words, with the date.

## 1. Regression guard for the notebooks' module code (open-items §1.1, part 1)
Why it matters: the shipped outputs don't prove the code still runs; part 2 (tip_tools copies
compile and match) is now in CI, part 1 (every attribute a notebook uses exists) is not.
PR #36 proposes it, but comes from an outside tracker bot (East Agile Tracker) that advertises
itself in the PR text, so it is not merged.
Default: write our own version on `develop`, close #36 with thanks.
Answer:

## 2. The four commercial decisions of the offering
Why it matters: offerings 4 and 5 can't be published without them; see
`9_misc/plan/offering-tip-presentation-and-workshop.md` §5 (pricing above 3 participants,
remote or on site, language, booking form for the free presentation).
Default: none — prices and terms are Arne's.
Answer:

## 3. The repository is public, the licence says "EPO Internal Use"
Why it matters: participants clone it without login, which needs public; the licence line reads
as if it should not be.
Default: stays public; reword the licence line in a later PR to what EPO agreed.
Answer:
