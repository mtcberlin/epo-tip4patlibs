# Provenance

Clean rebuild of the antibiotic-resistance landscape report for the TIP4PATLIBS course.

- **Analysis logic** derives from Riccardo Priore's antibiotic-resistance notebooks. The **primary
  reference** is the working module in `../1_antibiotic_resistance/` (its three notebooks run on TIP
  today — executable ground truth); Riccardo's originally delivered notebooks are the secondary
  reference for analyses the working module does not contain.
- **This code is authored fresh**, not imported or patched from either reference. The search
  strategy in notebook 1 is preserved so the corpus is identical; the authority (nb 2) and IPC
  co-occurrence (nb 3) analyses reproduce the reference faithfully so the numbers match.
- **Rebuilt by** Arne Krüger (mtc.berlin), integrating Riccardo's landscape-report topic into the
  course as one consistent four-step pipeline. Riccardo's own repository stays the canonical source
  of his originals.

Ships **pre-executed** after a TIP run (each notebook queries PATSTAT PROD; see `README.md`).
