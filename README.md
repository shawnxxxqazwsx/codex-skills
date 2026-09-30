# Codex Skills

个人与 mc-patcher 项目 skills 的公开同步仓库。

## 目录

- `personal/skills/`：24 个个人 skills。
- `projects/mc-patcher/skills/`：22 个项目 skills。
- `sync-manifest.json`：每份 skill 的文件清单与 SHA-256。
- `tools/sync_skills.py`：显式运行的本地导出工具，默认仅预览。

共 30 个不同 skill 名称、46 份副本。重复名称保留各自作用域，尤其是项目专属的 Chlora 配色规则。系统 skills、插件缓存、个人记忆、任务历史、音频素材和 mc-patcher 产品源码不在此仓库中。

## 使用

选择 `personal/skills/<name>` 中需要的完整目录，放入个人 Codex skill 目录（通常为 `~/.codex/skills/<name>`）。先比较已有副本，保留本地修改。

项目 skills 应在对应 mc-patcher checkout 的 `.agents/skills/` 中使用。部分技能依赖该项目的 `AGENTS.md`、构建工具、数据或真实 DAW；仅下载 skill 不会提供这些依赖，也不会自动授权部署或硬件操作。

`<PROGRAM_STEMS_SOURCE>`、`<PROGRAM_MIX_SOURCE>` 和 `<CRYPTO_RESEARCH_OUTPUT>` 是公开副本中的路径占位符；执行相关采集流程前，在本机配置并确认实际素材或研究输出目录。导出只替换公开副本，不改动源 skill。

## 手动同步

在此仓库目录运行，替换项目路径：

```sh
python3 tools/sync_skills.py \
  --personal-root "$HOME/.codex/skills" \
  --project-root /path/to/mc-patcher
```

确认预览后加 `--write` 更新本地仓库。脚本只管理上述两个 skill 子树以及 manifest；会移除 manifest 中已不存在于源目录的文件，不清理其他文件。它拒绝符号链接、未经审查的文件类型、残留个人 home 路径和常见凭证格式。文本资源接受 Markdown、Python、YAML、JSON、TXT、HTML、JavaScript、Shell 和 LICENSE。PNG/JPEG/GIF/WebP/MP4 仅允许已审查的 lieflat-charts、motion-web、threejs 示例资源目录，并检查格式签名及嵌入文本；单文件上限 50 MiB。导出保留源文件的可执行属性。

同步后检查差异、运行相应 skill 验证，再自行提交和推送。没有后台同步或自动推送任务。

## 验证范围

首次发布包含 skill 格式与本地引用检查、Python/YAML/JSON 解析、MusicXML 比较器的针对性回归。未重新执行 DAW、Max、Unity、硬件采集、训练或部署流程。外部链接与依赖版本应在实际使用时重新核实。

## 2026-09-30 同步验证

新增 chlora-operation、crypto-research-review、lieflat-charts、motion-web、p5js、snow-d3、threejs，保留随附模板、示例资源与原始许可证。各 skill 适用自己的许可条款；lieflat-charts 附带 PolyForm Noncommercial 1.0.0。

本次检查导出隐私边界、Python/YAML/JSON 解析和全部 569 个文件哈希。严格 Codex 元数据检查 44/46 通过；p5js 的 author/platforms/version 和 snow-d3 的 argument-hint 属于原始第三方扩展字段，保持原样，尚未通过该检查。文本换行统一为 LF，保留源 Markdown 的格式与行尾空白。没有重新认证 skill 描述中的历史研究结果或运行验收。运行 `python3 -m unittest discover -s tools -p "test_*.py"` 可检查同步工具的导出边界。
