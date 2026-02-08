# WIP: sync_schema_from_bigquery.py

**Status:** WIP - Ready for Implementation
**Created:** 2026-02-08
**Author:** Winston (Architect) + Arne

---

## Problem

The MCP server's schema metadata is spread across multiple redundant files:

| File | Size | Used by MCP? | Status |
|------|------|--------------|--------|
| `data/patstat_global_schema.json` | 172 KB | No | Dead weight, Sept 2025 export |
| `data/patstat-2026-01-19-context.json` | 44 KB | No | Dead weight, superseded by tables/ |
| `data/tables/*.json` (30 files) | 128 KB | **Yes** | Active, single source of truth |
| `data/samples/*.json` (30 files) | 172 KB | **Yes** | Active, lazy-loaded |

The `tables/*.json` files are the canonical format and already combine technical schema (types) with semantic descriptions. However, they were generated from the monolithic files and may be **out of date** vs. the live `patstat-mtc.patstat` BigQuery dataset (PATSTAT 2025 Autumn Edition).

There is no automated way to validate or update them.

---

## Goal

A Python script `mcp-server/scripts/sync_schema_from_bigquery.py` that:

1. Introspects the live BigQuery schema via `INFORMATION_SCHEMA`
2. Diffs against local `tables/*.json` files
3. Reports changes (new tables, new/removed columns, type mismatches)
4. Optionally updates the local files while **preserving hand-curated descriptions**
5. Optionally refreshes sample data in `samples/*.json`

---

## Location

```
mcp-server/
  scripts/
    sync_schema_from_bigquery.py    # new script
  data/
    tables/       # read + optionally updated
    samples/      # read + optionally updated
```

---

## Existing Infrastructure to Reuse

### BigQuery Connection

Already established in `context/test_queries_bq.py`:

```python
from google.cloud import bigquery
from google.oauth2 import service_account

project = os.getenv("BIGQUERY_PROJECT", "patstat-mtc")
dataset = os.getenv("BIGQUERY_DATASET", "patstat")
credentials_json = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")
```

- **Project:** `patstat-mtc`
- **Dataset:** `patstat`
- **Auth:** Service account `patstat-reader@patstat-mtc.iam.gserviceaccount.com`
- **Credentials:** `GOOGLE_APPLICATION_CREDENTIALS_JSON` env var (from `.env`)

### Target Format (tables/*.json)

Already defined and working. Example `tls201_appln.json`:

```json
{
  "table_name": "tls201_appln",
  "availability": ["bigquery", "tip"],
  "description": "Core table containing patent application records...",
  "columns": [
    {
      "name": "appln_id",
      "type": "INT64",
      "description": "Unique identifier for each patent application in the database."
    }
  ]
}
```

### Target Format (samples/*.json)

```json
{
  "table_name": "tls201_appln",
  "columns": ["appln_id", "appln_auth", ...],
  "rows": [ { "appln_id": "1505451", ... }, ... ],
  "row_count": 10
}
```

---

## CLI Interface

```bash
# Report only -- shows diffs, changes nothing
python scripts/sync_schema_from_bigquery.py --report

# Update schema files (preserves descriptions)
python scripts/sync_schema_from_bigquery.py --update-schema

# Full sync: schema + fresh sample data
python scripts/sync_schema_from_bigquery.py --update-schema --update-samples

# Dry run for update (shows what would change)
python scripts/sync_schema_from_bigquery.py --update-schema --dry-run
```

---

## Implementation Phases

### Phase 1: BigQuery Introspection

Two INFORMATION_SCHEMA queries:

```sql
-- All tables with row counts
SELECT table_name, row_count, size_bytes
FROM `patstat-mtc.patstat.INFORMATION_SCHEMA.TABLE_STORAGE`

-- All columns with types
SELECT table_name, column_name, data_type, is_nullable, ordinal_position
FROM `patstat-mtc.patstat.INFORMATION_SCHEMA.COLUMNS`
ORDER BY table_name, ordinal_position
```

### Phase 2: Load Local State

- Read all `data/tables/*.json` files
- Build lookup: `{ table_name: { columns: { col_name: {type, description} } } }`
- Identify custom tables (those with `availability` not including `"bigquery"`, or known custom tables like `tls_cpc_hierarchy`, `tls_ipc_hierarchy`)

### Phase 3: Diff

Per table, compare:

