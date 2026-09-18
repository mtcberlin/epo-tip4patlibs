# IPScore HTML Tools — Build Log

Riccardo Priore's build log, imported with the module. Written in his
`/home/jovyan/Dennemeyer/` working folder, which also held a second, unrelated tool family
(**ASP Invention Assessment** — different source Excel). **Only the IPScore and NPV Target
Planner material came into this repo**; where the log below mentions the other family or the
old working folder, it is describing that original context, not this one.

Last updated by him: 2026-07-16 · scope notes and corrections added on import, marked
*(this repo)*.

---

## Bug fix — `avgRev` off-by-one vs. Excel (2026-07-16)

**Found by**: `build/verify_against_excel.py`, a new pipeline step that reads
`IPscore_3.01 WORKHORSE.xlsx` directly (`Financial results` / `Financial calculations`
sheets) and runs the real `calcVAN()`/`calcNPV()` against Excel's own 3 built-in test
patents and their Excel-computed NPVs — the first time the JS engine was checked against
the Excel source rather than against its own prior output.

**Bug**: `avgRev` (average revenue used to size the one-time Investments/InvestmentReduction
liquidity terms) summed exactly `depPeriod` years starting at `yFirst`. Excel's own window
(`Financial calculations` rows 98–121) is `year > T` and `year <= T+1+depPeriod`, which is
always `depPeriod+1` calendar-year slots — one more than the JS summed.

**Why invisible until now**: both hand-built demo patients (BioSense/MedTech NIR glucose
monitor, NovaMed) have a commercial-lifetime score short enough that the extra boundary
year always has zero revenue, making the missing term a no-op. Diverges only when
commercial lifetime is long relative to the depreciation period (verified with a synthetic
stress case: 997,054 correct vs. 1,000,251 with the bug — understates the true bug impact
that can be, since both terms scale with `avgRev`, larger for more extreme inputs).

**Fix**: replace the `yFirst..yFirst+depPeriod-1` loop with a direct sum over
`y in 1..10 where y>T and y<=T+1+depPeriod`, matching Excel exactly. Applied to the two
source-of-truth files `make_*_template.py` transplant engine JS from —
`IPscore_IT.html` (`calcVAN`) and `NPV_Target_Planner_EN.html` (`calcNPV`) — then
propagated to all 5 live files via `make_ipscore_template.py` / `make_npv_template.py` →
`render.py --promote`.

**Verified**: all 3 Excel test patents now match to 4+ decimal places (Patent 1:
329,059.4284; Patent 2: 4,361.2849; Patent 3: -4,686.3598), plus the NPV Planner's demo
scenario against an independent Python re-implementation of the same Excel formula chain.
`verify_against_excel.py` is now a permanent notebook cell (section 6b) — re-run after any
future change to either engine.

---

## Build Notebook (2026-07-15)

*(this repo: the file is now `build_html_tools.ipynb`; upstream it is
`Dennemeyer_HTML_Tools_Builder.ipynb`.)*

`build_html_tools.ipynb` regenerates the IPscore + NPV Target Planner
family (`IPscore_IT.html`, `IPscore_IT_Demo.html`, `IPscore_EN_Demo.html`,
`NPV_Target_Planner_EN.html`, `NPV_Target_Planner_IT.html`) from structured data in
`build/data/*.json` through shared Jinja2 templates in `build/templates/*.j2`, instead of
hand-editing the HTML directly.

**Not an Excel→HTML generator**: `IPscore_3.01 WORKHORSE.xlsx` only holds the deterministic skeleton
(question IDs, plain EPO English text, risk/opportunity flags, OEK values). The Italian
translations, € benchmark help text, demo narratives, and NPV Planner insights were
authored directly in the HTML in past sessions and don't exist in the Excel — so the
pipeline extracts that already-authored content out of the current HTML (via a Node VM
sandbox in `build/extract_*.js`, not manual retyping) into JSON, then re-assembles it
through a template. The HTML files remain the source of truth for content; the notebook
is the source of truth for assembly.

The notebook's own verification catches exactly the class of bug in "Bug 2" below
automatically (Node syntax check on every generated `<script>` block), plus a structural
data-equality check and a functional smoke test comparing computed IPscore/NPV values
between the live and regenerated files. ASP Invention Assessment is a separate tool
family (different source Excel) and is out of scope for this notebook.

