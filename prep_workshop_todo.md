# Workshop Preparation — open work

Working notes for the **PATLIB Warsaw 2026** workshop. Goal: five topics, seven modules,
one consistent course. Modules 6 and 7 are Riccardo Priore's contributions, reworked here;
his repository (`rickypriore/patlib-sessions`) stays the upstream source.

---

## Guiding decision: show the whole chain, not just the last step

Riccardo's own framing is that only the **final step** — the finished report — needs
explaining. **We disagree, deliberately.** For a PATLIB audience the interesting question is
*"how do I get to a report like this for my own topic?"*, and the answer lives in the steps he
treats as prerequisites: **the search strategy is the actual professional skill**, and it was
the one thing invisible in the imported material.

Hence module 6 is now a three-part chain, each part feeding the next:

| Notebook | Answers | Produces |
|---|---|---|
| `1_dataset_and_search_strategy.ipynb` | *How is the corpus defined?* Keywords **AND** classifications; ambiguous acronyms (MRSA/VRE/ESBL) deliberately excluded; one representative publication per family (EP > WO > US) | `Antibiotic_Resistance_Dataset.xlsx` (3,974 families) |
| `2_technology_network.ipynb` | *Which technology fields co-occur?* | `Technology_Legend.xlsx`, `IPC_Cooccurrence.xlsx`, `IPC_Rankings.xlsx` |
| `3_additional_analyses_and_report.ipynb` | Triadic families, filing authorities, cluster explorer, IPC evolution — **and** the report assembly (Step 7) | the assembled report + `output_*` artifacts |

**Done:** notebooks 1 and 2 imported from upstream, TIP absolute paths
(`/home/jovyan/training/Patlib Sessions/…`) rewritten to relative, branded headers added,
all three numbered. *(Remaining `/home/jovyan` strings sit only in stored `print()` outputs
and disappear on the next run.)*

---

## TODO

### 1. Templating / report assembly — rebuild or extend
**Status:** partly solved. Step 7 in notebook 3 already assembles a one-file report
(`Antibiotic_Resistance_Report.html`).

Riccardo's original closing cell states plainly:

> *"The final HTML assembly step — stitching these plus the original 13 analyses into
> `…_MODERNIZED.html` — is a separate templating script, not included here … Ask if you'd like
> that persisted as a notebook too."*

So a **separate templating script exists upstream and was never shipped**, and he explicitly
offered it.

- [ ] **Ask Riccardo for the templating script.** The only thing genuinely missing — the other
      two gaps turned out to be solvable from his repo.
- [ ] Decide: **extend our Step 7** into the full assembler, or adopt his script if he sends it.
      Prefer whichever keeps the assembly *in the notebook* rather than in an external script.
- [ ] Either way the result must be reproducible from notebooks 1–3, with no hidden step.

### 2. Simplify and clarify
- [ ] Review the three notebooks end to end for redundancy — they were written independently
      and repeat setup/query boilerplate.
- [ ] Make the numbering visible *inside* each notebook (which part, what it needs, what it
      hands on) so the chain is obvious when opened standalone.
- [ ] Consider whether the two legacy artifacts (`Antibiotic_Report_FINAL.html` 50 MB,
      `…_MODERNIZED.html` 2.4 MB) should stay once our own assembled report is complete.
      `Antibiotic_Report_FINAL.html` is still **required** — notebook 3 Step 4 reads the cluster
      assignments out of its embedded chart.

### 3. Display convention — results inside TIP, no downloads
The point of the rework: Riccardo's model writes standalone HTML you must download.
**Ours should show results in TIP.** Four tiers, in order of preference:

| Tier | For | Mechanism | Status |
|---|---|---|---|
| 1 | Plotly charts | `fig.show()` inline | ⬜ 4 charts in notebook 3 still write-only |
| 2 | Tables | `itables` inline instead of hand-built DataTables HTML | ⬜ blocked: is `itables` on TIP? |
| 3 | Finished HTML tools | serve via `jupyter-server-proxy` (`tip_tools`) | ✅ done in module 7 |
| 4 | Real apps | launcher pattern (PATSTAT Explorer) | ✅ established |

**Key constraint (verified on TIP):** an `IFrame` cannot work. JupyterLab resolves relative
`src` against the page URL, and Jupyter Server serves `/files/` with a **CSP sandbox that
disables JavaScript**. That is exactly why Riccardo links everything with `?download=1`.
The proxy route is the only way to get interactivity inside TIP.

- [ ] Verify `itables` availability on TIP → decides tier 2.
- [ ] Add `fig.show()` to the charts in notebook 3, re-run on TIP so outputs are stored.
- [ ] Once settled, write the convention into `CLAUDE.md` so all 7 modules stay consistent.

### 4. Optional — complete the picture
Two further upstream notebooks feed the *original* 13-analysis report but are not imported:
`Antibiotic_Resistance_tSNE_Analysis_NEW.ipynb` (the clustering) and
`Antibiotic_Resistance_SDG_Analysis.ipynb` (SDG mapping).

- [ ] Decide whether the t-SNE notebook should join the chain — notebook 3 currently reads the
      cluster assignments out of the published report instead of computing them, which is a
      deliberate correctness choice (the separate t-SNE run yields *different* clusters:
      3,840 vs 3,585 families). Importing it would need that discrepancy explained, not hidden.

### 5. Before the release
- [ ] Dry-run all five topics against the clock (~8 min each).
- [ ] Re-sync with upstream (`git fetch` in `rickypriore/patlib-sessions`) — he commits actively.
- [ ] Release `develop` → `main`, then send Riccardo the link to both reworked modules.

---

## Reference

- Full analysis of Riccardo's repository: `_docu/` on branch `herrkrueger` in
  `rickypriore/patlib-sessions` (local only — the remote branch was deleted).
- Attribution: IPScore is an **EPO tool**, ASP adaptation. Modules 6 & 7 credit
  *created by Riccardo Priore*.
- Guest-module conventions (pre-executed outputs, authorship in header): see `CLAUDE.md`.
