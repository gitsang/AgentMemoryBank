# AI Market Research Source Verification Framework

**Research Question:** What are the prevailing artificial intelligence technologies, application domains, and innovation trajectories in the global market as of 2025-2026?

**Framework Version:** 1.0
**Last Updated:** 2026-05-28

---

## 1. Source Quality Hierarchy

### Tier 1: Authoritative Sources (Weight: 1.0)

| Category | Examples | Auto-Qualify |
|----------|----------|--------------|
| Peer-reviewed journals | Nature Machine Intelligence, JMLR, AI Magazine, IEEE TPAMI | Indexed in Scopus/WoS |
| Official industry reports | McKinsey Global Institute, Gartner, IDC, Forrester | Methodology section present |
| Government/NGO reports | OECD AI Policy Observatory, EU AI Act documents, NIST AI RMF | Published by official body |
| Academic preprints | arXiv (cs.AI, cs.LG), SSRN | Authors affiliated with institutions |

**Acceptance Criteria:**
- Author credentials verifiable (ORCID, institutional page)
- Methodology disclosed (data collection, sample size, analytical approach)
- Publication date within 2023-2026 window
- No undisclosed conflicts of interest

### Tier 2: Reputable Sources (Weight: 0.75)

| Category | Examples | Auto-Qualify |
|----------|----------|--------------|
| Business publications | Harvard Business Review, MIT Technology Review, The Economist | Circulation > 100K |
| Tech journalism | Ars Technica, Wired, VentureBeat, TechCrunch | Editorial standards documented |
| Analyst blogs | Benedict Evans, Ben Thompson (Stratechery), a]6z blog | Author has industry track record |
| Conference proceedings | NeurIPS, ICML, AAAI, CVPR workshops | Peer-reviewed track |

**Acceptance Criteria:**
- Author identified (not anonymous)
- Sources cited within article
- Publication has editorial review process
- Date within 2023-2026

### Tier 3: Contextual Sources (Weight: 0.50)

| Category | Examples | Use With Caution |
|----------|----------|------------------|
| Company blogs | Google AI Blog, OpenAI Blog, Microsoft Research Blog | Vendor bias likely |
| Press releases | PR Newswire, Business Wire, company IR pages | Marketing language |
| Conference talks | Keynotes, panel discussions | Unverified claims possible |
| White papers | Vendor-sponsored technical reports | Methodology often opaque |

**Acceptance Criteria:**
- Company identified and verifiable
- Claims corroborated by Tier 1/2 sources
- Used for context, not primary evidence
- Date verifiable

### Tier 4: Supplementary Sources (Weight: 0.25)

| Category | Examples | Use Only For |
|----------|----------|--------------|
| Social media | Twitter/X threads by researchers, LinkedIn posts | Identifying trends, not evidence |
| Opinion pieces | Medium articles, personal blogs | Anecdotal context |
| Forum discussions | Hacker News, Reddit r/MachineLearning | Community sentiment |
| Podcasts | Lex Fridman, The AI Podcast | Expert quotes only |

**Acceptance Criteria:**
- Author identifiable and has relevant expertise
- Claims must be verified against Tier 1/2 sources
- Never used as primary evidence
- Date within 2024-2026

---

## 2. Verification Checklist

### 2.1 Source Credibility Assessment

| Criterion | Check | Pass/Fail |
|-----------|-------|-----------|
| **Author Identity** | Named author with verifiable credentials | |
| **Author Expertise** | Relevant domain experience (AI/ML, market research, tech industry) | |
| **Author Affiliation** | Institutional or organizational affiliation stated | |
| **Publication Reputation** | Known publication with editorial standards | |
| **Publication Track Record** | Consistent quality over time | |
| **Peer Review** | For academic sources: peer-reviewed or editorially reviewed | |

**Scoring:**
- 6/6: Credible (proceed)
- 4-5/6: Acceptable (note gaps)
- <4/6: Reject (unless only source available)

### 2.2 Currency Assessment

| Criterion | Threshold | Action |
|-----------|-----------|--------|
| **Publication Date** | 2024-2026 preferred | Primary data |
| **Data Collection Date** | Within 18 months of publication | Note lag |
| **Market Coverage Period** | 2023-2026 explicitly stated | Accept |
| **Prediction Horizon** | 2025-2030 forecasts | Use cautiously |

**Date Priority Matrix:**

| Date Range | Acceptance | Weight Modifier |
|------------|------------|-----------------|
| 2025-2026 | Preferred | 1.0 |
| 2024 | Acceptable | 0.9 |
| 2023 | Context only | 0.7 |
| Pre-2023 | Reject unless historical baseline | 0.0 |

### 2.3 Methodology Transparency

| Criterion | Required | Optional |
|-----------|----------|----------|
| **Data Collection Method** | Surveys, interviews, secondary data | |
| **Sample Size** | N > 100 for quantitative | |
| **Sampling Method** | Random, stratified, convenience (noted) | |
| **Analytical Approach** | Statistical methods, qualitative coding | |
| **Limitations Disclosed** | Author acknowledges limitations | |
| **Reproducibility** | Data/code available or methodology detailed enough to replicate | |

