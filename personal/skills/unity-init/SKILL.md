---
name: unity-init
description: >-
  Bootstrap or repair Codex guidance for an existing Unity repository by
  inspecting its Unity version, packages, render pipeline, layout, and
  validation commands, then creating or carefully merging a root AGENTS.md.
  Use when the user asks to initialize, bootstrap, or configure Codex for a
  Unity project. Do not trigger merely because AGENTS.md is absent.
---

# Unity Repository Bootstrap

Create an idempotent, repository-specific `AGENTS.md` workflow for an existing Unity project. Do not create Cursor configuration or overwrite existing instructions.

## Confirm the project

1. Locate the intended repository or project root instead of assuming the current directory is correct.
2. Require `Assets/` and `ProjectSettings/ProjectVersion.txt`. If either is absent, stop and explain that the target is not identifiable as a Unity project.
3. Read any existing root `AGENTS.md` and `AGENTS.override.md` before proposing changes. An `AGENTS.override.md` shadows `AGENTS.md` at the same level; do not create misleading inactive guidance. Ask the user which file should remain authoritative before changing that situation.

## Discover project facts

Read only enough project data to make the guidance accurate:

- `ProjectSettings/ProjectVersion.txt` for the exact Editor version.
- `Packages/manifest.json` and `Packages/packages-lock.json` for package versions and local or embedded dependencies.
- Relevant graphics and quality settings plus package IDs to identify Built-in, URP, HDRP, or a custom render pipeline.
- Existing `.asmdef` and `.asmref` files to understand runtime, Editor, platform, and test assemblies.
- Existing test folders, CI workflows, build scripts, repository docs, and tool wrappers to find commands that actually work here.
- Existing source layout and naming conventions. Do not impose `Assets/_Game` or another personal layout when the repository uses something else.

Record uncertainty honestly. Do not infer a render pipeline, test command, or installed Editor path when the inspected files do not establish it.

## Create or merge `AGENTS.md`

Use [assets/AGENTS.unity.md](assets/AGENTS.unity.md) as a fragment, not as a file to copy blindly.

- If `AGENTS.md` does not exist, create it with an adapted Unity section.
- If it exists, preserve all current content and merge a `## Unity project workflow` section with `apply_patch`.
- If a Unity section already exists, update that section instead of appending a duplicate.
- Replace or remove every template placeholder. Include only commands and paths supported by inspected repository files.
- Keep broad organization policy at the root and place specialized guidance in a nested `AGENTS.md` only when the repository layout genuinely needs a narrower override.

The resulting guidance should cover:

1. The exact Unity Editor version and known render pipeline.
2. Relevant source, package, settings, test, and assembly-definition paths.
3. Generated directories that Codex must not edit or broadly scan: `Library/`,
   `Temp/`, `obj/`, `Obj/`, and `Logs/`. An exact current Editor or test log may
   be read narrowly when it is the primary failure signal.
4. Serialized asset and `.meta` handling, including GUID preservation.
5. The repository's real compile, EditMode, PlayMode, build, or visual-validation commands.
6. A requirement to report when the matching Editor, license, target platform, or visual path was unavailable.

## Safety boundaries

- Never overwrite or replace an existing `AGENTS.md`; merge narrowly and preserve unrelated user content.
- Never create `.cursorignore`, `.cursor/rules/`, or other Cursor configuration as part of this workflow.
- Do not add `.codex/config.toml`, hooks, rules, packages, tests, or CI files unless the user separately requests them.
- Do not open or upgrade the project in Unity merely to initialize Codex guidance.
- Do not write personal absolute Editor paths, credentials, license data, or machine-specific secrets into repository instructions.
- Do not edit generated Unity directories or generated IDE project files. Do
  not broadly scan generated directories; a targeted read of an exact current
  Editor or test log is allowed when diagnosing that failure.

## Validate the bootstrap

1. Re-read the final `AGENTS.md` and inspect its diff.
2. Confirm that discovered version, pipeline, paths, and commands match the files inspected.
3. Confirm that no template placeholders, duplicate Unity sections, Cursor-only syntax, or unsupported commands remain.
4. Report the file changed, facts recorded, and any unresolved validation command or shadowing `AGENTS.override.md`.

Codex reads project instruction files when a run starts. State that newly written guidance governs subsequent Codex runs; do not claim it governed work already completed in the current run.
