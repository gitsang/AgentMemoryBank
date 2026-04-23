---
title: YouTube to Chinese Voiceover Workflow Design
date: 2026-04-22
status: draft-for-review
---

# YouTube to Chinese Voiceover Workflow Design

## Goal

Use the provided YouTube video (`3zgm60bXmQk`) as the concrete example to run a complete personal-scale workflow that produces a Chinese voiceover version of the source video, while extracting the verified process into a reusable skill for this repository.

The implementation target is a **Chinese voiceover edition** rather than voice cloning or lip-sync. The workflow must stay low-cost, reproducible by one person, and explicit about where manual review is still required.

## Repository Fit

This repository currently centers around research artifacts under `reports/` and does not yet contain a `skills/` or `docs/` structure. To keep the work auditable and reusable:

- execution evidence and generated assets will live under `reports/youtube-zh-dub-3zgm60bXmQk-20260422/`
- reusable process guidance will be added under `skills/youtube-to-chinese-voiceover/`
- this design document lives under `docs/superpowers/specs/` to preserve the planning trail separately from the execution artifacts

## Scope

### In Scope

1. Download the sample YouTube video or its audio track.
2. Capture basic source metadata for traceability.
3. Generate an English transcript and subtitle timing.
4. Rewrite the transcript into a natural Chinese voiceover script.
5. Generate a Chinese narration audio track.
6. Combine the narration with the source video into a playable output.
7. Record commands, artifacts, issues, and manual interventions in a report.
8. Distill the validated workflow into a reusable skill.

### Out of Scope

1. Voice cloning that imitates the original speaker.
2. Lip-sync or face reenactment.
3. Batch processing multiple videos.
4. Full publishing automation.
5. Commercial-rights clearance beyond noting legal/copyright risk.

## Success Criteria

The workflow is considered successful when all of the following are true:

1. A local copy of the source media or audio exists.
2. An English transcript with usable timing data exists.
3. A Chinese script exists and reads naturally enough for narration.
4. A Chinese narration audio file exists.
5. A playable Chinese-voiceover video exists.
6. `report.md` in the new report directory explains the end-to-end process, failures, fixes, and outputs.
7. A new skill captures only the steps that proved stable during the real run.

## Recommended Approach

### Option A — Pure Manual Demo

Run the example once and write a narrative report.

- Pros: fastest path to a one-off demo
- Cons: weak repeatability, poor reuse, easy to forget exact commands and failure handling

### Option B — Personal Practical Workflow with Incremental Skill Extraction (Recommended)

Run the actual pipeline on the sample video, save every meaningful intermediate artifact, document exact commands and fixes, then extract the stable patterns into a skill.

- Pros: validated by a real run, repeatable for future videos, balanced cost/effort
- Cons: slightly more upfront structure than a pure demo

### Option C — Write the Skill First, Then Execute It

Design an idealized skill before touching the real video.

- Pros: clean on paper
- Cons: high risk of encoding assumptions that fail during real execution

Option B is recommended because it makes the skill evidence-based rather than aspirational.

## Workflow Architecture

### Phase 1 — Source Intake

- Input: YouTube URL supplied by the user
- Tools: `yt-dlp` for media retrieval
- Outputs:
  - source media or extracted audio
  - metadata file capturing title, URL, id, and download details

### Phase 2 — Transcription

- Preferred tool: `faster-whisper`
- Outputs:
  - raw transcript
  - subtitle file with timestamps if supported by the chosen invocation
- Fallback: if local transcription tooling is unavailable, document the blocker and use the closest viable local or API-based transcription path while preserving the same artifact structure

### Phase 3 — Chinese Script Adaptation

- Transform the English transcript into Chinese narration copy
- Style target:
  - natural spoken Chinese
  - shorter sentences than the source transcript
  - meaning preserved over literal translation
- Manual review is expected here because transcript noise and culture-specific phrasing often require judgment

