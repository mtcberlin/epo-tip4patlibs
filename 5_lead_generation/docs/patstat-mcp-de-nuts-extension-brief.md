# Hand-off brief — DE national-only applicant → NUTS mapping table for the PATSTAT-MCP

**For:** an agent working in the `mtc-patstat-mcp` repo (`~/Development/mtcberlin/mtc-patstat-mcp`).
**Goal:** persist, as a BigQuery table joinable through the PATSTAT-MCP, the region (NUTS/Bundesland)
of the **national-only German company applicants** that PATSTAT cannot geolocate — so any query can
recover the region PATSTAT leaves empty.

This brief is self-contained: everything you need (the mapping, the numbers, the schema, the build
steps) is below.

---

## 1. Background — the problem this solves

PATSTAT assigns NUTS **only on the EP/PCT route**. German applications filed *only* nationally
(`appln_auth='DE'`) carry no NUTS, so a NUTS region filter silently misses them — typically the
smaller, locally-filing companies a PATLIB most wants. PATSTAT *does* contain these applications and
their applicant identities; it just lacks their region. The DPMA register has the address (incl. PLZ)
for every DE filing. This table resolves that address **once per applicant** and stores the region.

## 2. The mapping (validated 2026-07-02)

**PATSTAT `tls201_appln.appln_nr` for DE = the 12-digit DPMA Aktenzeichen base, without check digit:**
`prefix(2) + filing_year(4) + serial(6)`, prefix `10`=patent, `20`=Gebrauchsmuster, `11`=national EP
phase. Example: `102019213199`.

Resolution path (one DPMA call per applicant):
- `getRegisterInfo/<12-digit>` **fails** ("invalid input value").
- **`search/AKZ=<appln_nr>` works** with the raw PATSTAT number → `HitCount=1`. The hit's
  `<applicant>` text is `"Name, PLZ Ort, DE"` — parse the PLZ directly. It also returns
  `leading-registered-number` = base + computed check digit (e.g. `1020192131999`), usable for an
  optional `getRegisterInfo`.
- Optional optimisation to skip the search call: compute the DPMA **mod-11 check digit** locally and
  hit `getRegisterInfo` directly. Verify any implementation against these known pairs:
  `102019213199`→check `9`; `102024206684`→check `2`.

Then map the 5-digit PLZ → NUTS3 via the Eurostat GISCO crosswalk (see §5), and NUTS1/Bundesland =
first 3 chars of the NUTS3 code.

## 3. Scope & numbers (measured on `patstat-mtc.patstat`)

Build set = **German company applicants** (`psn_sector='COMPANY'`, `person_ctry_code='DE'`), patents +
utility models (`TRIM(appln_kind) IN ('A','U')`), that have **no** German NUTS on any of their person
records. Filing years **2017–2024**:

| | applicants |
|---|---|
| German company applicants (A+U, 2017–2024) | 14,815 |
| already NUTS-geolocated in PATSTAT (via EP/PCT) | 8,373 |
| **national-only → build set (DPMA lookups)** | **6,442** |

(Do **not** drop `person_ctry_code='DE'`: without it the "national-only" set fills with foreign
multinationals like GM/Toyota/Nvidia that file DE-national — they have no German PLZ and are not
regional leads.) ~6,400 lookups ≈ a 30–40 min one-time batch, cacheable and reusable for every region.
Resolution success rate observed ≈ 96 % (the rest: city-only hits, ownership changes, foreign
co-applicants → leave region NULL).

## 4. Target table

Name (proposed, adjustable): **`patstat-mtc.patstat.de_applicant_nuts`** — same dataset as the `tls*`
tables so the MCP's `default_dataset` lets queries join it unqualified. `availability: ["bigquery"]`.

| column | type | description |
|---|---|---|
| `psn_id` | INT64 | PATSTAT harmonised applicant id (join key to `tls206_person.psn_id`) |
| `han_id` | INT64 | OECD HAN applicant id (secondary join key) |
| `psn_name` | STRING | applicant name (from PATSTAT) |
| `plz` | STRING | 5-digit German postcode (from DPMA register) |
| `nuts3` | STRING | NUTS3 (Kreis) code |
| `nuts1` | STRING | NUTS1 (Bundesland) code |
| `bundesland` | STRING | Bundesland name |
| `country` | STRING | resolved country (always `DE` for stored rows) |
| `source` | STRING | provenance, `'DPMA'` |
| `resolved_appln_nr` | STRING | the `appln_nr` used for the DPMA lookup |
| `n_appln` | INT64 | filing count in the build window (depth) |
| `first_filing_year` | INT64 | earliest filing year in window |
| `last_filing_year` | INT64 | latest filing year in window |
| `resolved_date` | DATE | when the address was resolved |

Store only rows that resolved to a German region (drop NULL-NUTS). Key = `psn_id`.

## 5. Build script

Model it on the existing custom-table loaders **`context/cpc/upload_cpc_hierarchy.py`** /
`context/ipc/upload_ipc_hierarchy.py` (define a `bigquery.SchemaField` list, `load_table_from_json`
with `write_disposition="WRITE_TRUNCATE"`, plus validation queries). Steps:

