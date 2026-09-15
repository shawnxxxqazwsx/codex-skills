# Unity advanced reference

Load only the sections relevant to the current task.

## Assembly definitions and tests

- Find the closest enclosing `.asmdef`; scripts compile into the closest applicable assembly rather than an arbitrary project-wide assembly.
- Preserve the repository's reference style, including name-based versus `GUID:` references. Verify that every new dependency points in the allowed direction and does not create a cycle.
- Keep Editor code in an Editor-only assembly or folder. Keep runtime assemblies free of `UnityEditor` references.
- Inspect `includePlatforms`, `excludePlatforms`, `defineConstraints`, `versionDefines`, `autoReferenced`, `overrideReferences`, and `noEngineReferences` before changing an assembly.
- Put tests in an existing test assembly when possible. Confirm its Test Assemblies configuration and references to the production assembly.
- Do not create a new `.asmdef` merely to make one compiler error disappear; first determine which assembly should own the code.

## Serialized assets and GUIDs

- Unity text serialization uses object records, local `fileID` values, and external GUID references. A syntactically valid text file can still contain broken Unity references.
- Move an asset and its `.meta` together when the Unity Editor is not performing the move. Never copy an existing `.meta` to create a distinct asset.
- Prefer Editor APIs such as `SerializedObject`, `SerializedProperty`, `PrefabUtility`, `AssetDatabase`, and scene-management APIs for repeatable structural transformations.
- When directly editing a scene, prefab, or ScriptableObject asset, avoid changing unrelated ordering, line endings, anchors, or importer data. Reopen/import with Unity before claiming success.
- When changing serialized field names or types, plan data migration explicitly. A successful C# compile does not prove existing assets retained their values.

## Shaders and render pipelines

- Identify Built-in, URP, HDRP, or a custom render pipeline from `Packages/manifest.json` and the relevant graphics and quality settings before choosing shader APIs.
- Match the project's pipeline and package version. Do not port to Shader Graph or rewrite shader language solely as cleanup.
- Keep shader keyword and variant growth intentional. Validate material compatibility, pass names, render queues, instancing, and platform targets affected by the change.
- Use visual or capture-based verification for rendering changes. Batch compilation alone cannot establish visual correctness.

## Editor tooling

- Keep Editor tools out of player assemblies and avoid runtime dependencies on `UnityEditor`.
- Make repeated asset operations idempotent, undoable where interactive, and explicit about dirtying and saving assets or scenes.
- Avoid broad `AssetDatabase.Refresh` or whole-project reimports when a narrower import is sufficient.
- Treat batch-mode execution as unattended: fail with a non-zero exit code, write actionable logs, and avoid modal dialogs.

## Performance, Jobs, Burst, and Entities

- Profile before optimizing. Distinguish CPU, render-thread, GPU, GC, physics, loading, and synchronization bottlenecks.
- Avoid avoidable allocation, lookup, logging, and string work in measured hot loops such as `Update`, `FixedUpdate`, render callbacks, and jobs.
- Preallocate or pool only where lifetime and reset behavior are clear. Do not introduce global pools without ownership and teardown rules.
- Verify Jobs, Burst, Collections, Mathematics, and Entities APIs against the package versions locked by the project; their APIs are version-sensitive.
- Preserve thread-safety and container lifetime rules. Do not access Unity objects from worker jobs unless the applicable API explicitly supports it.

## Validation details

- Prefer project-provided wrappers because they may select the correct Editor, platform, license strategy, filters, and result paths.
- Use EditMode tests for deterministic logic and Editor APIs. Use PlayMode or player tests for frame-driven, physics, scene, input, or lifecycle behavior.
- Omit `-nographics` when the validation requires a graphics device, rendering, or GPU-backed functionality.
- Capture an explicit log path and test result path outside generated project directories. Check both the exit status and parsed test failures.
- When compilation is the only required check, a batch import with `-quit` can expose compiler and asset-import errors, but it does not replace task-specific tests.