### Phase 4 — Chinese TTS Narration

- Preferred outcome: one complete Chinese narration audio file
- Initial constraint: use standard Chinese TTS rather than voice cloning
- Selection criteria:
  - low friction
  - low cost
  - acceptable naturalness
- If multiple TTS paths are available, prefer the one that can be reproduced with the least setup in this environment

### Phase 5 — Video Assembly

- Combine source video with new Chinese audio
- Preserve a simple output target: one playable mp4
- Subtitle burn-in is optional unless needed for demonstration value or timing clarity
- If full replacement of the audio track produces poor pacing, record that and document the manual adjustment required

### Phase 6 — Report and Skill Extraction

- Save the full run in `reports/youtube-zh-dub-3zgm60bXmQk-20260422/`
- Report contents:
  - source information
  - environment and dependencies
  - commands used
  - generated artifacts
  - manual edits/review points
  - encountered issues and workarounds
  - copyright/usage caveats
- Create a skill that teaches the reusable workflow, decision points, and common failure recovery paths

## Directory Plan

```text
reports/
  youtube-zh-dub-3zgm60bXmQk-20260422/
    report.md
    source/
    artifacts/
    notes/

skills/
  youtube-to-chinese-voiceover/
    SKILL.md

docs/
  superpowers/
    specs/
      2026-04-22-youtube-to-chinese-voiceover-design.md
```

## Key Design Decisions

### 1. Optimize for Single-Person Repeatability

The workflow should favor tools and steps that one person can rerun later without building a service backend.

### 2. Prefer Evidence Over Abstraction

The skill must be derived from what actually worked on the sample video, not from an imagined best-practice workflow.

### 3. Keep the End Product Modest

The first target is a Chinese voiceover video, not a high-fidelity dubbed reconstruction. This prevents the project from expanding into voice identity, lip-sync, or studio-grade postproduction.

### 4. Preserve Manual Review Points

Transcript cleanup and Chinese script adaptation should be explicit review gates rather than pretending the workflow is fully automatic.

## Risks and Mitigations

### Tool Availability Risk

Some local tools may be missing.

- Mitigation: document installation and fallback paths in the report and only encode proven paths in the final skill.

### Transcript Quality Risk

The source audio may produce noisy transcription.

- Mitigation: allow light manual correction before translation and note the corrections in the report.

### TTS Quality / Timing Risk

Chinese narration may be too long or too short for the source pacing.

- Mitigation: prefer a voiceover-style result and document any trim, silence, or timing adjustments.

### Copyright and Reuse Risk

The workflow can be technically valid while still raising copyright or platform-policy concerns.

- Mitigation: document that the output is a technical demonstration and keep legal caveats visible in the report.

## Testing and Verification Strategy

Verification should happen at each artifact boundary:

1. Confirm the media file exists after download.
2. Confirm transcript files are readable and non-empty.
3. Review the Chinese script for naturalness and completeness.
4. Confirm the narration audio plays and has non-trivial duration.
5. Confirm the final video plays successfully and contains the Chinese audio track.
6. Confirm the report and skill reference actual produced artifacts, not hypothetical ones.

## Implementation Constraints

1. Do not commit changes unless the user explicitly asks.
2. Keep the skill tightly scoped to the validated single-video workflow.
3. Avoid over-engineering automation before the manual practical path is proven.
4. Prefer ASCII-safe filenames and stable directory names.

## Open Questions Resolved by This Design

- **What are we building?** A personal-scale, low-cost Chinese voiceover workflow proven on one real video.
- **What is the artifact strategy?** Reports store evidence; the skill stores the reusable method.
- **What is the target fidelity?** Chinese voiceover, not full dubbing realism.
- **What is the extraction method?** Execute first, then codify proven steps into the skill.

## Approval Gate

Once this design is approved, the next step is to create an implementation plan and then execute the pipeline on the sample video while recording evidence into the report directory.