1. **PATSTAT query** (BigQuery, `patstat-mtc.patstat`) — one row per national-only German company
   `psn_id` with a representative `appln_nr`, `n_appln`, `first/last_filing_year`, `han_id`, `psn_name`.
   Reuse the CTE structure from
   `epo-tip4patlibs/5_lead_generation/regional_leads_full_coverage_bq.ipynb` (Step 1), widened to
   `appln_filing_year BETWEEN 2017 AND 2024` and keeping only `has_nuts=0`.
2. **Resolve** each `appln_nr` via DPMA `search/AKZ=` → PLZ. Reference implementation to vendor
   (stdlib, ~150 lines): `epo-tip4patlibs/5_lead_generation/dpma/fetch.py`
   (`DpmaClient.search_aktenzeichen`), `register_parser.py` (`parse_hit_applicant`), `plz_nuts.py`
   (`map_plz`, `BUNDESLAND_BY_NUTS1`). Credentials from `DPMA_USER`/`DPMA_PASS` env (never commit).
3. **PLZ → NUTS3** via the bundled Eurostat crosswalk
   `epo-tip4patlibs/5_lead_generation/dpma/data/pc2025_DE_NUTS-2024_v1.0.csv` (NUTS 2024, CC-BY-SA-4.0)
   — copy it into the mcp repo alongside the loader.
4. **Local resume cache** — persist each `(appln_nr → plz)` resolution to a JSON/CSV so a re-run skips
   done work (6k+ HTTP calls; expect retries/timeouts).
5. **Load** the assembled rows to `de_applicant_nuts` (WRITE_TRUNCATE). Print row count + a few sample
   regions for a sanity check.

Suggested location in the mcp repo: `context/de_nuts/build_de_applicant_nuts.py` (+ the crosswalk CSV).

## 6. Register the table in the MCP (no server code change)

The `ContextStore` (`src/patstat_mcp/context.py`) globs `data/tables/*.json` and `data/samples/*.json`
at startup and caches them. Add:

- **`data/tables/de_applicant_nuts.json`** — hand-written schema (the §4 columns with descriptions),
  `"availability": ["bigquery"]`, plus `"common_joins": ["JOIN tls206_person p ON p.psn_id = d.psn_id"]`
  and a short `"description"` explaining it maps national-only DE applicants to their region. Follow the
  format of `data/tables/tls_ipc_hierarchy.json`.
- **`data/samples/de_applicant_nuts.json`** — 10 example rows (format of `data/samples/tls904_nuts.json`).
  Either hand-write or generate both with `scripts/sync_schema_from_bigquery.py --update-schema
  --update-samples` after the table exists in BQ (it preserves hand-written descriptions).

## 7. Add a methodology guide

Add **`data/guides/national-only-regional-leads.md`** (first `# ` line = title, next line = one-sentence
description — that's how `context.py:_parse_guide_meta` derives metadata). Content: how to get the
**full** regional applicant list = PATSTAT NUTS ∪ this table, with example JOIN SQL, e.g.

```sql
-- Region = a Bundesland (NUTS1 prefix). Union of EP/PCT-geolocated + national-only.
SELECT p.psn_id, p.psn_name,
       COALESCE(d.nuts1, SUBSTR(p.nuts,1,3)) AS nuts1,
       (d.psn_id IS NOT NULL) AS national_only
FROM tls206_person p
LEFT JOIN de_applicant_nuts d ON d.psn_id = p.psn_id
WHERE COALESCE(d.nuts1, SUBSTR(p.nuts,1,3)) = 'DE2'   -- Bayern
```

## 8. Deploy & refresh

- Commit the loader, `data/tables/*.json`, `data/samples/*.json`, and the guide to `mtc-patstat-mcp`
  `develop`. The running server caches context on first call → **restart** to pick up new files.
- The hosted instance (`https://patstat.depa.tech/mcp`) **bakes `data/` into the Docker image**
  (`Dockerfile: COPY data/ data/`) → rebuild + redeploy (Coolify) to make the table discoverable there.
- **TIP backend: out of scope for now** (BigQuery-only). Adding TIP support would require adding the
  table name to `REFERENCE_TABLES` in **both** `tip_client.py` and `sync_reference.py`, regenerating
  `reference.db.gz` (`python -m patstat_mcp.sync_reference`), and is subject to TIP's restriction that a
  query may not mix reference and TIP tables (so a JOIN against `tls206_person` would be rejected on TIP).
- **Refresh cadence:** the table is a point-in-time snapshot. Re-run quarterly (or after each PATSTAT
  edition), resolving only new national-only `psn_id`s incrementally via the cache.

## 9. Verification (for you, the receiving agent)

- Dry-run the PATSTAT build query under the MCP's cost guard (cap 1 EUR; the counting queries here ran
  ~6 GB / ~0.04 EUR each).
- After load: `SELECT COUNT(*) FROM de_applicant_nuts` ≈ the resolved national-only set (~6k, ≤ 6,442).
- After restart: `get_table_schema de_applicant_nuts` returns the schema; `get_table_samples` returns rows.
- A join query (`tls206_person` × `de_applicant_nuts`) returns Bundesländer for applicants that have no
  `nuts` of their own — spot-check e.g. FEV Group GmbH → `DEA2D` (Aachen, NRW), Wundermix GmbH →
  `DE21H` (München, Bayern).
