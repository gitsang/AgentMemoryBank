# Local Study Question Bank Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development for execution only after this plan is approved.

## Goal
Build a tiny, local-only study tool that works from a JSON/CSV question bank and ships in two forms:
1. minimal CLI
2. static local HTML page

Priority order:
1. quiz/review mode
2. random practice
3. searchable lookup

No backend. No build system unless truly needed.

## File structure

Create or modify only focused files:

- `cli/` — CLI entrypoint and question-bank loading
- `web/` — single static HTML page, CSS, and tiny JS
- `data/` — sample question bank and any saved review queue state
- `README.md` — local usage, formats, examples
- `docs/superpowers/specs/` — only if a formal spec is later needed

## Deliverables

### CLI
- Load `json` and `csv`
- Start a quiz session from a local file path
- Show one prompt at a time, reveal answer on demand
- Track wrong answers in a local review file
- Support random practice
- Support basic tag filtering

### Static page
- Open locally in a browser
- Import JSON/CSV via file picker or drag/drop
- Quiz/review mode first
- Random practice second
- Search/filter third
- Persist review state in `localStorage`

## Data inputs / outputs

### Inputs
- JSON array of question objects
- CSV with matching columns

Recommended fields:
- `id`
- `question`
- `answer`
- `tags`
- `hint` (optional)

### Outputs
- CLI session output in terminal
- Local review queue file, e.g. `.study-review.json`
- Browser state in `localStorage`

## Commands

Keep commands simple:

- `study quiz <file>`
- `study random <file>`
- `study review <file>`
- `study web <file>` or open `web/index.html` directly

If one executable is enough, prefer a single CLI with subcommands over multiple scripts.

## Task breakdown

### 1) Define the question schema
- Pick a small shared schema for JSON and CSV
- Document required vs optional fields
- Decide how tags are encoded in CSV

### 2) Implement CLI loading and quiz loop
- Parse JSON/CSV
- Normalize records into one in-memory shape
- Implement quiz mode first
- Add wrong-answer capture and review queue persistence

### 3) Add random practice and tag filtering
- Reuse the same normalized dataset
- Shuffle questions
- Filter by tags before selection

### 4) Build the static HTML page
- Single-page local app
- Import question bank
- Reuse quiz/review flow
- Save progress locally

### 5) Add lookup/search
- Search by question text, answer text, and tags
- Keep it simple, client-side only

### 6) Write README and examples
- Show supported file formats
- Show all commands
- Include a sample JSON and CSV

## Manual QA surface

Verify these by hand:
- JSON import works
- CSV import works
- quiz mode shows prompt, answer reveal, and result tracking
- wrong answers appear in review queue
- random practice changes order between runs
- tag filter reduces the candidate set
- static page works with no server after opening locally
- state persists across reloads in the browser

## Recommended implementation order

1. schema
2. CLI quiz/review loop
3. CLI random + tags
4. static HTML page
5. search
6. README/examples

## Out of scope

- accounts or sync
- cloud storage
- spaced-repetition algorithms beyond a simple review queue
- build pipeline
- framework-heavy frontend