> ⚠️ *(this repo, verified 2026-07-24)* **The smoke test is only meaningful for the NPV
> Planner family.** For all three IPscore files `build/smoke_test.js` returns
> `{"total":"0/200","pct":"0%","vanTotal":"0 €"}` for the live *and* the regenerated file —
> its DOM stub returns `checked:false` from `document.querySelector`, so `updateResults()`
> reads zeros no matter what `fillDemo()` or `onRadio()` did. "MATCH" there compares 0 with 0
> and cannot detect an engine regression. The NPV Planner test is real (€1,225,802). The
> binding guarantee for the IPscore engine is `verify_against_excel.py`, which does exercise
> `calcVAN()` for real. Fixing the stub (make the radio state readable back) would restore
> the intended check.

See the notebook itself for the extend-with-a-new-language / new-demo-scenario workflow.

---

## File Inventory *(this repo — corrected on import)*

| File | Size | Description |
|------|------|-------------|
| `IPscore_IT.html` | 70 KB | EPO IPscore 3.0 — interactive Italian tool, blank form |
| `IPscore_IT_Demo.html` | 72 KB | EPO IPscore 3.0 — pre-filled demo (MedTech Italia S.r.l.) |
| `IPscore_EN_Demo.html` | 70 KB | EPO IPscore 3.0 — pre-filled demo (BioSense Technologies Ltd.), **shown in the course notebook** |
| `NPV_Target_Planner_EN.html` | 55 KB | NPV Target Planner, English — **shown in the course notebook** |
| `NPV_Target_Planner_IT.html` | 58 KB | NPV Target Planner, Italian |
| `IPscore_3.01 WORKHORSE.xlsx` | 414 KB | Source Excel for IPscore (EPO) — VAN formulas + the 3 test patents `verify_against_excel.py` checks against |

There is **no blank English form**: `IPscore_IT.html` is the only blank variant. The pipeline
could render one (`render_ipscore("en", demo_flag=False)`) but no live file exists.

The four `ASP_Invention_Assessment_*.html` files and their source Excel, described in the
section below, belong to the **other tool family in Riccardo's working folder** and were
deliberately not imported. That section is kept for context only.

---

## ASP Invention Assessment — EN and IT blank forms

**Source**: `ASP_Invention Assessment Calculator_preliminary for Startup workshop.xlsx`

**Design system**: Dennemeyer×ASP branding — navy `#1a2744`, orange `#f97316`, green `#16a34a`.  
**Architecture**: single-file HTML + vanilla JS, no frameworks.

**Steps**:
1. Extracted all question text and 1–5 scoring criteria from the Excel.
2. Built single-page HTML with radio-button scoring per question.
3. Section scores and total score computed live in JS; result drives a color-coded badge.
4. IT version: full Italian translation of labels and question text.
5. Collapsible help panels per question via `toggleHelp(id)` pattern.

---

## ASP Invention Assessment — AutoComment (EN + IT demo versions)

**Method**: copy base file → apply additions.

**Additions**:
- `fillDemo()` function called at `DOMContentLoaded` — pre-fills all radios with a realistic fake startup patent case.
- `generateSummary()` function — auto-writes a narrative paragraph from section scores.
- Demo badge added to header (`DEMO PRECOMPILATO`).
- Summary displayed in a highlighted results card below the score.

---

## IPscore_IT.html

**Source**: `IPscore_3.01 WORKHORSE.xlsx` (EPO IPscore 3.01)  
**Attribution**: EPO tool — header reads "Strumento EPO · Adattamento ASP". **Not** a Dennemeyer product.

### Page structure (8 pages, SPA with CSS display:none/block)

| Page | Content |
|------|---------|
| 0 | Intro + patent info fields |
| 1–5 | Sections A–E (40 questions total) |
| 6 | Dati finanziari (7 inputs) |
| 7 | Risultati: IPscore, radar chart, risk/opp bars, VAN table, Prossimi Passi |

Step-dot progress bar built dynamically by `buildStepBar()`.  
All page content rendered by `buildPages()` at `DOMContentLoaded`.

### Questions

| Section | n | Max pts | Topic |
|---------|---|---------|-------|
| A | 8 | 40 | Legal / patent status |
| B | 9 | 45 | Technology |
| C | 9 | 45 | Market |
| D | 6 | 30 | Finance |
| E | 8 | 40 | Strategy |
| **Total** | **40** | **200** | |

### OEK questions — score 1–5 maps to numeric value used in VAN

| Question | Score→Value mapping |
|----------|---------------------|
| B5 | [5, 2, 1, 0.5, 0] — time-to-revenue T (years) |
| C2 | [0.005, 0.025, 0.05, 0.08, 0.15] — annual market growth g |
| C3 | [0.5, 1, 2, 4, 8] — commercial lifetime L (years) |
| C6 | [0.005, 0.02, 0.04, 0.06, 0.1] — patent market share et |
| D1 | [1, 0.75, 0.5, 0.25, 0] — substitution factor |
| D2 | [0.3, 0.15, 0.08, 0.025, 0.005] — R&D cost factor |
| D3 | [1.3, 1.15, 1.0, 0.85, 0.7] — cost efficiency factor |
| D4 | [1.2, 1.1, 1.0, 0.7, 0.5] — investment factor |

