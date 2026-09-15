# Handoff templates

Use the language of the user's current request. Keep headings recognizable but
adapt fields to the work; omit sections that are truly inapplicable rather than
filling them with boilerplate. If no required work remains, mark the task
complete and omit the next-action and new-task-instruction sections in either
template; a completed brief does not authorize new work.

## Contents

- [Generic task handoff](#generic-task-handoff)
- [Unity task handoff](#unity-task-handoff)
- [Quality checks](#quality-checks)

## Generic task handoff

```markdown
# 交接 · [项目或主题] · [YYYY-MM-DD]

## 当前状态
[一段话：目标、已到达的状态、准确停点、用户最后要求]

## 目标与范围
- **目标**：
- **范围内**：
- **明确不做**：

## 已完成
- [x] [结果，而不是工具调用]

## 进行中 / 未解决
- [ ] [现象、剩余工作、复现或验证方式]
- **阻塞**：[无 / 精确条件与所需输入]

## 关键决策
| 决策 | 原因 | 放弃或未选方案 |
|---|---|---|
| … | … | … |

## 相关文件 / 外部状态
| 路径或对象 | 当前状态 / 改动 | 注意 |
|---|---|---|
| `relative/path` | … | 未提交 / 用户原有改动 / 外部 ID 等 |

## 仓库与任务状态
- **项目 / 工作区**：
- **分支 / worktree**：
- **未提交状态**：
- **Codex Goal**：[无 / objective、status、证据与剩余项]

## 验证
- **已运行**：`command` → ✅ / ❌（关键结果）
- **手工验证**：
- **未运行 / 未确认**：

## 假设与风险
- **已验证事实**：
- **待验证假设**：
- **风险 / Gotchas**：

## 立即下一步
1. …
2. …
3. …

## 新任务首条指令
[一句可执行指令，包含第一步所需的项目相对路径和验收点]

---
交接结束 · 由 session-handoff 生成
```

## Unity task handoff

Use this template only for work that actually carries Unity state. Include
serialized scene or prefab overrides because they can supersede C# defaults.

```markdown
# 交接 · [Unity 项目] · [YYYY-MM-DD]

## 1. 当前状态
[一段话：当前里程碑、功能状态、准确停点、用户最后反馈]

## 2. 目标与范围
- **目标**：
- **范围内**：
- **明确不做**：

## 3. Unity 环境
- **Unity 版本 / 渲染管线**：
- **主场景**：
- **相关 Scene / Prefab / ScriptableObject / Volume**：
- **Packages / ProjectSettings 变化**：
- **Input / 渲染 / 平台备注**：

## 4. 已完成
- [x] [用户可观察的功能结果]

## 5. 进行中 / 未解决
- [ ] [现象 + 精确复现步骤]
- **阻塞**：[无 / 条件]

## 6. 关键决策
| 决策 | 原因 | 放弃或未选方案 |
|---|---|---|
| … | … | … |

## 7. 文件与序列化状态
| 项目相对路径 | 改了什么 | 注意 |
|---|---|---|
| `Assets/.../Foo.cs` | … | partial / Editor-only 等 |
| `Assets/.../Game.unity` | Inspector 字段 = 值 | 场景实例覆盖代码默认值 |
| `Packages/manifest.json` | … | 包版本 / 兼容性 |
| `ProjectSettings/...` | … | 平台或项目级影响 |

### 逻辑 / 表现 / Editor
- **逻辑**：状态机、输入、规则、运行时验证
- **表现**：Mesh、材质、颜色、动画、相机、后处理
- **Editor / 序列化**：Inspector、Scene、Prefab override、SO 数据

## 8. 仓库与 Codex 状态
- **项目 / 工作区**：
- **分支 / worktree**：
- **未提交状态**：
- **Codex Goal**：[无 / objective、status、证据与剩余项]

## 9. 坑、假设与风险
- **Gotchas**：
- **待验证假设**：
- **用户原有改动**：

## 10. 编译与测试
- **编译**：✅ / ❌ / 未测（命令或 Unity 状态）
- **Edit Mode**：✅ / ❌ / 未测
- **Play Mode**：✅ / ❌ / 未测
- **手工复现**：✅ / ❌ / 未测
- **未覆盖平台 / 场景**：

## 11. 立即下一步
1. …
2. …
3. …

## 12. 新任务首条指令
[第一件事 + 项目相对路径 + 验收方式]

---
交接结束 · 由 session-handoff 生成
```

## Quality checks

Before delivering either template, confirm:

- The stopping point and first next action are unambiguous, or the brief
  explicitly states that the task is complete and no action remains.
- Completed items describe outcomes, not searches or tool calls.
- Test status distinguishes pass, fail, and not run.
- Paths are project-relative and identify the relevant symbols or serialized
  objects when needed.
- Pre-existing user changes are not presented as task changes.
- Rejected approaches include enough rationale to prevent repetition.
- Facts and assumptions are separated.
- No credential, secret, large log, or unnecessary code block is included.
- A Unity handoff covers relevant `Assets/`, `Packages/`, and
  `ProjectSettings/` changes; it does not assume all work lives under `Assets/`.
- `.meta` files are mentioned when their GUID or asset relationship matters,
  but their full contents are not pasted.
