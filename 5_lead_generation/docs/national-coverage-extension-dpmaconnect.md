# National Coverage Extension — DPMAconnect Plus (Design / Feasibility)

**Status: 📝 proposed / feasibility.** Not yet implemented. Closes the coverage gap named in
the notebook's Step 7 and in `philippe-vs-patstat-comparison.md`. Jira: PIP-127.

## The gap this fills
A NUTS filter returns only the **EP/PCT-active subset** of a region's applicants (NUTS is
assigned on the EP/PCT route only). Measured on PATSTAT Autumn 2025, ~70% of German national
patent families never take that route and carry **no NUTS**; ~77% of DE company applicant
records have no NUTS at all. Those national-only filers — typically the smaller, locally
filing SMEs a PATLIB most wants — are invisible to the PATSTAT-only method, and PATSTAT
cannot recover them by postcode (`tls226.zip_code` empty, addresses sparse).

**DPMA register data has the addresses (incl. PLZ) for _all_ German national filings**, so it
can recover exactly that tail — the same structural advantage Philippe's INPI ZIP/SIREN
method had over PATSTAT, but sourced from an official API.

## Source: DPMAconnect REST Web Services
Base: `https://dpmaconnect.dpma.de/dpmaws/rest-services/` · Basic auth (registered user).
Relevant service: **`DPMAregisterPatService`** (Patente/Gebrauchsmuster). Two routes to
applicant addresses:

### Route A — targeted (small result sets)
1. `search/<Expertenabfrage>` → hit list XML (`PatentHitList.xsd`); each hit carries a
   `leading-registered-number` (führendes Aktenzeichen). Expert-query syntax = DPMAregister
   "Expertenrecherche" (patents/utility models). The applicant/proprietor field is **`INH`**
   (Inhaber), e.g. `search/INH%3D<name>` — **not** `pa` (`pa=`/`PA=` are rejected with
   *"'pa' not admissible at position 1"*, HitCount 0). `IN` is a broader variant.
2. `getRegisterInfo/<Aktenzeichen>` → full register record as **ST.36 XML** (DPMA extension
   `DE-PATGBM-RegisterExt`), which contains applicant name **and address**.
- ⚠️ **Hit cap: 1000** per search (100 on a test account) — too small for a whole
  Bundesland/year. Use Route B for population-scale work.

### Route B — bulk (population scale) — **the route the notebook uses**
- `getRegisterabzuege/<yyyy-mm-dd>/<daily|weekly|monthly|yearly>` → ZIP with **one ST.36
  record per registration** (a weekly extract ≈ 6 000–7 000 records / ~12 MB). ✅ **Works
  with the workshop account.** This is the population entry point: pull a period, parse every
  record, map PLZ → NUTS, aggregate by region. Confirmed 2026-07-02 on the 2026-06-20 week
  (6 760 records → 1 953 DE applicants region-mapped).
- `getPublikationsdaten_XML/<yyyyWW>` → ⚠️ **permission denied** for the `mtc.berlin`
  account ("No permission of user=mtc.berlin for right=Publikationsdaten"). Needs a separate
  DPMAconnect right; not used.

Semantics note: `getRegisterabzuege` is the register-*change* stream (records with activity in
the period, incl. foreign applicants and EP validations), not only new filings — keep the DE
subset for regional leads.

## Proposed pipeline
1. **Fetch** (Route B): pull the relevant `getRegisterabzuege` / `getPublikationsdaten_XML`
   ZIPs for the target years. Auth via env vars (`DPMA_USER`/`DPMA_PASS`) — **never** in the
   repo. Runs where `dpmaconnect.dpma.de` egress is allowed (see Constraints).
2. **Parse ST.36 XML** → per application: applicant name, address (street, **postcode**,
   city, country), application/registration number, filing date, IPC, kind (A/patent,
   U/utility model).
3. **PLZ → region**: map the 5-digit German postcode to Kreis/Bundesland via a
   PLZ↔AGS/NUTS crosswalk (public data). Gives the region assignment PATSTAT lacks.