| Check | Report Label |
|-------|-------------|
| Table in BQ but no local file | `NEW TABLE` |
| Local file but not in BQ (and not custom) | `ORPHANED` |
| Local file but not in BQ (custom) | `CUSTOM (expected)` |
| Column in BQ but not in local | `NEW COLUMN` |
| Column in local but not in BQ | `REMOVED COLUMN` |
| Data type differs | `TYPE MISMATCH` |
| Row count changed significantly (>5%) | `INFO: row count changed` |

### Phase 4: Update Schema (--update-schema)

For each table with changes:

- **New columns:** Add with BigQuery type, set `description: ""` (to be curated later)
- **Removed columns:** Remove from JSON
- **Type changes:** Update type, keep description
- **Existing descriptions:** NEVER overwrite -- this is the valuable curated content
- **New tables:** Create new JSON file with empty descriptions, `availability: ["bigquery"]`
- Add/update `estimated_rows` field
- Add/update `last_synced` timestamp

### Phase 5: Update Samples (--update-samples)

For each table in BigQuery:

```sql
SELECT * FROM `patstat-mtc.patstat.{table_name}`
ORDER BY RAND()
LIMIT 10
```

Write to `samples/{table_name}.json` in existing format.

**Cost note:** Random sampling on large tables can be expensive. Consider using `TABLESAMPLE` for tables > 1M rows:

```sql
SELECT * FROM `patstat-mtc.patstat.{table_name}` TABLESAMPLE SYSTEM (0.001 PERCENT)
LIMIT 10
```

---

## Report Output Format

```
=== PATSTAT Schema Sync Report ===
Source: patstat-mtc.patstat
Date:   2026-02-08
Tables in BigQuery: 29
Tables in local:    30

  tls201_appln           27 cols  (match)
  tls202_appln_title      3 cols  (match)
  tls206_person          16 cols -> 17 cols  [+1 new: psn_sector_2]
  tls299_new_table       NEW in BigQuery (not in local)
  tls_cpc_hierarchy      CUSTOM (not in BigQuery, expected)
  tls_ipc_hierarchy      CUSTOM (not in BigQuery, expected)

Summary: 26 matching, 1 changed, 1 new, 2 custom
```

---

## Dependencies

Add to `mcp-server/pyproject.toml`:

```toml
[project.optional-dependencies]
sync = [
    "google-cloud-bigquery>=3.0",
    "google-auth>=2.0",
    "python-dotenv>=1.0",
]
```

Install: `pip install -e ".[sync]"`

The sync dependencies are optional -- they are NOT required for running the MCP server itself.

---

## Cleanup After First Successful Run

Once the script runs and `tables/` files are confirmed up-to-date:

1. **Delete** `data/patstat_global_schema.json` (172 KB, unused)
2. **Delete** `data/patstat-2026-01-19-context.json` (44 KB, unused)
3. Consider whether `context/bigquery-schema.md` can also be auto-generated from `tables/` files

---

## Edge Cases and Design Decisions

### Custom Tables (tls_cpc_hierarchy, tls_ipc_hierarchy)

These exist only in `tables/` and were uploaded to BigQuery separately. The script should:
- Recognize them via a config list or by checking `availability` field
- Skip them during diff (no "ORPHANED" warning)
- Still validate them against BQ if they DO exist there

### BigQuery Type Mapping

BigQuery INFORMATION_SCHEMA returns types like `INT64`, `STRING`, `DATE`, `FLOAT64`, `BOOL`, `TIMESTAMP`. The existing `tables/*.json` already use these BigQuery type names, so no mapping needed.

### nuts_zip Table

Present in the old `patstat-2026-01-19-context.json` as `public.nuts_zip` but NOT in the current `tables/` directory. The script should detect it if it exists in BigQuery and flag it as `NEW TABLE`.

### Preserving Column Order

When updating, maintain the column order from BigQuery's `ordinal_position`. New columns go at the end or in their correct ordinal position.

### availability Field

- Standard PATSTAT tables: `["bigquery", "tip"]`
- Custom tables (hierarchy): `["bigquery"]`
- New tables discovered from BQ: default to `["bigquery"]`, manually add `"tip"` later if applicable

---

## Open Questions

1. **Should the script also validate descriptions?** (e.g., flag columns with empty descriptions for review)
2. **Should we add a `--generate-descriptions` flag** that uses BigQuery column comments or an LLM to fill in empty descriptions?
3. **Row count display:** Should `estimated_rows` be added to the `tables/*.json` format? Useful for query planning but adds maintenance burden.
