<img width="100%" src="https://capsule-render.vercel.app/api?type=waving&color=0:0f2027,50:203a63,100:2c5364&height=190&section=header&text=LexGuard&fontSize=56&fontColor=ffffff&animation=fadeIn&desc=A%20Secure%2C%20Open-Source%20Repository%20for%20Legal%20Case%20References&descSize=18&descAlignY=58"/>

<div align="center">

**An open-source legal-learning & case-reference platform** that organizes information from **official Indian sources** into structured, understandable, and traceable records.

> **Collect → Structure → Simplify → Verify → Connect → Reference official sources**

<br/>

![Python](https://img.shields.io/badge/Python_3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white)
![Pydantic](https://img.shields.io/badge/Pydantic-E92063?style=for-the-badge&logo=pydantic&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![pytest](https://img.shields.io/badge/pytest-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white)

<br/>

![Phase](https://img.shields.io/badge/Phase-1%E2%80%933%20Foundation-6366F1?style=flat-square)
![Status](https://img.shields.io/badge/Status-In%20Development-F59E0B?style=flat-square)
![Open Source](https://img.shields.io/badge/Open%20Source-Yes-22C55E?style=flat-square)

</div>

---

## 🧭 Product Flow

<div align="center">

<img src="https://img.shields.io/badge/Learn-1a2980?style=for-the-badge" />
<img src="https://img.shields.io/badge/%E2%86%92-555555?style=for-the-badge" />
<img src="https://img.shields.io/badge/Search-26d0ce?style=for-the-badge" />
<img src="https://img.shields.io/badge/%E2%86%92-555555?style=for-the-badge" />
<img src="https://img.shields.io/badge/Compare-26d0ce?style=for-the-badge" />
<img src="https://img.shields.io/badge/%E2%86%92-555555?style=for-the-badge" />
<img src="https://img.shields.io/badge/Verify-2ecc71?style=for-the-badge" />

</div>

> The current **Phase 1–3** work builds the foundation (schema, validation, provenance, seeding, audit) needed to support these actions. Search, comparison, and AI-extraction are scoped to later phases.

---

## 🎯 Core Content Areas

<table>
<tr>
<td width="50%" valign="top">

### 📌 Source Provenance
Records **where legal information came from** — source, publisher, official URL, retrieval date, and a stable file's **SHA-256** hash.

### 🏛️ Court Learning Structure
Teaches court roles and publicly documented workflows — `COURT_ROLE`, `WORKFLOW_GUIDE`, `WORKFLOW_STEP` (clerks, librarians, how to verify a citation, read a cause list…).

</td>
<td width="50%" valign="top">

### 🗂️ Structured Case References
Turns a judgment into an organized record: title, citation, court, parties, facts, issues, provisions, actions, holding, outcome, review status, and official sources.

### 🔐 Integrity & Review
**SHA-256** hashing detects file changes/corruption — but proves *file version integrity, not legal authenticity* — alongside a formal review-status lifecycle.

</td>
</tr>
</table>

---

## 🧱 Data Model

<details open>
<summary><b>📐 Conceptual model — 10 entity sets (Chen ER)</b></summary>

<p align="center">
<img src="https://img.shields.io/badge/SOURCE-003B57?style=flat-square"/>
<img src="https://img.shields.io/badge/CONTENT_SOURCE-003B57?style=flat-square"/>
<img src="https://img.shields.io/badge/COURT_ROLE-003B57?style=flat-square"/>
<img src="https://img.shields.io/badge/WORKFLOW_GUIDE-003B57?style=flat-square"/>
<img src="https://img.shields.io/badge/WORKFLOW_STEP-003B57?style=flat-square"/>
<img src="https://img.shields.io/badge/CASE_REFERENCE-003B57?style=flat-square"/>
<img src="https://img.shields.io/badge/PARTY-003B57?style=flat-square"/>
<img src="https://img.shields.io/badge/STATUTORY_PROVISION-003B57?style=flat-square"/>
<img src="https://img.shields.io/badge/CASE_ISSUE-003B57?style=flat-square"/>
<img src="https://img.shields.io/badge/CASE_ACTION-003B57?style=flat-square"/>
</p>

Key relationships: `HAS SOURCE` · `REFERENCES` · `RELEVANT TO` · `CONTAINS` · `INVOLVES` (with `role_in_case`) · `CITES` · `RAISES` · `HAS STEP`.

</details>

<details>
<summary><b>🗄️ Logical schema — 13 tables</b></summary>

| Group | Tables |
|---|---|
| **Source** | `sources`, `content_sources` |
| **Court-learning** | `court_roles`, `workflow_guides`, `workflow_guide_roles`, `workflow_steps` |
| **Case-reference** | `case_references`, `parties`, `case_parties`, `statutory_provisions`, `case_provisions`, `case_issues`, `case_actions` |

Enforced rules: exactly-one content-source owner · unique `(guide, step_number)` · unique `(case, party, role_in_case)` · unique `(act_name, section_no)` · unique issue/action ordering.

</details>

---

## 🔄 Review-Status Lifecycle

<div align="center">

```text
draft → source_linked → metadata_reviewed → file_verified
        needs_correction · superseded · withdrawn
```

</div>

<sub>Provenance, integrity, review status, and relevance are kept **separate** — never collapsed into a single "verified" claim. A review status is not a legal certificate.</sub>

---

## 🏗️ Technology Architecture

```text
Validated content files
        ↓
Pydantic validation
        ↓
Python services
        ↓
SQLAlchemy ORM
        ↓
SQLite database
        ↓
FastAPI application
        ↓
Jinja2 / HTML interface
```

<div align="center">

<img src="https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white"/>
<img src="https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white"/>
<img src="https://img.shields.io/badge/SQLAlchemy-D71F00?style=flat-square&logo=sqlalchemy&logoColor=white"/>
<img src="https://img.shields.io/badge/Pydantic-E92063?style=flat-square&logo=pydantic&logoColor=white"/>
<img src="https://img.shields.io/badge/SQLite-003B57?style=flat-square&logo=sqlite&logoColor=white"/>
<img src="https://img.shields.io/badge/Jinja2-B41717?style=flat-square&logo=jinja&logoColor=white"/>
<img src="https://img.shields.io/badge/pytest-0A9EDC?style=flat-square&logo=pytest&logoColor=white"/>
<img src="https://img.shields.io/badge/Uvicorn-4051B5?style=flat-square"/>

</div>

> Free & open-source, runs locally, testable, and designed for future expansion. AI is a **future draft-assist only** — it never authenticates, sets review status, or gives legal advice.

---

## 🚧 Development Status

| | Item |
|---|---|
| ✅ | FastAPI skeleton · root & `/api/health` · SQLite connection · legacy models · 5 JSON case files · legacy hash & seed scripts |
| 🚧 | Approved **13-table schema** & models · updated Pydantic schemas · Python hash service · draft quarantine · transactional idempotent seeding · test suite |
| 🔮 | Public browsing · court-learning pages · search · comparison · multi-factor relevance · AI-assisted extraction (human-reviewed) |

**Immediate plan:** commit approved docs → clean Python 3.12 env → refactor models → implement schema → Pydantic validation → `hash_service.py` → quarantine drafts → replace seeding → add tests.

---

## ⚠️ Legal Boundaries

> 🚫 LexGuard is **not** an AI lawyer, advice chatbot, outcome predictor, court-management/filing system, or official court website — and never replaces an advocate or databases like SCC Online / Manupatra / eCourts.
> It never tells a user what to do in a specific case and claims **no official court affiliation**.

---

<div align="center">

### Structured, understandable legal information that stays traceable to an official source.

<br/>

<a href="https://github.com/Vijayaraj-IHT"><img src="https://img.shields.io/badge/Built%20by-Vijayaraj%20K%20P-0f2027?style=for-the-badge"/></a>
<a href="https://www.linkedin.com/in/vijaya-raj-k-p-9981593a0/"><img src="https://img.shields.io/badge/LinkedIn-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white"/></a>

</div>

<img width="100%" src="https://capsule-render.vercel.app/api?type=waving&color=0:2c5364,50:203a63,100:0f2027&height=110&section=footer"/>
