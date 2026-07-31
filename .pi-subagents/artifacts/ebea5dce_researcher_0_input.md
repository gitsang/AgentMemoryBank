# Task for researcher

搜索今天 (2025年7月17日) 的重大安全漏洞和事件。重点领域：

1. AI 安全事件（大模型漏洞、提示注入、模型窃取等）
2. 服务端安全（RCE、认证绕过、服务器软件高危CVE，如nginx/Apache/K8s/Docker/Node.js/Go/Java等）
3. 软件供应链攻击（npm/PyPI/cargo恶意包、CI/CD攻击等）

请用多个不同关键词多次搜索。每个发现需要：简要描述、来源URL、严重程度、可用的修复/缓解步骤。用中文返回。

---
**Output:**
Write your findings to exactly this path: /home/sang/src/github.com/gitsang/AgentMemoryBank/.pi-subagents/artifacts/outputs/ebea5dce/research.md
This path is authoritative for this run.
Ignore any other output filename or output path mentioned elsewhere, including output destinations in the base agent prompt, system prompt, or task instructions.

## Acceptance Contract
Acceptance level: attested
Completion is not accepted from prose alone. End with a structured acceptance report.

Criteria:
- criterion-1: Return concrete findings with file paths and severity when applicable

Required evidence: review-findings, residual-risks

Finish with a fenced JSON block tagged `acceptance-report` in this shape:
Use empty arrays when no items apply; array fields contain strings unless object entries are shown.
`criteriaSatisfied[].status` must be exactly one of: satisfied, not-satisfied, not-applicable.
`commandsRun[].result` must be exactly one of: passed, failed, not-run.
`manualNotes` and `notes` are optional strings; an empty string means no note and does not satisfy `manual-notes` evidence.
```acceptance-report
{
  "criteriaSatisfied": [
    {
      "id": "criterion-1",
      "status": "satisfied",
      "evidence": "specific proof"
    }
  ],
  "changedFiles": [
    "src/file.ts"
  ],
  "testsAddedOrUpdated": [
    "test/file.test.ts"
  ],
  "commandsRun": [
    {
      "command": "command",
      "result": "passed",
      "summary": "short result"
    }
  ],
  "validationOutput": [
    "validation output or concise summary"
  ],
  "residualRisks": [
    "none"
  ],
  "noStagedFiles": true,
  "diffSummary": "short description of the diff",
  "reviewFindings": [
    "blocker: file.ts:12 - issue found, or no blockers"
  ],
  "manualNotes": "anything else the parent should know"
}
```