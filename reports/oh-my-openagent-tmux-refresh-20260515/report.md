# oh-my-openagent tmux/subagent display refresh issue search

Date: 2026-05-15

## User question

Query whether `oh-my-openagent` has an issue about team mode / subagent mode where, after tmux starts, the subagent window/pane data does not refresh, stays at the first message / only a system message, while the subagent is actually running.

## Search scope

- GitHub issues in `code-yeongyu/oh-my-openagent`
- Web search index for GitHub issue text and related commits
- Local workspace references for repo names and prior notes

## Exact-match result

No exact issue was found with wording equivalent to:

- `only system message`
- `first system message`
- `not refreshing`
- `subagent window stuck first message`
- `team_mode tmux_visualization pane system message refresh`

The closest GitHub issue search results for those exact phrases were empty or unrelated.

## Closest matches

### High confidence: #3280

- URL: https://github.com/code-yeongyu/oh-my-openagent/issues/3280
- Title: `[Bug]: tmux subagent panes are created but stay blank with no visible execution output`
- State: open
- Created: 2026-04-09
- Updated: 2026-04-16
- Why it matches: The issue says tmux split panes are created, pane titles/navigation hints are visible, but there is no live execution content in the panes. The parent UI can still report task completion, so subagents appear to run. This is the closest match to "pane does not refresh/show subagent data, but subagent is actually running."
- Difference: It says panes are blank/no visible output, not specifically "stuck at the first/system message."

### High confidence related fix commits

- https://github.com/code-yeongyu/oh-my-openagent/commit/91848057ea1f32c6a6bd8520bd7b2b836f1baa4f
  - Message: `fix(background-agent): fire promptAsync before tmux callback`
  - Relevant text: awaiting tmux callback blocked prompt for up to 10s; spawned pane ran `opencode attach` against an empty session and rendered a blank TUI; users saw "pane created but attach not working."
- https://github.com/code-yeongyu/oh-my-openagent/commit/c9c1c58c2cb96cf85ec86f4bf1b5af7dd8e2c7e7
  - Message: `fix(tmux-subagent): track pane without blocking on session readiness`
  - Relevant text: blocking pane tracking caused attach client to see an empty session and render a blank TUI.

These commits are especially relevant because "empty session / blank TUI while the real session later runs" is technically close to a pane staying on initial content while the child session progresses elsewhere.

### Medium confidence: #3505

- URL: https://github.com/code-yeongyu/oh-my-openagent/issues/3505
- Title: `[Bug]: Tmux subagent pane auto-closes because opencode attach exits before session is ready`
- State: open
- Created: 2026-04-18
- Why it matches: The issue says a pane appears, then disappears, while the background task continues and completes. Logs show session eventually appears/runs normally, but the pane is already gone.
- Difference: This is auto-close, not a persistent pane stuck on the first message.

### Medium confidence: #3593

- URL: https://github.com/code-yeongyu/oh-my-openagent/issues/3593
- Title: `[Bug] Inconsistent subagent/activity visibility in OpenCode UI makes running work look idle`
- State: open
- Created: 2026-04-23
- Why it matches: It reports active delegated work appearing idle or not clearly progressing in the UI while work is still ongoing.
- Difference: It is about OpenCode UI visibility, not specifically tmux panes.

### Medium confidence: #3851

- URL: https://github.com/code-yeongyu/oh-my-openagent/issues/3851
- Title: `[Bug]: Is tmux split view incompatible with the subagent delegation tmux view when team mode is set to true?`
- State: open
- Created: 2026-05-08
- Why it matches: It specifically involves team mode and subagent delegation tmux split view interaction.
- Difference: It reports the delegated agent tmux view no longer appears as split view after team mode is enabled, not stale pane output.

### Related team-mode tmux visualization issues

- #3963: https://github.com/code-yeongyu/oh-my-openagent/issues/3963
  - `team_mode.tmux_visualization silently skips pane creation...`
  - Members still spawn as child sessions in the background, but tmux panes do not appear.
- #3894: https://github.com/code-yeongyu/oh-my-openagent/issues/3894
  - `Team mode tmux visualization creates broken panes when opencode server not running`
  - Panes are created but `opencode attach` cannot reach the server.

These are relevant to team mode tmux visualization, but they are not the same as a pane that exists and stops refreshing after the first message.

## Conclusion

There is no exact issue found for "subagent pane stays at the first/system message while the subagent actually runs." The closest match is #3280, supported by the two Apr 18 commits about blank TUI / empty session during tmux attach. If filing or commenting, the best existing target is #3280 unless the failure only happens under team mode, in which case cross-link #3851 and #3963.

Suggested phrasing for a comment/new issue:

> Similar to #3280: with team mode / subagent tmux visualization, the subagent pane is created and the subagent keeps running, but the pane display does not update. In my case it stays at the initial/first system message instead of showing live child-session output. Parent/background task state confirms the subagent is still running.
