---
stepsCompleted: [1, 2, 3, 4, 5, 6]
status: complete
inputDocuments:
  - context/_bmadv4_docs/product-brief-tip-for-patlibs-2026-01-10.md
  - context/BPM001977_Technical_Specifications__TIP4PATLIB.pdf
  - context/index.md
  - context/project-overview.md
  - context/DTF_OPS_University_Analysis.ipynb
date: 2026-02-01
author: Arne
---

# Product Brief: TIP for PATLIBs (Phase 2)

## Executive Summary

**TIP for PATLIBs Phase 2** delivers four production-ready Jupyter notebooks that serve as both training materials and practical tools for the European PATLIB network. Commissioned by EPO Academy as part of the PATLIB2028 roadmap, this project bridges the gap between TIP's powerful capabilities and the limited programming skills of PATLIB staff.

The solution takes a "product, not education" approach: instead of more tutorials, we deliver didactically structured notebooks that teach through doing. Each notebook is immediately useful while exposing users to Python, SQL, and data analysis concepts they can build upon.

A companion Streamlit application (patstat.streamlit.app) serves as a lead generator, demonstrating TIP's potential and driving adoption of the Jupyter-based learning environment.

**Budget:** 14,000 EUR
**Deliverables:** 4 Jupyter notebooks + educational materials + 20 hours training

---

## Core Vision

### Problem Statement

PATLIB centres across Europe need to deliver patent analytics to their clients (SMEs, universities, regional authorities) but lack the programming skills to use TIP effectively. Despite extensive PATSTAT documentation and Python training materials, adoption remains low because:

1. **Skills Gap:** PATLIB staff are patent information professionals, not developers
2. **Time Constraints:** No bandwidth to learn Python from scratch
3. **Training Fatigue:** More documentation and tutorials haven't moved the needle
4. **Confidence Gap:** Staff can't confidently present TIP-based insights to clients

### Problem Impact

- EPO's investment in TIP is underutilized by a key target audience
- PATLIBs cannot deliver data-driven regional/sectoral analysis to their clients
- The PATLIB2028 goal of increased TIP adoption is at risk
- 300+ PATLIB centres across Europe remain disconnected from TIP's capabilities

### Why Existing Solutions Fall Short

| Current Approach | Why It Fails |
|------------------|--------------|
| Raw TIP/Jupyter | Requires Python knowledge to do anything useful |
| PATSTAT documentation | Reading docs ≠ being productive |
| Training workshops | Knowledge doesn't stick without practice tools |
| Commercial alternatives | Not integrated with TIP, not free for PATLIBs |

### Proposed Solution

Four Jupyter notebooks designed for the TIP environment, each serving a specific analytical use case:

| # | Notebook | Purpose | Status |
|---|----------|---------|--------|
| 1 | **Query Library** | 13+ parameterized queries with selector UI - explore, execute, modify, learn | Ready |
| 2 | **Interactive Demo** | Guided walkthrough of TIP capabilities for training sessions | Ready |
| 3 | **AI Query Builder** | Natural language → PATSTAT SQL generation | Needs Jupyter conversion |
| 4 | **University Analysis** | University innovation landscape analysis with inventor/applicant networks | Needs PATSTAT refactoring |

All notebooks use consistent patterns:
- `PatstatClient` for data access (BigQuery via TIP)
- `ipywidgets` for no-code parameter selection
- Well-documented, didactically structured code
- Dual-purpose: training material AND practical tool

### Key Differentiators

- **Learn by doing:** Notebooks are useful from first cell execution
- **TIP-native:** Built for the platform PATLIBs already have access to
- **Transparent code:** Users see Python/SQL but interact via UI controls
- **Honeypot strategy:** Streamlit app (42 queries) attracts; Jupyter (learning) retains
- **Scalable impact:** One set of materials serves 300+ PATLIB centres

---

## Target Users

### Primary Users

**PATLIB Staff (Entry-Level)**

Patent information professionals at PATLIB centres across Europe who need to deliver patent analytics but have limited or no programming experience.

| Attribute | Description |
|-----------|-------------|
| **Role** | Patent information professional, IP advisor |
| **Location** | ~300 PATLIB centres across Europe (many at universities) |
| **Technical Skills** | Comfortable with web tools; no Python/SQL experience |
| **Pain Point** | Can't use TIP effectively despite access; relies on basic searches |
| **Goal** | Deliver data-driven insights to clients without coding |
| **Success Moment** | Running a parameterized query and presenting results to a client |

**How they use the notebooks:**
- Execute pre-built queries via UI controls
- Adjust parameters (region, technology, time period)
- Export results for client presentations
- Learn by seeing the code without needing to write it

---

**PATLIB Staff (Advanced / Multiplicators)**

Ambassadors within the PATLIB network who will extend and build upon the notebooks, spreading adoption across their regional networks.

| Attribute | Description |
|-----------|-------------|
| **Role** | PATLIB staff with technical curiosity or some coding exposure |
| **Technical Skills** | Willing to read/modify Python; may have basic SQL knowledge |
| **Pain Point** | Has ideas for analyses but lacks starting points |
| **Goal** | Customize queries, add new analyses, become local TIP expert |
| **Success Moment** | Modifying a query to answer a novel business question |

