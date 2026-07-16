# Hand-off brief — a DPMA register MCP server (working title `depatisnet-mcp`)

**For:** an agent building a new MCP server, modelled on the **MTC OPS MCP** (`ops_*` tools,
markdown/json dual output, hosted at `*.depa.tech/mcp`, Docker + Coolify).
**Goal:** expose the DPMA national register — the applicant addresses PATSTAT cannot geolocate —
as MCP tools, so an agent can do live, per-record lookups the way it already does with OPS.
**Source material:** [`../2_national-coverage.ipynb`](../2_national-coverage.ipynb) and the
[`../dpma/`](../dpma/) package (stdlib-only, ~400 lines, live-tested — vendor it, don't rewrite it).

---

## 0. Read this first — five decisions to take before coding

1. **The name is wrong and should change.** DEPATISnet is DPMA's *publication search* system. The
   notebook and `dpma/fetch.py` use **DPMAconnect Plus → `DPMAregisterPatService`** — the
   **register** (procedural/legal status + applicant addresses), a different service. A server
   named `depatisnet-mcp` that serves register data will mislead every future reader and every
   agent reading the tool descriptions. **Recommendation: `dpma-mcp`** (room for DEPATISnet-style
   publication routes later), tool prefix `dpma_`. Confirm with Arne before the repo is created —
   renaming a hosted MCP after connectors point at it is painful.
2. **Do not duplicate `de_applicant_nuts`.** A sibling brief
   ([`patstat-mcp-de-nuts-extension-brief.md`](patstat-mcp-de-nuts-extension-brief.md)) specifies a
   BigQuery table that batch-resolves ~6,400 national-only applicants once. That is the
   **population-scale, cached** answer; this MCP is the **interactive, live, single-record**
   answer. They are complements, and the clean design makes that explicit: **this server should
   read the cached table first and only call DPMA on a miss.** Decide up front whether v1 does that
   or is live-only (live-only is a fine v1 — but design the lookup behind one function so the cache
   can slot in).
3. **Shared credentials + terms of use.** The server would hold **one** DPMAconnect account
   (`mtc.berlin`) and re-serve its data to every connector user. OPS has an explicit developer
   quota model; DPMAconnect's ToS on redistribution via a third-party service is **unverified**.
   Check `docs/2026.06_SchnittstellenbeschreibungDPMAconnectPlus.pdf` and the DPMAconnect terms
   before exposing this beyond an internal instance. Flag to Arne — this is a go/no-go for public
   hosting, not an implementation detail.
4. **GDPR is sharper here than in the notebook.** The notebook filters to
   `psn_sector='COMPANY'` *in PATSTAT*. The DPMA register has **no sector flag** — a raw
   `dpma_search` will happily return natural-person applicants' home addresses, and an MCP hands
   them straight to an LLM. Decide the default: recommend a `legal_form` heuristic (GmbH/AG/KG/
   e.V./SE/…) with natural-person addresses **suppressed by default** and an explicit opt-in
   parameter, documented in the tool description. The parser already reads `applicants` only (never
   inventors/agents) — keep that.
5. **Leave the bulk route out of v1.** `getRegisterabzuege` returns a ~12 MB ZIP / 6,000–7,000
   records per week. That is not an MCP tool response; it belongs to the batch table builder.
   `iter_registrations_from_zip` still ships in `dpma/` for that job.

## 1. Why this server is worth building

PATSTAT assigns NUTS **on the EP/PCT route only**. ~70 % of German national families never take
that route, so a NUTS region filter silently misses them — typically the smaller, locally-filing
SMEs a PATLIB most wants. The DPMA register has the PLZ for **every** DE filing. Measured for 2023:
~2,600 German company applicants, ~2,100 already geolocated in PATSTAT, **~500 national-only** —
recoverable only this way. The OPS MCP answers "what is this family / its legal status"; this one
answers **"where is this German applicant, and who is filing in my region"**.

## 2. Proposed tool surface (mirroring `ops_*`)

| tool | maps to | notes |
|---|---|---|
| `dpma_capabilities` | `ops_capabilities` | overview + expert-query cheat sheet + limits. Same shape as the OPS one. |
| `dpma_search` | `ops_search` | expert query (`INH=Hager`, `AKZ=102019213199`). **Hit cap 1000** (100 on a test account) — say so in the description so the agent doesn't try to sweep a Bundesland. Wraps `DpmaClient.search`. |
| `dpma_register` | `ops_family` / `ops_legal` | full ST.36 register record by Aktenzeichen → structured. Wraps `get_register_info` + `parse_register_xml`. |
| `dpma_applicant_region` | *(no OPS analogue — the value-add)* | application number → applicant name + PLZ → **NUTS3 + Bundesland**. One call, the notebook's Step 3+4 collapsed. This is the tool the whole thing exists for. |
| `dpma_plz_region` | — | pure local crosswalk lookup, no HTTP, no quota. Cheap and always available. |

Every tool takes `response_format: "markdown" | "json"` (default `markdown`), like OPS.

**Number handling — copy the OPS ergonomic.** `ops_family` accepts `EP1000000`, `EP1000000A1`,
`EP.1000000.A1` and normalises internally. Do the same: accept the PATSTAT `appln_nr`
(12-digit base, e.g. `102019213199`), the full Aktenzeichen with check digit
(`1020192131999`), and the dotted register form (`102024206684.2`). This matters because
**`getRegisterInfo/<12-digit>` fails** ("invalid input value") while **`search/AKZ=<12-digit>`
works** — the server must hide that trap, not surface it. Optionally compute the mod-11 check digit
locally to skip a call; verify against `102019213199`→`9` and `102024206684`→`2`.

## 3. Resources (mirroring the OPS `resource://` set)

OPS ships six markdown resources (`cql_reference`, `number_formats`, `ops_best_practices`, …).
Ship the equivalents — they are what stop an agent guessing:

- `resource://expert_query_reference` — DPMAregister Expertenrecherche grammar. **Must state that
  the applicant field is `INH` (Inhaber), not `pa`/`PA`** — `pa=` is rejected by the grammar
  (`HitCount=0`, *"'pa' not admissible at position 1"*), and every agent will try `pa=` first
  because that is the OPS field code.
- `resource://number_formats` — Aktenzeichen anatomy (`prefix(2)+year(4)+serial(6)`; `10`=patent,
  `20`=Gebrauchsmuster, `11`=national EP phase), check digit, and the **PATSTAT `appln_nr` bridge**.
- `resource://nuts_regions` — NUTS1→Bundesland table, NUTS3 semantics, crosswalk vintage
  (Eurostat GISCO NUTS 2024) and the vintage-mismatch caveat vs PATSTAT's NUTS.
- `resource://dpma_best_practices` — hit cap, per-account permissions, throttling, egress.
- `resource://coverage_and_scope` — the national-only gap, what the register does and does **not**
  contain (no street; PLZ+city merged in `address-1`), DE-only, GDPR.

## 4. What to vendor from `dpma/`

| file | role in the server |
|---|---|
| `fetch.py` | `DpmaClient` — Basic auth from `DPMA_USER`/`DPMA_PASS`, `search`, `search_aktenzeichen`, `get_register_info`. Backs `dpma_search` / `dpma_register`. |
| `register_parser.py` | ST.36 → `Registration`/`Applicant`; `parse_hit_applicant` reads name/PLZ/city straight from a **hit** (no second call). |
| `plz_nuts.py` | `map_plz`, `BUNDESLAND_BY_NUTS1`. Backs `dpma_plz_region` and the mapping half of `dpma_applicant_region`. |
| `data/pc2025_DE_NUTS-2024_v1.0.csv` | the crosswalk. **CC-BY-SA-4.0 (© EuroGeographics/Eurostat) — attribution is required**, in the repo *and* in served output. Copy the licence note with the file. |
| `samples/` | 2 single records + a 27-record mini-extract → **offline tests, no credentials needed**. Company applicants only; inventor data already removed. |

Known gaps to carry forward: applicant-name harmonisation is unsolved; a few lookups won't resolve
(city-only hits, ownership changes, foreign co-applicants) — return a NULL region, never a guess.
Resolution rate observed **≈ 96 %**.

## 5. Non-obvious operational facts (learned the hard way — don't re-discover)

- **Egress:** automated runs need `dpmaconnect.dpma.de` on the network allowlist. The default
  Claude-Code-on-web sandbox **blocks it** (403 at CONNECT). Set the network policy when creating
  the environment, or the server's own tests will fail for the wrong reason.
- **Permissions are per-route:** `getPublikationsdaten_XML` is **permission-denied** for the
  `mtc.berlin` account ("No permission of user=mtc.berlin for right=Publikationsdaten"). Don't
  build a tool on it without checking the account's rights first.
- **`search` answers HTTP 200 on a rejected query** (`HitCount=0` + a `Message_EN` attribute).
  `DpmaClient.search` already raises `ValueError` on that — surface it as a real MCP error, not as
  "no results", or the agent will conclude the applicant doesn't exist.
- **Register records are near-static** → cache aggressively (the address is a *company* attribute,
  reusable across all its filings and years). The PLZ crosswalk is local and free.
- **DE only.** The FR analogue is INPI, a different server.

## 6. Verification

- **Offline:** parse both `samples/*.xml` and the mini-extract ZIP; assert the known applicants,
  PLZ→NUTS3 mappings, and the `format_ipc` output. No credentials, runs in CI.
- **Live smoke (needs credentials + egress):** `INH=Hager` search (≈981 hits), a query-rejection
  path (`pa=Hager` → `ValueError`), one `search_aktenzeichen` round-trip.
- **End-to-end:** `dpma_applicant_region("102024206684")` returns an applicant with a Bayern NUTS3.
  Cross-check the sibling brief's spot-checks: FEV Group GmbH → `DEA2D` (Aachen, NRW),
  Wundermix GmbH → `DE21H` (München, Bayern).
- **Rate limit:** the DPMA quota is undocumented in our notes and the full 200-lookup pass was
  deliberately *not* re-run during notebook verification to avoid hitting it. Throttle
  conservatively and measure before any batch behaviour.

## 7. Deploy

Follow the `mtc-patstat-mcp` pattern: Docker image with `data/` baked in (`COPY data/ data/`) →
Coolify. Context/resources are cached at startup → **restart to pick up new files**. Credentials via
environment (`DPMA_USER`/`DPMA_PASS`), never committed. Suggested host: `dpma.depa.tech/mcp`.
