## Unity project workflow

### Project facts

- Unity Editor: `{{UNITY_EDITOR_VERSION}}`
- Render pipeline: `{{RENDER_PIPELINE}}`
- Relevant packages: {{RELEVANT_PACKAGES}}
- Runtime assemblies: {{RUNTIME_ASSEMBLIES}}
- Editor and test assemblies: {{EDITOR_AND_TEST_ASSEMBLIES}}

### Working scope

- Read and edit relevant project files under `Assets/`, local or embedded code under `Packages/`, and task-specific settings under `ProjectSettings/`.
- Never edit or broadly scan generated `Library/`, `Temp/`, `obj/`, `Obj/`, or `Logs/` content. A targeted read of an exact current Editor or test log is allowed when diagnosing that failure.
- Treat generated `.csproj` and `.sln` files as outputs, not sources of truth.
- Preserve existing project structure and conventions; do not assume a personal `Assets/` layout.

### Unity code and assets

- Use APIs compatible with the exact Editor and package versions above.
- Respect the nearest `.asmdef` or `.asmref`, including runtime, Editor, test, platform, and define constraints.
- Keep runtime assemblies free of `UnityEditor` dependencies.
- Treat scenes, prefabs, ScriptableObjects, controllers, and other Unity text assets as structured serialized data.
- Preserve GUID and `fileID` relationships. Move an asset with its `.meta`; never regenerate an existing asset's `.meta` casually.
- Keep direct serialized-text edits narrow and verify them by importing or opening the asset in the matching Unity Editor when available.

### Validation

- Compile/import: {{COMPILE_OR_IMPORT_COMMAND}}
- EditMode tests: {{EDITMODE_TEST_COMMAND}}
- PlayMode tests: {{PLAYMODE_TEST_COMMAND}}
- Build or visual check: {{BUILD_OR_VISUAL_CHECK}}
- If the matching Editor, license, target platform, or visual path is unavailable, report that limitation and do not claim Unity verification passed.