**How they use the notebooks:**
- Study the code to understand patterns
- Copy and modify queries for new use cases
- Share customizations with their network
- Attend training, then cascade knowledge locally

---

**University PATLIB Staff**

PATLIB staff embedded at universities who are responsible for IP intelligence for their institution.

| Attribute | Description |
|-----------|-------------|
| **Role** | IP/patent information specialist at a university |
| **Context** | Works with tech transfer, researchers, students |
| **Pain Point** | Needs to understand their university's innovation landscape vs. competitors |
| **Goal** | Analyze university patent portfolios, inventor networks, collaboration patterns |
| **Success Moment** | Presenting university innovation insights to leadership or researchers |

**How they use the notebooks:**
- University Analysis notebook is their primary tool
- Select their university, run portfolio analysis
- Identify top inventors, industry collaborations, technology strengths
- Support tech transfer decisions with data

---

### Secondary Users

| User Type | Relationship | How They Benefit |
|-----------|--------------|------------------|
| **SME inventors/entrepreneurs** | PATLIB clients | Receive patent landscape reports from PATLIB staff |
| **University researchers** | PATLIB clients | Get innovation intelligence about their field |
| **Tech transfer offices** | Collaborators | Use PATLIB analysis for partnership decisions |
| **Regional authorities** | PATLIB clients | Receive regional innovation comparisons |
| **EPO Academy** | Training provider | Uses notebooks as training material |

---

### Key Stakeholder

**Rainer Kaysen (EPO)** - Project sponsor. Success = his satisfaction with the deliverables and PATLIB adoption. His approval determines future contracts.

---

### User Journey

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        PATLIB STAFF JOURNEY                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  DISCOVERY          ONBOARDING           CORE USAGE         MASTERY    │
│  ─────────          ──────────           ──────────         ───────    │
│                                                                         │
│  Streamlit app   →  Training session  →  Query Library  →  Customize   │
│  (honeypot)         + notebooks          execution         & extend    │
│                                                                         │
│  "This looks     →  "I can do this!" →  "This saves    →  "I built    │
│   useful"                                 me hours"        my own!"    │
│                                                                         │
│  ────────────────────────────────────────────────────────────────────  │
│                                                                         │
│  Entry-level staff may stay in "Core Usage" phase                      │
│  Multiplicators progress to "Mastery" and help others                  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Success Metrics

### Contract Deliverables (Must Deliver)

| Deliverable | Target | Measurement |
|-------------|--------|-------------|
| Jupyter Notebooks | 4 functional, documented notebooks | Delivered and accepted |
| Training Hours | 20 hours delivered | 2 training sessions + 2 working group meetings |
| Educational Materials | Handbook, quick guides, reference materials | Delivered and accepted |

### Stakeholder Satisfaction

| Stakeholder | Success Indicator |
|-------------|-------------------|
| **Rainer Kaysen (EPO)** | Happy with deliverables; wants to continue partnership |
| **EPO Academy** | Materials suitable for training curriculum |
| **PATLIB Conference audience** | Positive reception at demonstrations |
| **Training participants** | Positive feedback; able to use notebooks independently |

### Business Objectives

| Objective | Indicator |
|-----------|-----------|
| Increase TIP adoption | More PATLIBs actively using TIP after training |
| Raise staff confidence | PATLIB staff can present TIP-based insights to clients |
| Build autonomy | Staff can run analyses without developer support |
| Enable multiplicators | Advanced users extend and share notebooks within network |

### PATLIB2028 Contribution

This project directly contributes to PATLIB2028 goals:
- Increases number of PATLIB centres actively applying TIP in their services
- Raises confidence and autonomy of PATLIB staff when working with patent data
- Creates reusable training materials for ongoing adoption efforts

---

## Scope

### Core Deliverables (14k EUR)

**4 Jupyter Notebooks for TIP:**

| # | Notebook | Work Required |
|---|----------|---------------|
| 1 | **Query Library** | Migrate all 42 queries from Streamlit; add query selector UI; enable extensibility/sharing mechanism |
| 2 | **Interactive Demo** | Review, document, ensure didactic quality for training |
| 3 | **AI Query Builder** | Convert from Streamlit to Jupyter notebook for TIP environment |
| 4 | **University Analysis** | Refactor to PatstatClient; university selector for European universities |

**Educational Materials:**
- Handbook on configuring/using the notebooks
- Quick reference guides and checklists
- Step-by-step guidance with screenshots/example outputs

**Training Delivery (20 hours):**
- 2 dedicated training sessions (online or on-site)
- 2 PATLIB TIP working group meeting participations

**Ongoing Maintenance:**
- Streamlit app (patstat.streamlit.app)
- Query maintenance, updates, and extensions

---

### Out of Scope

| Item | Rationale |
|------|-----------|
| Multi-language UI | English only for this phase |
| Non-TIP deployments | Notebooks are TIP-native only |
| Custom development per PATLIB | Standard materials for all centres |

---

### Future Considerations

- Query sharing/collaboration mechanism between PATLIBs
- European university list (from DeepTechFinder or web sources)
- Community-contributed queries workflow
