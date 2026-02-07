# PATLIB Training Guide: IPC/CPC Search in PATSTAT on BigQuery

## Summary

Create a training guide for PATLIB staff (patent information professionals at universities and patent offices across Europe) that teaches how to search IPC and CPC classifications in PATSTAT on BigQuery effectively.

## Work Order

1. **Review** the attached specification: `patstat-ipc-cpc-training-guide.md`
2. **Upload** the IPC hierarchy SQLite database (`patent-classification-2025.db`, 79,833 entries, IPC version 2025.01) to BigQuery as `tls_ipc_hierarchy` — using the upload script and conversion functions provided in the MCP extension spec
3. **Validate** all SQL examples from the guide against the live BigQuery instance
4. **Publish** the guide in the agreed training channel (wiki / LMS / PDF)

## Scope

The guide covers:
- All 6 classification-related PATSTAT tables (`tls209`, `tls224`, `tls225`, `tls230`, `tls901`, `tls902`)
- Whitespace handling in IPC/CPC symbols (the critical gotcha)
- IPC vs CPC: when to use which, application-level vs family-level
- The IPC hierarchy extension (`tls_ipc_hierarchy`) with `title_full` for technology keyword search
- Technology search workflow: discover IPC codes by keyword → build PATSTAT query
- Common pitfalls and a quick-reference decision table

## Expected Result

- A reviewed, validated markdown document ready for distribution to PATLIB staff
- All SQL examples confirmed working against current PATSTAT BigQuery instance
- PATLIB staff can independently search IPC/CPC in PATSTAT, including technology keyword search via `title_full`
