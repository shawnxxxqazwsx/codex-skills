# Codex Skills

个人与 mc-patcher 项目 skills 的公开同步仓库。

## 目录

- `personal/skills/`：18 个个人 skills。
- `projects/mc-patcher/skills/`：21 个项目 skills。
- `sync-manifest.json`：每份 skill 的文件清单与 SHA-256。
- `tools/sync_skills.py`：显式运行的本地导出工具，默认仅预览。

共 23 个不同 skill 名称、39 份副本。重复名称保留各自作用域，尤其是项目专属的 Chlora 配色规则。系统 skills、插件缓存、个人记忆、任务历史、音频素材和 mc-patcher 产品源码不在此仓库中。

## 使用

选择 `personal/skills/<name>` 中需要的完整目录，放入个人 Codex skill 目录（通常为 `~/.codex/skills/<name>`）。先比较已有副本，保留本地修改。

项目 skills 应在对应 mc-patcher checkout 的 `.agents/skills/` 中使用。部分技能依赖该项目的 `AGENTS.md`、构建工具、数据或真实 DAW；仅下载 skill 不会提供这些依赖，也不会自动授权部署或硬件操作。

`<PROGRAM_STEMS_SOURCE>` 和 `<PROGRAM_MIX_SOURCE>` 是公开副本中的路径占位符；执行相关采集流程前，在本机配置并确认实际素材目录。导出只替换公开副本，不改动源 skill。

## 手动同步

在此仓库目录运行，替换项目路径：

```sh
python3 tools/sync_skills.py \
  --personal-root "$HOME/.codex/skills" \
  --project-root /path/to/mc-patcher
```

确认预览后加 `--write` 更新本地仓库。脚本只管理上述两个 skill 子树以及 manifest；会移除 manifest 中已不存在于源目录的文件，不清理其他文件。它拒绝符号链接、未经审查的文件类型、残留个人 home 路径和常见凭证格式。当前只接受 Markdown、Python、YAML、JSON、TXT；新增图片等资源需先扩展审核规则。

同步后检查差异、运行相应 skill 验证，再自行提交和推送。没有后台同步或自动推送任务。

## 验证范围

首次发布包含 skill 格式与本地引用检查、Python/YAML/JSON 解析、MusicXML 比较器的针对性回归。未重新执行 DAW、Max、Unity、硬件采集、训练或部署流程。外部链接与依赖版本应在实际使用时重新核实。
