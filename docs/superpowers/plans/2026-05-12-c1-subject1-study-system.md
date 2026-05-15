# C1 Subject 1 Study System Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development for execution only after this plan is approved.

## Goal

Build a local-first C1 科目一学习系统 from `doupoa/DrivingTestSubjectOne`, using current official regulations as the authority layer. The project should produce five reviewable deliverables:

1. a normalized local C1 科目一 question bank
2. a法规校验 and stale-risk audit report
3. a full electronic knowledge handbook, not a compressed short guide
4. image assets for signs, gestures, dashboard lights, and other visual questions
5. lightweight local study tools: CLI first, static Docusaurus practice page second

This plan is for review before implementation. The user has resolved the initial scope questions below; implementation still starts only after explicit approval to proceed.

## User-approved planning decisions

- Handbook length: do not compress; plan for the original expanded ~300-350 page electronic handbook.
- Image strategy: first try to extract or capture images from the selected question bank/source material; if that is impractical, use web-sourced images with attribution or create hand-drawn/recreated diagrams.
- Format target: electronic only. Author handbook content in Markdown/MDX and generate HTML with Docusaurus. Do not hand-write the handbook directly as standalone HTML, and do not design for print or A5 saddle-stitch layout.
- Subproject root: all new data, content, tools, assets, reports, and generated site output live under `c1-subject/`. Existing `reports/` research files stay as historical inputs only.
- Question types: C1 科目一 has only single-choice and true/false questions. The importer should model only those two types and flag any unexpected multi-answer record as invalid/source drift.
- Question-bank attribution: required. Every generated dataset/material must clearly state that practice questions come from the third-party `doupoa/DrivingTestSubjectOne` repository unless later replaced by another source.
- Learner audience: serve both zero-base/time-poor learners and experienced/quick-pass learners. Study plans and chapter intros should include both routes.

## Current inputs and known facts

### Repository artifacts already created

- `reports/c1-subject1-question-bank-20260512/README.md` documents reliable source tiers: official regulations for authority, third-party banks for practice.
- `reports/c1-subject1-question-bank-20260512/downloadable-sources.md` documents the verified `doupoa/DrivingTestSubjectOne` download flow.
- `reports/c1-subject1-question-bank-20260512/booklet-structure-design.md` is a curriculum draft from the planning team.
- `docs/superpowers/plans/2026-05-12-local-study-question-bank.md` is a tool-only subplan from the planning team.

### Verified dataset profile

Downloaded source:

- URL: `https://raw.githubusercontent.com/doupoa/DrivingTestSubjectOne/main/q.json`
- License noted by upstream repo: MIT
- Upstream README last update noted in our report: `2022/07/17`
- Raw records: `4378`
- `subject=1` records: `2545`
- `subject=4` records: `1833`

Observed `subject=1` shape:

- `style=1`: `1758`
- `style=2`: `787`
- `type=3`: `1281`
- `type=1`: `1264`
- `chapterId` distribution: `1:1242`, `2:547`, `5:351`, `3:184`, `15:121`, `14:59`, `4:41`
- C1 科目一 only has true/false and single-choice questions; all observed `subject=1` answers currently have length `1`, and any multi-answer imported record should be flagged as invalid/source drift

Important implication: the curriculum draft mentions “multiple choice” and an old “2-point” bucket. Treat those as draft risks, not final facts; the implementation must not add multi-select support for C1 科目一 unless the scope changes. Current point-deduction mapping must be verified against 公安部令第163号, whose buckets are 12/9/6/3/1.

## Authority model

Use this precedence when an answer, explanation, or mnemonic conflicts:

1. current law / administrative regulation
2. current public-security ministry rule
3. official traffic-management platform guidance
4. third-party question bank text
5. study mnemonics and generated explanations

Primary current references:

