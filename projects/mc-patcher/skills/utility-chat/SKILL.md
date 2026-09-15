---
name: utility-chat
description: A user-invoked mode for non-product-coding utility work such as Codex skills, plugins, configuration, AI tooling explanations, local setup audits, and source-backed research synthesis. Use only when the user explicitly invokes $utility-chat or says utility/杂活 mode. Route work to the relevant installed skill instead of duplicating its workflow. Do not trigger merely because a request is miscellaneous, and do not use as a substitute for a repository's domain skill during substantial implementation.
---

# Utility Chat

Handle cross-cutting setup and research tasks thoroughly without imposing a model choice or an artificial file/query limit.

## Route before acting

Select the smallest specialized workflow that covers the request:

| Request | Route |
|---|---|
| Create or revise a skill | Use `skill-creator` and follow its initialization, metadata, and validation process |
| Install a skill | Use `skill-installer` |
| Create or revise a plugin bundle | Use `plugin-creator` |
| Codex/OpenAI behavior, configuration, models, or current product guidance | Use `openai-docs` and its official-source route |
| Current facts, comparisons, papers, pricing, or policy research | Use `web-research` |
| Documents, PDFs, presentations, spreadsheets, images, sites, or design canvases | Use the installed artifact/domain skill that matches the output |
| Local Codex configuration audit | Inspect the actual files and current capabilities before proposing edits |

When another installed skill applies, read and follow it completely. If it is unavailable, say so briefly and use the safest local fallback.

## Work style

1. Classify the task as explanation, read-only audit, research, or mutation.
2. Inspect existing state before editing configuration or personal files.
3. Preserve unrelated user changes and keep mutations inside the requested scope.
4. Verify time-sensitive or product-specific claims through the proper official-source workflow.
5. For a change, validate the resulting file or configuration with the owning tool when available.
6. Lead the response with the outcome, then list changed paths, evidence, and remaining uncertainty.

Do not force a new task merely because the subject changes. Suggest a separate Codex task only when work is independent, context isolation is useful, or parallel writes would otherwise conflict.

## Boundaries

- Do not invent configuration keys, tool names, feature availability, prices, or model behavior.
- Do not edit global or repository configuration when the user only asked for an explanation or audit.
- Do not use broad web search for private connected data when an authorized connector is available.
- Do not turn this mode into a global verbosity override; match depth to the user's request and decision risk.
- Do not replace a project-specific development workflow such as `mc-patcher` or `unity-dev` during substantial implementation.

## Response shape

For an explanation or research task, give the direct conclusion first, cite claims near their sources, and state unresolved gaps. For a mutation, report:

```markdown
## Result
[What now works or what was changed]

## Files
- `path` — purpose

## Verification
- ...

## Remaining uncertainty
- ...
```