**Scoring:**
- Fully transparent: All 6 criteria met
- Partially transparent: 4-5 criteria met
- Opaque: <4 criteria met (flag for bias risk)

### 2.4 Conflict of Interest Assessment

| Indicator | Risk Level | Action |
|-----------|------------|--------|
| **Vendor-sponsored report** | High | Cross-validate with independent source |
| **Author employed by vendor** | Medium | Note affiliation, seek corroboration |
| **Consulting firm with vendor clients** | Medium | Check for client disclosure |
| **Funded by VC with AI portfolio** | Medium | Note investment bias |
| **Independent academic/analyst** | Low | Proceed with standard verification |
| **Government/NGO** | Low | Proceed with standard verification |

**Disclosure Requirements:**
- Funding sources stated
- Author affiliations listed
- Competing interests declared
- If none present: flag as "no disclosure" (not necessarily negative)

### 2.5 Citation Quality

| Criterion | Check | Weight |
|-----------|-------|--------|
| **Primary Data Cited** | References original datasets, studies, or surveys | High |
| **Citation Count** | For academic: >10 citations (Google Scholar) | Medium |
| **Cross-Referencing** | Claims supported by multiple independent sources | High |
| **Data Attribution** | Statistics traced to original source | High |
| **No Circular Citations** | Not citing sources that cite the same original | Critical |

---

## 3. Evidence Grading Rubric

### 3.1 Evidence Levels

| Level | Description | Strength | Use Case |
|-------|-------------|----------|----------|
| **Level I** | Meta-analyses and systematic reviews synthesizing multiple primary studies | Strongest | Primary evidence for market size, growth rates |
| **Level II** | Large-scale industry surveys with N>500, statistical rigor, methodology disclosed | Strong | Market trends, adoption rates, technology preferences |
| **Level III** | Individual company case studies with quantitative metrics, verified implementation | Moderate | Application domain examples, ROI data |
| **Level IV** | Expert opinions, trend analyses, forecasting reports with methodology | Supporting | Innovation trajectories, future predictions |
| **Level V** | Anecdotal evidence, single-source claims, unverified data | Weak | Context only, never primary evidence |

### 3.2 Evidence Grading Criteria

| Criterion | Level I | Level II | Level III | Level IV | Level V |
|-----------|---------|----------|-----------|----------|---------|
| **Sample Size** | Multiple studies (N>1000 total) | N>500 | N>50 | N/A (expert) | N<50 |
| **Methodology** | PRISMA-compliant | Documented | Case study protocol | Analytical framework | None |
| **Peer Review** | Published in journal | Industry review | Internal review | Editorial review | None |
| **Replication** | Highly replicable | Replicable | Partially replicable | Not replicable | Not replicable |
| **Bias Risk** | Low | Low-Medium | Medium | Medium-High | High |

### 3.3 Evidence Combination Rules

| Scenario | Acceptable | Not Acceptable |
|----------|------------|----------------|
| Single Level I source | Yes | - |
| Multiple Level II sources (≥3) agreeing | Yes | - |
| Single Level II source | Yes, with caveats noted | - |
| Multiple Level III sources (≥5) agreeing | Yes, as supporting evidence | - |
| Single Level III source | Context only | Primary evidence |
| Level IV source | Supporting only | Primary evidence |
| Level V source | Anecdotal reference only | Any quantitative claim |

---

## 4. Quality Matrix Template

### 4.1 Source Evaluation Matrix

| Field | Description | Example |
|-------|-------------|---------|
| **Source ID** | Unique identifier | SRC-2025-001 |
| **Title** | Full title | "The State of AI 2025" |
| **Author(s)** | Named authors | John Smith, Jane Doe |
| **Publication** | Source name | McKinsey Global Institute |
| **Date** | Publication date | 2025-03-15 |
| **URL/DOI** | Access link | https://... |
| **Tier** | 1-4 | Tier 1 |
| **Evidence Level** | I-V | Level II |

### 4.2 Verification Scorecard

| Criterion | Score (0-5) | Weight | Weighted Score | Notes |
|-----------|-------------|--------|----------------|-------|
| **Source Credibility** | | 0.25 | | |
| **Currency** | | 0.20 | | |
| **Methodology** | | 0.25 | | |
| **Independence** | | 0.15 | | |
| **Citation Quality** | | 0.15 | | |
| **TOTAL** | | 1.00 | | |

**Scoring Guide:**
- 5: Exceeds all criteria
- 4: Meets all criteria
- 3: Meets most criteria (minor gaps)
- 2: Meets some criteria (significant gaps)
- 1: Meets few criteria
- 0: Fails all criteria

**Threshold:**
- ≥4.0: Include as primary source
- 3.0-3.9: Include with noted limitations
- <3.0: Exclude or use as supplementary only

### 4.3 Quality Matrix Spreadsheet Template

