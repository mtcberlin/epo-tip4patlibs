# Product Brief: TIP for PATLIBs

**Date:** 2026-01-10
**Author:** BMad
**Context:** Enterprise/Institutional (EPO initiative for PATLIB network)

---

## Executive Summary

**TIP for PATLIBs** is a ready-to-use Python analysis environment for the EPO's Technology Intelligence Platform (TIP), designed specifically for PATLIB centres. The solution enables patent information professionals to perform sophisticated regional, sectoral, and comparative patent analysis without programming skills.

Despite extensive PATSTAT, Python, and Jupyter training materials, PATLIB staff lack basic developer experience and time to learn. This project delivers a **product, not more education** - pre-built Jupyter notebooks with transparent Python scripts and no-code UI controls that demonstrate TIP's capabilities while being immediately useful.

The solution will be demonstrated at the PATLIB Conference in May 2026 and forms the basis for a pilot scheme targeting adoption across the European PATLIB network.

**Budget:** 10,000 EUR (Round 1)
**Prototype Deadline:** Mid-February 2026 (4 weeks)
**Conference Demo:** May 2026

---

## Core Vision

### Problem Statement

PATLIB centres are staffed by patent information professionals who need to analyse patent and innovation data for their advisory work. However:

1. **Skills Gap:** Despite extensive training materials, PATLIB staff lack basic developer experience to use TIP effectively
2. **Time Constraints:** Entry-level TIP users have limited time to invest in learning Python
3. **Analysis Limitations:** They need regional and sectoral comparisons they cannot easily perform today
4. **Tool Competition:** TIP's Jupyter output is "limited and unimpressive" compared to commercial tools like lens.org

The result: TIP adoption among PATLIBs remains low despite its powerful PATSTAT backend.

### Problem Impact

- EPO's investment in TIP is underutilized by a key target audience
- PATLIBs cannot deliver data-driven insights to their customers (SME inventors, tech transfer agencies)
- Training efforts have failed to bridge the skills gap
- Questionnaire feedback confirms: training isn't the solution

### Why Existing Solutions Fall Short

| Current State | Why It Fails |
|---------------|--------------|
| Raw TIP/Jupyter | Requires Python knowledge |
| PATSTAT training | PATLIBs lack time and developer mindset |
| Documentation | Reading docs ≠ being productive |
| Commercial tools | Not integrated with TIP, not free |

### Proposed Solution

A Jupyter notebook application with:

1. **Transparent script loading** - "Execute this cell first!" initializes all dependencies
2. **No-code UI layer** - Dropdowns, input fields, and buttons for all user interactions
3. **Plotly visualizations** - Interactive charts rendered in Jupyter cells
4. **Pre-built analysis workflows** - Regional, sectoral, and temporal patent analysis ready to use

```
┌─────────────────────────────────────────────────────┐
│  Jupyter Notebook (TIP Environment)                 │
├─────────────────────────────────────────────────────┤
│  Cell 1: "Execute this cell first!" (loads scripts) │
│  Cell 2+: No-code UI                                │
│    → Dropdowns (country, region, sector)            │
│    → Input fields (date range, keywords)            │
│    → Buttons ("Run Analysis", "Export")             │
│    → Plotly visualizations (interactive charts)     │
└─────────────────────────────────────────────────────┘
```

**Future enhancement (out of scope for Round 1):** Streamlit or D3-based companion site for richer visualization outside TIP's rendering limitations.

### Key Differentiators

- **Transparency:** Code is visible (learning by seeing), but interaction is no-code
- **Immediate value:** Useful from first use, no learning curve
- **TIP-native:** Built for the platform PATLIBs already have access to
- **Free:** No licensing costs, shareable across the network
- **PATSTAT expertise:** Handles the complexity of PATSTAT queries under the hood

---

## Target Users

### Primary Users

**PATLIB Staff (Entry-Level TIP Users)**

- Patent information professionals at PATLIB centres across Europe
- Limited or no Python/programming experience
- Limited time to invest in learning new tools
- Need to deliver patent analysis for advisory work
- Value: Quick insights for marketing their services and serving customers

**Characteristics:**
- Understand patent data conceptually (IPC, applicants, jurisdictions)
- Comfortable with web interfaces and basic data tools
- Frustrated by the gap between TIP's potential and their ability to use it

### Secondary Users (Downstream)

PATLIBs will share this free tool with their networks:

| User Type | Use Case |
|-----------|----------|
| Chambers of Commerce | Innovation/entrepreneurship consulting |
| Tech Transfer Agencies | University-industry collaboration analysis |
| SME Inventors | Understanding their competitive landscape |

### Key Stakeholder

**Rainer Kaysen (EPO)** - Project sponsor, success gatekeeper. His satisfaction determines project success and future contracts.

---

## Success Metrics

### Quantitative (Pilot Phase)

| Metric | Target |
|--------|--------|
| PATLIBs actively using the tool | 5+ centres in pilot |
| LinkedIn posts sharing analyses | Evidence of organic adoption |
| German PATLIB adoption | Traction among the 16 German PATLIBs |

### Qualitative

| Stakeholder | Success Indicator |
|-------------|-------------------|
| Rainer Kaysen (EPO) | "Happy and loves it" - wants to continue/expand |
| PATLIB Conference audience | Enthusiastic reception at May demo |
| German PATLIBs | Find it useful for marketing and customer work |
| TU Chemnitz PATLIB | Positive feedback (strategic relationship) |

