# ⚖️ LexGuard

### A Secure, Open-Source Repository for Legal Case References

**LexGuard** is an open-source legal-learning and case-reference platform that organizes legal information from **official Indian sources** into structured, understandable, and traceable records.

> **Collect → Structure → Simplify → Verify → Connect → Reference official sources**

LexGuard does **not** replace official court websites, judgments, statutes, or professional legal databases. It is an organized **educational layer** that helps users understand and navigate those sources — the official source always remains authoritative.

---

## 🎯 Product Flow

> **Learn → Search → Compare → Verify**

The current Phase 1–3 work builds the foundation needed to support these actions.

## 🙋 Who It's For

- **Now:** the student developer, content reviewers, project guide/evaluator, and testers
- **Later:** citizens, law students, interns, junior lawyers, law clerks, registry & library staff, and legal-data reviewers

## 🗂️ Three Core Content Areas

1. **Source Provenance** — where information came from (source, publisher, official URL, retrieval date, stable-file **SHA-256**)
2. **Court Learning Structure** — court roles and publicly documented workflows (`COURT_ROLE`, `WORKFLOW_GUIDE`, `WORKFLOW_STEP`)
3. **Structured Case References** — a judgment as an organized record: title, citation, court, parties, facts, issues, provisions, actions, holding, outcome, review status, official sources

## 🧱 Data Model

- **Conceptual (Chen ER):** 10 entity sets — `SOURCE`, `CONTENT_SOURCE`, `COURT_ROLE`, `WORKFLOW_GUIDE`, `WORKFLOW_STEP`, `CASE_REFERENCE`, `PARTY`, `STATUTORY_PROVISION`, `CASE_ISSUE`, `CASE_ACTION`
- **Logical relational schema:** **13 tables**, including many-to-many association tables (`case_parties`, `case_provisions`, `workflow_guide_roles`)
- Enforces rules such as *exactly-one content-source owner*, unique step/issue/action ordering, and `(act_name, section_no)` uniqueness

## 🔐 Integrity & Review

- **SHA-256 hashing** of stable source files via a Python/FastAPI service (`hashlib`) to detect file changes/corruption — a hash proves **file version integrity, not legal authenticity**
- A **review-status lifecycle**: `draft → source_linked → metadata_reviewed → file_verified` (plus `needs_correction`, `superseded`, `withdrawn`)
- Provenance, integrity, review status, and relevance are kept as **separate** concepts — never collapsed into a single "verified" claim
- Legacy draft cases are **quarantined** and only re-seeded after review

## 🚫 What LexGuard Is Not

Not an AI lawyer, advice chatbot, or outcome predictor · not a court-management/filing system · not an official court website or a replacement for SCC Online / Manupatra / eCourts. It never tells a user what to do in a specific case, and never claims official court affiliation.

## 🛠️ Technology Architecture

```
Validated content → Pydantic validation → Python services
→ SQLAlchemy ORM → SQLite → FastAPI → Jinja2 / HTML
```

- **Python 3.12** · **FastAPI** · **SQLAlchemy** · **Pydantic** · **SQLite**
- **Jinja2** + HTML/CSS · minimal vanilla JavaScript
- **pytest** · **Uvicorn**

## 🚧 Current Status (Phase 1–3)

**Implemented:** FastAPI skeleton, root & `/api/health` endpoints, SQLite connection, legacy models, five JSON case files, legacy hash & seed scripts.

**In progress:** the approved 13-table schema & models, updated Pydantic schemas, official-source ingestion, the Python hash service, draft-quarantine workflow, transactional idempotent seeding, and a substantive test suite.

**Later phases:** public browsing, court-learning pages, search, comparison, multi-factor relevance analysis, and AI-assisted extraction (AI output always stays a draft requiring human review).

## ✅ Phase 1–3 Completion Criteria

Approved schema implemented · model-import conflict removed · Pydantic validation · source provenance stored · Python-generated file hashes · drafts quarantined · reviewed records separated · repeatable seeding · key constraints tested · health reporting accurate · no future feature falsely claimed as done.

---

<div align="center">
<strong>Structured, understandable legal information that stays traceable to an official source.</strong>
<br/><br/>
Built by <a href="https://github.com/Vijayaraj-IHT">Vijayaraj K P</a>
</div>