### VAN formula (verified against Excel)

*(this repo: the figures originally noted here — "Patent1 NPV≈22,473" — predate the `avgRev`
fix at the top of this log. The current, reproducible values are Patent 1 = 329,059.4284,
Patent 2 = 4,361.2849, Patent 3 = −4,686.3598; re-run `build/verify_against_excel.py` to
confirm.)*

```
Liquidity[y] = Revenue[y] - Costs[y] - Investments[y]
               + Regained[y] + Efficiency[y] + InvReduction[y]

VAN = Σ  Liquidity[y] × BT/100 / (1+r)^y    for y = 1..10
```

Critical invariant (derived by reading the Excel Financial Calculations sheet):
- **Investments and InvestmentReduction are ONE-TIME events at yFirst** (first year with Revenue > 0), not annual.
- Revenue and Regained/Efficiency use `FracYear(y)` for partial entry/exit years.

### Risk / Opportunity indicators

- Risk questions (RiskFactor=1): A1,A2,A3,A5,A6,A7,A8, B2,B3,B4,B5,B6,B7,B8, C1,C4,C9, D2,D3,D4,D5  
  → contribution per question: `-(5-score)/4`
- Opportunity questions (OppFactor=-1): A3,A4,A5, B1,B2,B9, C1,C2,C3,C4,C5,C6,C7,C8, D3  
  → contribution per question: `(score-1)/4`

### Radar chart

HTML5 Canvas pentagon — 5 axes clockwise from top:  
A=Legal, B=Technology, C=Market, D=Finance, E=Strategy  
Scores normalised to [0,1] against section maxima before plotting.

### Bugs fixed during build

**Bug 1 — colon typo**  
`interpColor:'#15803d'` (colon) → `interpColor='#15803d'` (assignment)

**Bug 2 — Italian apostrophe SyntaxError (critical)**  
Italian text `un'azione` inside a single-quoted JS string closed the string early → SyntaxError → entire `<script>` block silently killed → `#pages` div empty → page appeared frozen.  
Fix: `un\'azione` (escaped apostrophe).  
Diagnosis tool: `node -e "const fs=require('fs'); const h=fs.readFileSync('file.html','utf8'); const m=h.match(/<script>([\s\S]*?)<\/script>/); try{new Function(m[1]);console.log('OK');}catch(e){console.error(e.message);}"`

**Rule**: always run the Node.js parse check above after editing any Italian (or any natural-language) text inside JS single-quoted strings.

---

## IPscore_IT_Demo.html

**Method**: `cp IPscore_IT.html IPscore_IT_Demo.html` then four targeted edits:

1. `<title>` — added "DEMO"
2. Header badge — "TOOL INTERATTIVO" → "DEMO PRECOMPILATO" (amber `#f59e0b`)
3. Demo banner div — amber stripe between step-bar and pages, explains data is fictional
4. `fillDemo()` function + call in `DOMContentLoaded`

### fillDemo() logic

```javascript
function fillDemo(){
  // 1. Patent info text fields
  // 2. All 40 radio scores via onRadio(qid, val)
  // 3. All 7 financial inputs + updateNetResult()
  // 4. Mark all progress dots as done
  // 5. goToPage(7)  →  lands directly on Risultati
}
```

### Fake demo case — MedTech Italia S.r.l.

**Patent**: Monitoraggio continuo della glicemia non invasivo mediante spettroscopia NIR  
**Number**: EP4123456A1 / IT102021000012345  
**Sector**: Dispositivi Medici / Diagnostica in vitro  
**IPscore**: 140/200 (70%)

| Section | Scores | Total |
|---------|--------|-------|
| A | 4,4,4,3,3,3,2,3 | 26/40 |
| B | 5,4,3,3,2,4,3,4,5 | 33/45 |
| C | 5,4,4,3,4,4,4,3,2 | 33/45 |
| D | 4,3,3,3,3,3 | 19/30 |
| E | 4,4,5,3,2,2,5,4 | 29/40 |

| Financial input | Value |
|----------------|-------|
| Fatturato (BT) | 1,500,000 € |
| Costi diretti (DC) | 900,000 € |
| Costi indiretti (IC) | 225,000 € |
| Ammortamenti (DP) | 45,000 € |
| Periodo ammortamento | 7 anni |
| Quota settore (S%) | 40% |
| Tasso attualizzazione | 12% |