```
| Source ID | Title | Publication | Date | Tier | Evidence Level | Credibility | Currency | Methodology | Independence | Citation | Total | Decision |
|-----------|-------|-------------|------|------|----------------|-------------|----------|-------------|--------------|----------|-------|----------|
| SRC-001   |       |             |      |      |                |             |          |             |              |          |       |          |
| SRC-002   |       |             |      |      |                |             |          |             |              |          |       |          |
```

---

## 5. Red Flags and Disqualification Criteria

### Automatic Disqualification

| Red Flag | Action |
|----------|--------|
| No author identified | Reject |
| No publication date | Reject (unless verifiable) |
| Plagiarism detected | Reject and flag |
| Fabricated data (proven) | Reject and report |
| Predatory journal (Beall's list) | Reject |
| No methodology for quantitative claims | Reject for quantitative use |

### Warning Signs (Require Additional Verification)

| Warning Sign | Action |
|--------------|--------|
| Single-source for major claim | Seek corroboration |
| Vendor-sponsored without disclosure | Flag bias risk |
| Data older than 18 months | Note currency issue |
| Sample size < 100 for survey | Note statistical limitation |
| No limitations section | Flag overconfidence |
| Circular citations detected | Trace to original source |

---

## 6. Verification Workflow

```
Source Identified
       │
       ▼
┌─────────────────┐
│ Check Tier (1-4) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐    ┌─────────────┐
│ Verify Author    │───▶│ Reject if    │
│ Identity         │    │ Anonymous    │
└────────┬────────┘    └─────────────┘
         │
         ▼
┌─────────────────┐    ┌─────────────┐
│ Check Date       │───▶│ Reject if    │
│ (2023-2026)      │    │ Pre-2023     │
└────────┬────────┘    └─────────────┘
         │
         ▼
┌─────────────────┐    ┌─────────────┐
│ Assess Method    │───▶│ Flag if      │
│ Transparency     │    │ Opaque       │
└────────┬────────┘    └─────────────┘
         │
         ▼
┌─────────────────┐    ┌─────────────┐
│ Check COI        │───▶│ Note if      │
│ Indicators       │    │ Vendor-linked│
└────────┬────────┘    └─────────────┘
         │
         ▼
┌─────────────────┐
│ Grade Evidence   │
│ Level (I-V)      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Complete Quality │
│ Matrix Entry     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Decision:        │
│ Accept/Flag/     │
│ Reject           │
└─────────────────┘
```

---

## 7. Application to AI Market Research

### 7.1 Source Categories for AI Market Research

| Research Dimension | Primary Sources (Tier 1) | Secondary Sources (Tier 2) |
|-------------------|--------------------------|----------------------------|
| **Market Size** | IDC, Gartner, Statista | TechCrunch, VentureBeat |
| **Technology Trends** | arXiv papers, IEEE publications | MIT Tech Review, Wired |
| **Adoption Rates** | McKinsey surveys, Deloitte reports | HBR articles |
| **Application Domains** | Industry-specific journals | Company case study blogs |
| **Innovation Trajectories** | Patent databases, research labs | Conference proceedings |

### 7.2 Minimum Evidence Requirements

| Claim Type | Minimum Evidence | Corroboration Required |
|------------|------------------|------------------------|
| Market size (exact figure) | Level I or II | 2+ independent sources |
| Growth rate (%) | Level II | 3+ sources agreeing within 20% |
| Technology adoption % | Level II | Survey N>500 |
| Emerging trend | Level III-IV | Expert consensus (3+ sources) |
| Company-specific claim | Level III | Official source + independent verification |
| Future prediction | Level IV | Methodology disclosed, assumptions stated |

---

## 8. Quality Assurance Checklist

Before finalizing source list, verify:

- [ ] All sources have Tier classification
- [ ] All sources have Evidence Level assigned
- [ ] Quality Matrix completed for each source
- [ ] Red flags documented and addressed
- [ ] Minimum evidence requirements met for each claim type
- [ ] Currency threshold (2023-2026) applied
- [ ] Conflict of interest assessment completed
- [ ] Cross-referencing completed for major claims
- [ ] Source diversity (not all from same publication/author)
- [ ] Geographic diversity (global perspective, not single region)

---

## Appendix A: Quick Reference Card

### Tier Quick Check
```
Tier 1: Peer-reviewed, official reports, government data
Tier 2: Reputable publications, established analysts
Tier 3: Company blogs, press releases, conference talks
Tier 4: Social media, opinion pieces, forums
```

### Evidence Level Quick Check
```
Level I:   Meta-analysis of multiple studies
Level II:  Large survey (N>500), statistical rigor
Level III: Case study with metrics
Level IV:  Expert opinion with framework
Level V:   Anecdotal, single-source
```

### Decision Matrix
```
Tier 1 + Level I-II   → Primary evidence
Tier 1 + Level III-IV → Supporting evidence
Tier 2 + Level I-II   → Primary with verification
Tier 2 + Level III-IV → Supporting evidence
Tier 3 + Any          → Context only, verify against Tier 1-2
Tier 4 + Any          → Supplementary only, never primary
```

---

**Document Status:** Ready for use
**Maintained by:** Research Quality Team
**Review Cycle:** Quarterly or as new source types emerge