4. **Merge with PATSTAT**: link on the German application number
   (DPMA Aktenzeichen ↔ PATSTAT `appln_nr` for `appln_auth='DE'`) after number-format
   normalisation. Add a `has_EP` / `has_EP_PCT` flag per family (from PATSTAT) so each firm
   is tagged as EP/PCT-active vs national-only.
5. **Recompute the regional applicant list** from the union: the PATSTAT NUTS list (as today)
   **plus** the national-only firms recovered from DPMA. Feed the same depth × reach tiering;
   national-only firms will typically be small × local — precisely the lead tail the PATLIB
   was missing.

## Confirmed from sample records (2026-07-02)
Verified against a 1977 utility model and a 2024 patent (`DE-PATGBM-RegisterExt`, schema 0.10):
- **Address tags:** `bibliographic-data/parties/applicants/applicant/addressbook` →
  `<name>` (applicant), `<text>` (full "Name, PLZ Ort, Land" string), and
  `<address>` with **only** `<address-1>` + `<country>`. There is **no separate street /
  postcode / city tag** — even modern records merge **PLZ + city** into `<address-1>`
  (e.g. `66440 Blieskastel`), and street is not published at all. Extract PLZ as the leading
  5 digits of `<address-1>` (`^(\d{5})\s`); foreign applicants have no PLZ (`Obernai, FR`).
  `<inventors>` / `<agents>` / `<correspondence-address>` are separate party blocks — parse
  `<applicants>` only.
- **Other fields:** application number `application-reference/document-id/doc-number`
  (`102024206684.2`); filing date `.../date`; kind via publication `<kind>` (`A*`=patent,
  `U*`=utility model) or `office-specific-bib-data/type-of-ip-right`; IPC
  `classifications-ipcr/classification-ipcr/text` (`G01N0033530000`).

### Still open
- **Number formats** for the Aktenzeichen ↔ `appln_nr` join (normalisation rules, check digits).
- Coverage of the address field across record types (granted vs pending; company vs natural
  person).

### Sample-fetch recipe (run where DPMA is reachable)
```bash
export DPMA_USER='...'; export DPMA_PASS='...'   # do not commit; rotate if shared
curl -sS -u "$DPMA_USER:$DPMA_PASS" \
  "https://dpmaconnect.dpma.de/dpmaws/rest-services/DPMAregisterPatService/search/INH%3D<name>" \
  -o hitlist.xml
xmllint --format hitlist.xml | grep leading-registered-number | head
curl -sS -u "$DPMA_USER:$DPMA_PASS" \
  "https://dpmaconnect.dpma.de/dpmaws/rest-services/DPMAregisterPatService/getRegisterInfo/<AZ>" \
  -o registerinfo.xml
xmllint --format registerinfo.xml   # inspect the applicant/address block
```

## Constraints & caveats
- **Egress:** automated runs need `dpmaconnect.dpma.de` on the environment's network-egress
  allowlist. The default Claude-Code-on-web sandbox blocks it (403 at CONNECT); set an
  appropriate network policy when creating the environment, or run the fetch elsewhere.
- **Auth/secrets:** Basic auth; keep credentials in env vars / a secret store, never in the
  repo or notebook.
- **Volume/rate:** bulk ZIPs are large; `search` is capped at 1000 hits.
- **Data protection (GDPR):** company addresses are low-risk for B2B lead generation; addresses
  of **natural-person** applicants are personal data — handle/store/display accordingly.
- **Scope:** DE only. The analogous national route for FR is INPI; this design is DPMA-specific.

## Relation to the existing module
This is an **optional extension** to the PATSTAT-only workshop notebook, not a replacement.
The notebook stays TIP-only and self-contained; this pipeline would be a separate,
credentialed data-prep step whose output augments the regional applicant list with the
national-only tail. See `alsace-applicant-screening-methodology.md` (the "optional portfolio
completion" note) and `philippe-vs-patstat-comparison.md` (why national-office data wins on
population coverage).