### Business Objectives

- Increase TIP adoption across PATLIB network
- Demonstrate TIP value to justify continued EPO investment
- Create foundation for expanded tooling (Round 2+)
- Position contractor (BMad) as trusted TIP solutions partner

---

## MVP Scope

### Core Features (Round 1 - 10k EUR)

1. **Setup Cell**
   - "Execute this cell first!" initialization
   - Loads all dependencies
   - Handles library installation/updates
   - Environment compatibility checks

2. **Country Selector**
   - Dropdown for all TIP-supported countries
   - Foundation for all analyses

3. **Region Selector**
   - NUTS regions / federal states
   - Cascading from country selection
   - Optional (can analyze at country level only)

4. **Technology Sector Selector**
   - 35 predefined PATSTAT sectors
   - IPC concordance validation
   - Clear sector descriptions

5. **Date Range Selector**
   - Input fields for start/end year
   - Support for 5/10/15 year trend analysis

6. **Core Visualizations (Plotly)**
   - Patent application trends over time
   - Top N applicants ranking
   - Geographic distribution (regional analysis)
   - Technology sector breakdown

7. **Export Capability**
   - Download results as CSV
   - Export charts as PNG

### Example Query (The "Killer Demo")

> "Show me all medtech patents and the top 10 applicants in Wales"

This translates to:
- Country: United Kingdom
- Region: Wales
- Sector: Medical Technology
- Output: Top 10 applicants + trend visualization

### Nice-to-Have (If Time/Budget Allows)

- European universities innovation network analysis
- External data correlation (EUROSTAT, World Bank, OECD)
- Streamlit companion site prototype

### Explicitly Out of Scope (Round 2)

- Power user code editing features
- Custom query builder interface
- Advanced analytics/correlations
- Multi-language UI
- User authentication/personalization

**Note:** Code is transparent by nature (Jupyter). Power users CAN read/modify code anytime - we're just not designing for that use case in Round 1.

---

## Technical Preferences

### Platform

- **Environment:** EPO Technology Intelligence Platform (TIP)
- **Interface:** Jupyter Notebook (JupyterLab)
- **Backend:** PATSTAT via EPO patstat Python library + SQLAlchemy ORM

### Technology Stack

| Component | Technology |
|-----------|------------|
| Data Access | EPO patstat library, SQLAlchemy |
| Data Processing | Pandas |
| Visualizations | Plotly |
| UI Widgets | ipywidgets (jupyter-widgets) |
| Future UI | Streamlit or D3 (Round 2+) |

### Environment Considerations

- Discover TIP environment constraints during development
- Tests must verify environment compatibility
- Solution must handle own dependencies (install/update via pip)
- Available extensions: jupyter-ai-core, jupyter-widgets-jupyterlab-manager, PYPI manager

### Data Sources

| Source | Priority | Purpose |
|--------|----------|---------|
| PATSTAT | Core | Patent applications, applicants, IPC/CPC |
| 35 Technology Sectors | Core | Predefined sector classification |
| IPC Concordance | Core | Sector-to-IPC mapping validation |
| European Universities | Nice-to-have | Innovation network analysis |
| EUROSTAT/World Bank/OECD | Nice-to-have | Socioeconomic correlations |

---

## Risks and Assumptions

### Critical Risk

**PATSTAT Complexity and Data Quality**

This is the primary concern. PATSTAT has known challenges:
- Applicant name variations (same company, different spellings)
- Address parsing inconsistencies
- Classification gaps and errors
- Regional attribution complexity (NUTS mapping)

**Mitigation:**
- Build on proven query patterns
- Implement data quality indicators in UI
- Set realistic expectations with users
- Document known limitations

### Other Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| TIP environment constraints | Medium | Medium | Early testing, adaptive design |
| Scope creep from EPO | Medium | High | Clear MVP definition, change control |
| Timeline pressure (4 weeks) | High | High | Prioritize ruthlessly, defer nice-to-haves |
| Conference demo failure | Low | Critical | Multiple dry runs, backup demos |

### Assumptions

- TIP environment supports required Python libraries (or allows installation)
- PATSTAT data access via existing EPO patstat library works as documented
- 35 technology sectors and IPC concordance are stable/documented
- Rainer Kaysen remains the primary stakeholder

---

## Timeline

| Milestone | Date | Deliverable |
|-----------|------|-------------|
| Project Start | 2026-01-10 | Product Brief approved |
| Working Prototype | Mid-February 2026 | Core features functional |
| Rainer Review | Feb-March 2026 | Feedback incorporation |
| Polish & Testing | March-April 2026 | Production-ready |
| PATLIB Conference | May 2026 | Live demo |
| Pilot Launch | 2026 | Rollout to select PATLIBs |

---

## Supporting Materials

### Input Documents

- PRD_TIP4PATLIBS_Technical_Document.pdf (EPO customer briefing)
- PATLIB interview findings (6 structured interviews)

### Reference

- EPO patstat Python library documentation
- PATSTAT data model
- 35 Technology Sectors concordance list
- NUTS regional classification

---

_This Product Brief captures the vision and requirements for TIP for PATLIBs._

_It was created through collaborative discovery and reflects the unique needs of this enterprise/institutional project._

_Next: PRD workflow will transform this brief into detailed product requirements with epics and user stories._
