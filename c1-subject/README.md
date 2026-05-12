# C1 Subject 1 Study System

Local-first C1 科目一 study subproject: normalized practice-bank data, stale-law audit, CLI practice, and a Docusaurus handbook/practice site.

## Data source

Practice questions are normalized from the third-party open-source project [`doupoa/DrivingTestSubjectOne`](https://github.com/doupoa/DrivingTestSubjectOne) (MIT License; see `THIRD_PARTY_NOTICES.md`). This is not an official public-security question bank. For legal conflicts, use current official regulations as the authority.

## Common commands

```bash
PYTHONPATH=. python3 -m unittest discover -s tests
python3 scripts/audit_stale_risks.py data/processed/questions.json data/audits/stale-risk-report.md
npm run typecheck
npm run build
npm run start
```

## Main outputs

- `data/processed/questions.json` — 2,545 normalized C1 科目一 records.
- `data/audits/stale-risk-report.md` — stale-law/source-scope findings for manual review.
- `cli/study.py` — local quiz, review, and search CLI.
- `docs/` and `src/pages/practice.tsx` — Docusaurus handbook and browser practice page.
