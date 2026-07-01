# Task — Regional Applicant Profiling via PATSTAT

You have access to a PATSTAT MCP (EPO PATSTAT Global on BigQuery): query tools with a `dry_run` option, schema/table inspection, and methodology guides (`get_guide`, e.g. `regional-analysis`). Use them as you see fit; design your own method and validate your own assumptions against the live data.

## Goal

For a given **country** (FR, IT, BE, DE, or PL) and a **region** within it, profile the **company patent applicants based in that region** over a recent multi-year window, along two dimensions:

1. **Portfolio depth** — how many patent families each company holds.
2. **Geographic reach** — which jurisdictions / economic zones those families cover.

Then segment the companies by depth × reach into lead-qualification tiers (from small, locally-filing firms up to those with large, globally-protected portfolios), so a PATLIB can tell which regional companies are worth approaching for IP services and training.

## Deliverable

A ranked applicant list with family counts and the reach profile per company, plus the segmentation. Reproducible queries.

## Expectations

Work family-based, not application-based. Be explicit about how you identify "based in the region" and verify it against the data before aggregating (the region's encoding is not always what you'd assume, and the data edition matters). Mind query cost. State the limitations of whatever method you choose — in particular, who your approach can and cannot see.
