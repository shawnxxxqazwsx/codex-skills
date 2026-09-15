---
name: unity-dev
description: >-
  Develop, debug, refactor, and verify Unity projects in C#, including
  MonoBehaviour, ScriptableObject, scenes, prefabs, assembly definitions,
  shaders, Editor tooling, and Unity tests. Use when the request explicitly
  concerns Unity or the repository is identifiable as a Unity project from
  Assets/ plus ProjectSettings/ProjectVersion.txt. Do not use for non-Unity
  repositories that merely contain an Assets directory, or for Codex/AGENTS.md
  bootstrap-only requests handled by unity-init.
---

# Unity Development

Work from the project's actual Unity version, package graph, assembly boundaries, and serialized data. Preserve asset identity and distinguish static review from verification performed by the Unity Editor.

## Establish project context

1. Locate the Unity project root. Require both `Assets/` and `ProjectSettings/ProjectVersion.txt`; do not treat a generic `Assets/` directory as sufficient evidence.
2. Read applicable `AGENTS.md` files and the repository's own build or test documentation before editing.
3. Read `ProjectSettings/ProjectVersion.txt` and use APIs supported by that Editor version. Do not silently upgrade the Editor, packages, scripting backend, or serialization mode.
4. Inspect `Packages/manifest.json` and, when dependency resolution matters, `Packages/packages-lock.json`. Identify the render pipeline, Input System, test framework, Burst, Entities, and other packages relevant to the task.
5. Find the nearest `.asmdef` or `.asmref` files for every changed script. Respect their runtime, Editor, platform, define, and test-assembly boundaries.

## Read the right files

- Read relevant source and assets under `Assets/`, embedded or local packages under `Packages/`, and task-specific settings under `ProjectSettings/`.
- Allow targeted reads of `Packages/manifest.json`, `Packages/packages-lock.json`, `ProjectSettings/ProjectVersion.txt`, render-pipeline settings, build settings, and test configuration.
- Never edit generated `Library/`, `Temp/`, `obj/`, `Obj/`, or `Logs/` content, and do not scan those directories broadly. A targeted read of the exact Editor or test log for the current failure signal is allowed. Avoid generated build output unless the user asks to inspect an artifact.
- Do not edit generated `.csproj` or `.sln` files as the source of truth.
- Read `.meta` files only when GUIDs, imports, moves, references, or asset identity are relevant. When moving or renaming an asset outside the Editor, keep its `.meta` file with it.

Use `rg` and narrow paths instead of scanning the whole project. Adapt to the repository's real layout; do not assume `Assets/_Game/Scripts` exists.

## Implement safely

- Follow established project conventions before applying generic Unity style. Keep namespaces, field naming, nullability, and dependency patterns consistent with adjacent code.
- Prefer private serialized fields and explicit references over repeated scene-wide lookups. Cache required components outside hot per-frame paths.
- Keep runtime code independent of `UnityEditor`. Place Editor-only code in an Editor assembly or guard the dependency appropriately.
- Treat lifecycle order, domain reload behavior, scene unloads, disabled objects, and destroyed `UnityEngine.Object` instances as part of correctness.
- Version-gate APIs such as `Awaitable`, Input System types, render-pipeline APIs, and Entities APIs against the project's Editor and package versions.
- Do not add or reorganize assembly definitions casually. An `.asmdef` changes compilation and dependency boundaries for every script below it.
- Add focused EditMode tests for pure logic and Editor behavior; add PlayMode tests when behavior depends on frames, physics, scenes, or runtime lifecycle.

## Preserve serialized data

- Treat `.unity`, `.prefab`, `.asset`, `.controller`, `.overrideController`, and related text assets as structured Unity serialization, not ordinary YAML or JSON.
- Prefer an existing Editor tool or a narrowly scoped Editor script for structural scene or prefab changes.
- If a direct text edit is necessary, keep the diff minimal, preserve `fileID` and GUID relationships, avoid whole-file reformatting, and inspect the resulting diff for broken references.
- Preserve serialized field data when renaming fields. Use the project's compatible migration pattern, such as `FormerlySerializedAs`, when existing assets must retain values.
- Never regenerate or casually replace `.meta` files for existing assets.

Read [references/unity-advanced.md](references/unity-advanced.md) when the task involves assembly definitions, serialized assets, shaders or render pipelines, Editor tools, profiling, Burst/Jobs, or Entities.

## Verify proportionally

Use the repository's existing CI scripts and commands first. Otherwise, choose the smallest relevant ladder:

1. Inspect the diff and confirm that namespaces, `.asmdef` references, platform guards, and serialized-field changes are coherent.
2. Run the narrowest existing EditMode or PlayMode tests that exercise the change.
3. Compile or import with the exact Editor version from `ProjectVersion.txt` when a compatible Editor and license are available.
4. For scenes, prefabs, shaders, animation, physics, or UI, perform the relevant Editor or player-path check; a C# compile alone is not sufficient.

Generic batch-mode forms are:

```text
"<UnityExecutable>" -batchmode -nographics -projectPath "<absolute-project-root>" -runTests -testPlatform EditMode -testResults "<absolute-results.xml>" -logFile "<absolute-editor.log>"
"<UnityExecutable>" -batchmode -nographics -projectPath "<absolute-project-root>" -runTests -testPlatform PlayMode -testResults "<absolute-results.xml>" -logFile "<absolute-editor.log>"
"<UnityExecutable>" -batchmode -nographics -quit -projectPath "<absolute-project-root>" -logFile "<absolute-editor.log>"
```

Adapt flags to the installed Test Framework and repository scripts. Do not add `-accept-apiupdate` unless an Editor/API migration is intentional. Do not run a second Editor against a project already open elsewhere.

Inspect the process exit code, test result XML, and relevant log errors. Do not treat creation of a results file as proof that tests passed.

If the matching Editor is unavailable, licensing fails, the project is locked by another Editor, or the required platform cannot run, report exactly what was checked and label Unity compilation, tests, or visual verification as not run. Do not substitute `dotnet build` for Unity compilation or claim the change is fully verified.
