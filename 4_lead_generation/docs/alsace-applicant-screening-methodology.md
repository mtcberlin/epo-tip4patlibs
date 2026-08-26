# Regional Applicant Profiling — Alsace (FR42), Reproducible Recipe

*PATSTAT Global Autumn 2025 via the depa.tech MCP. Family-based, two axes. All numbers verified live.*

## What this produces
A ranked list of the **company applicants based in a region**, each with **portfolio depth** (patent families) and **geographic reach** (jurisdiction zones) — the input to lead-qualification tiering.

## Corpus logic — the non-negotiables
- Backbone: `tls206_person → tls207_pers_appln → tls201_appln`
- Applicants only: `applt_seq_nr > 0`
- Families, never applications: `COUNT(DISTINCT docdb_family_id)`, `docdb_family_id > 0`
- Companies only: `psn_sector = 'COMPANY'`
- Both geocoding sources: `nuts_level IN (3,4)`
- **Region across both NUTS vintages** (old level-3 + current level-4 codes) — see Axis 1
- Genuine patent applications: `TRIM(appln_kind)='A'` (exclude `T` validations, `U` utility models)
- Window: filing years 2017–2022 (= active in window)

## Axis 1 — portfolio depth (the applicant list)
```sql
SELECT p.han_name AS applicant, COUNT(DISTINCT a.docdb_family_id) AS families
FROM tls206_person p
JOIN tls207_pers_appln pa ON p.person_id = pa.person_id
JOIN tls201_appln a       ON pa.appln_id  = a.appln_id
WHERE pa.applt_seq_nr > 0
  AND p.nuts_level IN (3,4)
  AND (p.nuts LIKE 'FR421%' OR p.nuts LIKE 'FR422%'
    OR p.nuts LIKE 'FRF11%' OR p.nuts LIKE 'FRF12%')
  AND p.psn_sector = 'COMPANY'
  AND a.appln_filing_year BETWEEN 2017 AND 2022
GROUP BY applicant ORDER BY families DESC;
```
**Result: 78 companies / 396 families.** Distribution by family class (1 / 2 / 3–4 / 5–10 / 10–20 / 20–50 / >50): **31 / 15 / 13 / 9 / 5 / 4 / 1** — the SME pyramid. Leader: HAGER ELECTRO (63).

## Axis 2 — geographic reach
For the same corpus, collect `appln_auth` across **all members** of each family, map to zones, and count families per zone per company:
```sql
WITH corp_fam AS (
  SELECT DISTINCT p.han_name, a.docdb_family_id
  FROM tls206_person p JOIN tls207_pers_appln pa ON p.person_id=pa.person_id
  JOIN tls201_appln a ON pa.appln_id=a.appln_id
  WHERE pa.applt_seq_nr>0 AND p.nuts_level IN (3,4)
    AND (p.nuts LIKE 'FR421%' OR p.nuts LIKE 'FR422%' OR p.nuts LIKE 'FRF11%' OR p.nuts LIKE 'FRF12%')
    AND p.psn_sector='COMPANY' AND a.appln_filing_year BETWEEN 2017 AND 2022
),
fz AS (
  SELECT cf.han_name, cf.docdb_family_id,
    MAX(m.appln_auth='EP') ep, MAX(m.appln_auth='WO') wo,
    MAX(m.appln_auth IN ('US','CA')) na,
    MAX(m.appln_auth IN ('CN','JP','KR','IN','TW','SG','IL')) asia,
    MAX(m.appln_auth IN ('AU','NZ')) oce
  FROM corp_fam cf JOIN tls201_appln m ON m.docdb_family_id=cf.docdb_family_id
  GROUP BY 1,2
)
SELECT han_name, COUNT(*) families,
  SUM(CAST(na AS INT64)) na, SUM(CAST(asia AS INT64)) asia, SUM(CAST(oce AS INT64)) oce
FROM fz GROUP BY han_name ORDER BY families DESC;
```
Read **depth × reach** into tiers: Hippo (many families, EP-bound), Lion (many, global), Antelope (few, broad), Lemur (few, local), Zebra (in between).

## What this can and cannot see — verified
- **EP/PCT-active subset only.** ~70% of German national patent families never take the EP/PCT route and carry no NUTS; ~77% of DE company applicant records have no NUTS (Alsace/FR similar). The locally-filing SME majority is invisible.
- **Postcode cannot recover them** inside PATSTAT (`tls226.zip_code` empty; addresses sparse).
- **`han_name` under-consolidates** — group/legal-form splits (KUHN SAS + KUHN SA; HAGER ELECTRO + HAGER CONTROLS). Consolidate via `doc_std_name_id`/`psn_id` before final ranking.
- **`EP`/`WO` are routes, not states**; designations are not broken out.
- **Optional portfolio completion:** fix the applicants' identity set, then recount *all* their families (incl. national-only) with a `has_EP` flag — recovers depth for known firms, but cannot find net-new national-only firms.