- 《机动车驾驶证申领和使用规定》公安部令第172号, effective 2025-01-01: driver license eligibility, C1/C2 vehicle scope, exams, renewal, replacement, internship/probation, verification/review.
- 《道路交通安全违法行为记分管理办法》公安部令第163号, effective 2022-04-01: point-deduction questions; current buckets are 12/9/6/3/1.
- 《机动车登记规定》公安部令第164号, effective 2022-05-01: registration, plates, 行驶证, transfers, temporary plates, inspection-related business.
- 《中华人民共和国道路交通安全法》 current 2021 amendment: baseline duties, penalties, DUI/escape/without-license liability, insurance, enforcement.
- 《中华人民共和国道路交通安全法实施条例》 current amended version: detailed traffic rules, speed, lane usage, overtaking, turning, lighting, stopping/parking, expressway behavior.

Citation target format for generated materials:

```text
【公安部令第163号《道路交通安全违法行为记分管理办法》第8/9/10/11/12条，2022-04-01施行】
```

Use one citation per verified knowledge block. For non-statutory safety-operation knowledge, mark `pedagogical/non-statutory` and cite the 科目一考试范围 from 公安部令第172号 rather than inventing a statute.

## File structure

Create a standalone `c1-subject/` subproject. `c1-subject/` itself is the Docusaurus project root, so handbook source, generated HTML, data, assets, scripts, CLI, and local reports stay together. New implementation artifacts should not be added to top-level `reports/`, `data/`, `content/`, `web/`, or `cli/` directories.

```text
c1-subject/
  README.md
  package.json
  docusaurus.config.ts
  sidebars.ts
  docs/
    handbook-outline.md
    chapter-00-exam-overview.md
    chapter-01-law-regulations.md
    chapter-02-traffic-signals.md
    chapter-03-safe-civilized-driving.md
    chapter-04-driving-operation-basics.md
    chapter-05-new-rules-local-notes.md
    study-plan.md
    appendices.md
  src/
    components/
    pages/
      index.tsx
      practice.tsx
  static/
    img/
      c1-subject/
  data/
    raw/
      driving-test-subject-one-q.json
    processed/
      questions.json
      questions.csv
      metadata.json
    audits/
      stale-risk-report.md
      law-source-registry.json
      topic-map.json
  assets/
    source-captures/
    web-sourced/
    hand-drawn/
    attribution.json
  scripts/
    import_questions.py
    audit_stale_risks.py
  cli/
    study.py
  reports/
    source-validation.md
    sample-audit-findings.md
  build/        # generated by Docusaurus, not hand-edited
```

Minimum acceptable structure:

- `c1-subject/data/` for raw and processed question data
- `c1-subject/assets/` for sourced/captured/recreated images and attribution metadata
- `c1-subject/docs/` for Markdown/MDX handbook content
- `c1-subject/` for Docusaurus configuration and generated HTML site output
- `c1-subject/src/pages/practice.tsx` for the browser practice page
- `c1-subject/cli/study.py` for local terminal practice
- `c1-subject/reports/` for source validation and audit findings

## Data schema

Normalize every question into one stable internal shape:

```json
{
  "id": "string",
  "source": "DrivingTestSubjectOne",
  "source_id": "string",
  "source_url": "string",
  "source_license": "string|null",
  "source_retrieved_at": "YYYY-MM-DD|null",
  "subject": "1",
  "chapter_id": "string",
  "question_type": "true_false|single_choice",
  "question": "string",
  "options": ["string"],
  "answer": "string",
  "answer_text": "string",
  "answer_skill": "string",
  "tags": ["string"],
  "topic": "string",
  "subtopic": "string",
  "vehicle_scope": "C1-general|all-motor-vehicles|special-vehicle|non-C1|unknown",
  "primary_source": "string|null",
  "article_refs": ["string"],
  "effective_date": "YYYY-MM-DD|null",
  "last_verified": "YYYY-MM-DD|null",
  "stale_risk": "low|medium|high|unknown",
  "validation_notes": "string"
}
```

Required during first implementation:

- `id`
- `source_id`
- `subject`
- `chapter_id`
- `question_type`
- `question`
- `options`
- `answer`
- `answer_skill`
- `topic`
- `stale_risk`

Can be filled progressively:

- `primary_source`
- `article_refs`
- `effective_date`
- `last_verified`
- `validation_notes`

## Topic routing rules

Use these rules to map questions to authority sources and handbook sections:

| Question topic | Primary source | Booklet destination |
| --- | --- | --- |
| 扣分、满分学习、记分减免、代扣分 | 公安部令第163号 | Chapter 1 + point-deduction专项 |
| 申领、准驾车型、年龄、考试、换证、补证、审验、注销、实习期 | 公安部令第172号 | Chapter 1 + license/time专项 |
| 登记、号牌、行驶证、临牌、变更、转让、抵押、注销、检验标志 | 公安部令第164号 | Chapter 1 + registration subsection |
| 通行规则、灯光、让行、超车、掉头、停车、高速、速度 | 道交法 + 实施条例 | Chapter 3 + speed专项 |
| 交通信号、标志、标线、交警手势 | 实施条例 + standards where available | Chapter 2 |
| 事故处理、逃逸、现场处置 | 道交法 + 实施条例 | Chapter 1 / Chapter 3 depending on question |
| 安全文明、操作常识、仪表 | Exam scope + pedagogical source | Chapter 3 / Chapter 4 |
| 客货运、危化品、校车、摩托车专用 | Specialized source or exclude | Appendix or exclusion list |

## Implementation phases

### Phase 0: Scope lock

The initial review questions are resolved:

1. Build the full system, not a data-only/tool-only subset.
2. Target the expanded ~300-350 page electronic handbook; do not compress to a short edition first.
3. Use Markdown/MDX as the source format and Docusaurus as the HTML generator.
4. Put all new project artifacts under `c1-subject/` as a standalone subproject.
5. Include visual-question planning from the start, but implement image acquisition as a controlled asset workflow.
6. Model C1 科目一 question types as true/false and single-choice only.
7. Keep `DrivingTestSubjectOne` as the primary practice bank despite known 2022 freshness risk, with explicit attribution and stale-risk audit.
8. Serve both learner personas: zero-base/time-poor and experienced/quick-pass.

Exit criteria:

- Scope decisions above are reflected in data, content, asset, tool, and documentation tasks.
- Any future change to these decisions updates this plan before implementation continues.

### Phase 1: Data ingestion and normalization

1. Add `c1-subject/data/raw/` and store the downloaded `q.json` with source notes.
2. Write a small importer that filters `subject=1` only.
3. Normalize field names and option arrays.
4. Map `question_type` only to `true_false` or `single_choice`; write any unexpected multi-answer record to the audit output instead of supporting it as a normal C1 type.
5. Generate `c1-subject/data/processed/questions.json`, `questions.csv`, and `metadata.json`.
6. Record counts by subject, style, type, chapter, and answer shape.

Verification:

- Raw count remains `4378`.
- Processed C1 科目一 count remains `2545` unless source changes.
- No `subject=4` records in processed output.
- All processed rows have `id`, `question`, `answer`, and normalized `options`.

Manual QA surface:

- Open the CSV in a text viewer and confirm Chinese text, options, and answers are readable.
- Use a tiny driver command to print 5 random normalized questions.

### Phase 2: Topic map and stale-risk audit

1. Create `c1-subject/data/audits/law-source-registry.json` with source title, authority, order number, effective date, canonical URL, retrieval date, and notes.
2. Create `c1-subject/data/audits/topic-map.json` with topic routing rules and keyword patterns.
3. Tag each question with `topic`, `subtopic`, and `vehicle_scope`.
4. Run stale checks for:
   - `2分`
   - `60周岁`
   - old order numbers such as `91`, `111`, `123`, `124`, stale `162` references when superseded
   - `回核发地` and similar old offline-only service language
   - A/B/D/E/F-only vehicle categories in C1-general content
   - point-deduction answers not matching 12/9/6/3/1 current buckets
5. Write `c1-subject/data/audits/stale-risk-report.md` with high-risk findings first.

Verification:

- Every question has a topic or `unknown` tag.
- Every high-risk match includes the matched phrase, question ID, and suggested authority source.
- Stale-risk report separates “requires legal update” from “may be non-C1/special-vehicle”.

Manual QA surface:

- Pick 10 high-risk questions and trace them from processed JSON to the audit report.
- Pick 5 low-risk questions and confirm they are not over-flagged.

### Phase 3: Electronic handbook outline cleanup

1. Use `reports/c1-subject1-question-bank-20260512/booklet-structure-design.md` as a draft, not a final source.
2. Create `c1-subject/docs/handbook-outline.md` with corrected current-law assumptions and a ~300-350 page target.
3. Remove or mark unsupported claims:
   - state that C1 科目一 only has true/false and single-choice questions; treat any multi-select wording as draft error or source drift
   - replace old 12/6/3/2/1 point structure with current 12/9/6/3/1
   - avoid “all 2545 questions are current” phrasing
4. Keep the useful handbook organization, expanded for electronic reading rather than print constraints:
   - Chapter 0: exam overview and study routes
   - Chapter 1: law, license, points, penalties, accident handling, registration
   - Chapter 2: traffic signals, signs, markings, gestures
   - Chapter 3: safe and civilized driving
   - Chapter 4: driving operation basics
   - Chapter 5: new-rule and local-rule notes
   - appendices: mnemonics, keyword index, confusing concepts, law index
5. For each section, define both learner paths:
   - zero-base/time-poor: plain-language explanation, minimum daily action, and what can be skipped safely
   - experienced/quick-pass: traps, contrast tables, and fast diagnostic questions
6. For each section, define:
   - target questions
   - authority source
   - common traps
   - representative examples
   - verification state

Verification:

- Outline references only current point buckets.
- Every chapter declares whether it is statute-backed or pedagogical.
- No chapter promises image assets that are not available.

Manual QA surface:

- Read Chapter 1 outline against the audit report and confirm high-risk law topics have explicit verification slots.

### Phase 4: Image asset workflow

Use images only through a tracked asset pipeline.

Priority order:

1. Question-bank/source captures: capture or extract images that are already part of the selected practice source, then record source URL, capture date, question IDs, and whether the use is internal-study-only.
2. Official standards as ground truth for redraws: use current standards such as GB 5768.2-2022 for road traffic signs, GB 5768.3-2025 for road markings, and GB 5768.9-2025 for accident-management-area signs as reference sources. Prefer redrawing/vector reconstruction over embedding scanned standard figures when license terms are unclear.
3. Legally reusable web sources: use only when license/source terms are clear enough for local educational material, and record exact URL, license, and retrieval date.
4. Hand-drawn/recreated diagrams: preferred fallback for traffic signs, police gestures, scenario diagrams, and simplified dashboard indicators when source licensing is unclear or extraction is too slow.

Implementation tasks:

1. Create `c1-subject/assets/attribution.json`.
2. Define image metadata fields: `asset_id`, `kind`, `source_type`, `source_url`, `license_or_terms`, `retrieved_at`, `related_question_ids`, `redrawn_from_standard`, `internal_study_only`, `notes`.
3. Record standard references with title, standard number, publication/effective year, access portal, and whether the asset is reused, redrawn, or newly created.
4. Create an asset inventory table in the handbook for traffic signs, gestures, markings, dashboard indicators, and scenario diagrams.
5. For the first milestone, process only the images needed by the first selected content slice; do not block data/CLI work on complete image coverage.

Verification:

- Every non-hand-drawn image has source URL, retrieval date, and license/terms note.
- Every standard-based image is labeled as redrawn/recreated from a reference standard, not a scanned reproduction.
- Every hand-drawn/recreated image is labeled as recreated for study, not copied from an official/commercial source.
- No image is embedded without an `asset_id` and attribution record.
- Avoid paid question sites, VIP PDFs, random image-search results without license, and OEM dashboard manual images unless permission is clear.

Manual QA surface:

- Open one handbook section containing an image and trace it to `c1-subject/assets/attribution.json`.
- Confirm the handbook credit line is short but sufficient, e.g. `Source: GB 5768.2-2022 reference; redrawn for study` or `Screenshot from DrivingTestSubjectOne-derived practice source; study reference only`.

### Phase 5: First content slice

Implement one vertical slice before generating the whole handbook:

1. Choose `Chapter 1 / 违法记分制度` as the first slice.
2. Pull only relevant questions from processed data.
3. Verify the point-deduction framework against 公安部令第163号.
4. Write one polished knowledge block with:
   - concept explanation
   - current rule table
   - examples from the question bank
   - “why wrong answers are tempting” notes
   - citations
5. Add a short self-test section using real normalized questions.

Verification:

- All cited point buckets match 12/9/6/3/1.
- No answer explanation relies only on third-party `answerSkill` if the rule is statutory.
- Every example can be traced to `source_id`.

Manual QA surface:

- A learner can read the slice and answer 5 related practice questions without opening the raw JSON.

### Phase 6: CLI study tool

Use the existing tool subplan as input, but keep the first CLI deliberately small.

Commands:

```text
python3 c1-subject/cli/study.py quiz c1-subject/data/processed/questions.json
python3 c1-subject/cli/study.py random c1-subject/data/processed/questions.json --count 20 --tag 扣分
python3 c1-subject/cli/study.py review c1-subject/data/processed/questions.json
python3 c1-subject/cli/study.py search c1-subject/data/processed/questions.json --query 扣分
```

Minimum behavior:

1. Load normalized JSON.
2. Run quiz mode one question at a time.
3. Accept answer input.
4. Show correct answer and existing `answer_skill`.
5. Persist wrong answers to `.study-review.json`.
6. Review wrong answers.
7. Randomize question order.
8. Filter by tag/topic.
9. Search by question text, options, answer skill, and tags.

Verification:

- JSON load works with processed output.
- Quiz accepts correct and wrong answers.
- Wrong answers appear in review file.
- Review mode reads the review file.
- Random mode changes ordering across runs.
- Search returns matching question IDs.

Manual QA surface:

- Run a 5-question quiz in a terminal.
- Intentionally answer one wrong question.
- Run review mode and confirm the wrong question appears.
- Run one bad input and confirm the CLI does not corrupt state.

### Phase 7: Docusaurus handbook site and practice page

Build after the CLI proves the schema. The handbook source is Markdown/MDX under `c1-subject/docs/`; Docusaurus generates the final HTML into `c1-subject/build/`. Do not hand-edit generated HTML.

Minimum behavior:

1. Initialize/configure Docusaurus at `c1-subject/`.
2. Put handbook chapters in `c1-subject/docs/` as `.md` or `.mdx` files.
3. Put public site images under `c1-subject/static/img/c1-subject/`, copied or optimized from tracked assets in `c1-subject/assets/`.
4. Configure `c1-subject/sidebars.ts` for handbook chapters and study-plan docs.
5. Add reusable React widgets under `c1-subject/src/components/` only when MDX needs interactivity.
6. Add a custom React practice page at `c1-subject/src/pages/practice.tsx`.
7. The practice page imports or fetches normalized question data from `c1-subject/data/processed/questions.json` during local development/build.
8. Store wrong answers and progress in `localStorage`.
9. Search/filter by topic/tag/text.

Verification:

- Docusaurus dev server renders the handbook docs.
- `npm run build` in `c1-subject/` generates static HTML in `c1-subject/build/`.
- Markdown/MDX edits update the rendered HTML without editing generated files.
- The practice page displays question, options, answer reveal, and explanation.
- Wrong answers persist after reload.
- Browser console has no errors during the happy path.

Manual QA surface:

- Run the Docusaurus site locally from `c1-subject/`.
- Open the handbook route and confirm a Markdown chapter renders.
- Open `/practice`, load/import `questions.json` if needed, and complete 3 questions.
- Reload and confirm wrong-answer state persists.

### Phase 8: Study plan and practice plan

Create `c1-subject/docs/study-plan.md` with three routes:

1. 7-day sprint: for users already familiar with basic driving concepts.
2. 14-day standard: recommended default.
3. 30-day steady: for zero-base learners.

Each route should include two persona overlays:

- zero-base/time-poor: fewer concepts per day, more examples, explicit “must know vs can skim” markers
- experienced/quick-pass: diagnostic quiz first, skip paths, trap tables, and weak-topic drills

Each route should specify:

- daily reading target
- daily quiz target
- wrong-question review target
- checkpoint score threshold
- when to switch from chapter practice to mock practice

Suggested thresholds:

- chapter practice: reach 90%+ before moving on
- mixed random practice: reach 92%+ before mock-only phase
- final readiness: repeated 100-question mocks at 95%+ with point/law/stale-risk topics stable

Verification:

- Study plan references actual content chapters and CLI/browser tool commands.
- No day requires content that has not been generated yet unless marked “future phase”.

Manual QA surface:

- Follow Day 1 instructions with the current vertical slice and confirm all referenced files/commands exist.

### Phase 9: Documentation and handoff

1. Update `c1-subject/README.md` with the project entry points.
2. Link source reports and processed data location.
3. Document source freshness risks clearly.
4. Document third-party question-bank attribution clearly in README, metadata, generated handbook intro, and tool UI/help text.
4. Document how to rerun import/audit.
5. Document how to use CLI and Docusaurus practice page.
6. Add a “not official题库” disclaimer.

Verification:

- A new user can start from README and run the import, quiz, and Docusaurus practice page.
- All paths in README exist.
- All commands in README have been manually executed once.

Manual QA surface:

- Start from README only and complete one quiz session.

## Non-goals

- Do not claim access to a complete official公安部/12123 downloadable question bank.
- Do not copy commercial app question explanations or protected sign images without source/rights review and attribution.
- Do not create print-first or A5 saddle-stitch layouts; electronic Docusaurus-generated HTML/PDF export is the target.
- Do not hand-write the handbook as standalone HTML; Markdown/MDX is the source of truth and Docusaurus owns generated HTML.
- Do not build accounts, sync, backend services, or cloud storage.
- Do not implement a heavy spaced-repetition algorithm in the first version.
- Do not teach A/B/D/E/F-only or commercial transport rules as C1-general content unless clearly marked.
- Do not publish stale 2022-era point or age rules without current-law verification.

## Risks and mitigations

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Upstream question bank is old | Wrong answers or stale explanations | Add stale-risk audit before content writing |
| Third-party bank is not official | Cannot market as official题库 | Use “practice bank” wording and cite official法规 separately |
| Draft handbook outline has stale assumptions | Learner confusion | Treat draft as planning input only; correct in `content/` |
| Legal citations are labor-intensive | Slow content generation | Start with one vertical slice, then expand by topic |
| Image-heavy traffic sign content may need assets | Browser/handbook delay | Use the tracked asset workflow: source capture first, attributed web source second, hand-drawn/recreated fallback |
| CLI and web duplicate logic | Maintenance cost | Keep schema simple; duplicate small parsing logic if needed rather than adding build tooling |

## Resolved review decisions

- Handbook length: expanded ~300-350 pages; no compressed edition first.
- Image strategy: question-bank/source captures first; attributed web images or hand-drawn/recreated diagrams if extraction is impractical.
- Format: electronic only; author in Markdown/MDX and generate HTML with Docusaurus rather than writing handbook HTML directly.
- Subproject root: all new artifacts live under `c1-subject/`.
- Question types: only true/false and single-choice for C1 科目一.
- Question source attribution: required everywhere user-facing and in metadata.
- Audience: serve both zero-base/time-poor learners and experienced/quick-pass learners.

## Proposed first approved milestone

If no changes are requested, implement Milestone 1 only:

1. normalize `DrivingTestSubjectOne` into `c1-subject/data/processed/questions.json`
2. generate `metadata.json` and `questions.csv`
3. create source registry and stale-risk audit script/report under `c1-subject/data/audits/`
4. create/configure the Docusaurus project at `c1-subject/`
5. correct the handbook outline into `c1-subject/docs/handbook-outline.md` with both learner paths
6. create the first image attribution inventory entry if the selected content slice needs visuals
7. build the minimum CLI quiz/review/search loop
8. manually QA a 5-question terminal quiz, one stale-risk trace, one Docusaurus Markdown render, and one source-attribution trace

This milestone creates a usable local practice loop and a trustworthy foundation for the full handbook without prematurely writing hundreds of pages.
