---
name: web-research
description: >-
  Professional multi-source web research with verified live URLs and papers
  (fetch before cite). Auto-apply for technical docs, APIs, papers, product
  compare, market pricing, policy tables, obscure-entity/media hunts, or when
  the user attaches @web-research / says 调研 / 全面调研 / look up sources. For
  OpenAI and Codex product questions, use the official-source `openai-docs`
  workflow instead.
---

# Web Research

专业向联网调研。目标：**准、全、可复核** —— 结论可跟、依据可点开、论文/链接须经抓取确认。  
**错误正例差过「未找到」。禁止编造 URL / DOI / 文献。**

范围：**技术文档、学术论文、产品/政策/行情、专业对比与溯源**。

## When / scale

| Need | Depth |
|------|--------|
| 单事实、报错、官方价格、API 签名 | **Standard**：定位并抓取能直接支持结论的主来源；有冲突或歧义再补检索 |
| 对比、行情、政策表、全面调研 | **Deep**：按独立子问题和冲突扩展来源，直到证据覆盖或明确停止 |
| 论文 / 学术主张 | **Academic**：优先 DOI / arXiv / 出版社页；见 [reference.md](reference.md#academic--papers) |
| 旧应用 / 实机视频 / 下架软件 | **Obscure**：身份锚定 → 验证 → 负结论 OK；见 reference |

其他 active skill 可以约束呈现长度或领域判断，但不能降低支持当前
结论所需的来源验证。领域 skill 负责专业方法，本 skill 负责检索与引用证据。

## Workflow

1. **Classify** — 时效？版本？名称撞车？要论文还是产品页？
2. **Anchors** — 实体全名 + 消歧项（开发商 / ID / 作者 / 年份）；宽题拆 2–4 子问题
3. **Search rounds**（按需叠加）  
   - A 官方 / 主键（`site:`、商店 API、机构站）  
   - B 实务（GitHub、论坛、SO、区域站）  
   - C 学术（Scholar 线索 → DOI/arXiv 落地页）  
   - D 补洞（冲突、过时、SEO 污染 → 更窄 query）
4. **Verify then cite** — 见下表；失败则剔除
5. **Synthesize** — 冲突如实写；缺口进「未覆盖」

每轮后自问：*还有什么未知？*  
**停止**：子问题已答，或两权威源一致，或锚点已穷尽 → **未找到**，不塞近似结果。

## Query craft

| Bad | Good |
|-----|------|
| `Unity input` | `Unity 6 Input System Mouse.current wasPressedThisFrame site:docs.unity3d.com` |
| `transformer paper` | `Attention Is All You Need Vaswani 2017 site:arxiv.org` |
| `末日列车 视频` | `"Doomsday Express HD" Warp Dreams gameplay` + App ID |

Rules：产品+版本+年份；官方用 `site:`；报错用原文；撞名用引号+开发商/ID；英文扩召回，用用户语言作答。模板见 [reference.md](reference.md)。

## Verify before cite（强制）

| 类型 | 最低验证 |
|------|----------|
| 任意 URL 进「依据」 | **Fetch 成功**；404/空页/拦访 → **不引用** |
| 数字 / 政策 / 价格 | 抓取主键页；禁止仅信搜索 Synthesis |
| 论文 | 打开 **DOI / arXiv / 出版社页**；核对题名、作者、年份 |
| 软件是否在架 | 商店/API lookup；0 结果 = 已下架 |
| 视频 / 实机 | 打开媒体；标题≠内容时排除 |
| 身份同一产品 | ≥2 锚点；仅标题不够 |

未 fetch 通过的不得写入依据。无法验证 → 标「未验证」或移出，勿假装百分百。

## Source hierarchy

1. 官方文档 / changelog / 标准与法规  
2. 官方博客、商店页、机构发布  
3. 论文：DOI、arXiv、学会/出版社  
4. Maintainer GitHub  
5. 员工论坛回复  
6. 社区长文（须用 1–4 核对）  
7. SEO 聚合 — **最低**，不作唯一依据  

技术实现主张只依赖官方文档、标准或原始研究论文；社区来源只能用于
发现线索或描述社区经验，不能替代主来源。

## Output

```markdown
## 结论
[直接回答；调研/对比可用表。否定结论说明已试范围]

## 依据（均已抓取确认）
- [标题](完整URL) — 支持哪条要点（论文加：作者, 年份, DOI/arXiv）
- …

## 易混淆 / 已排除（撞名或假阳性时必填）
- [标题](URL) — 排除原因

## 未覆盖 / 不确定
- …

## 建议下一步（可选）
- …
```

行情/二手：见下方 + [reference](reference.md#market--second-hand-pricing)。

## Market / 二手

1. 型号谱系先于价格  
2. 官零售价锚定 + 日期  
3. 按地区搜成交/挂牌  
4. 标注 Sold / Asking / Dealer / MSRP  

强制：单只 vs 一对、货币+月份、成色；无列表 URL 不引用。

## Anti-patterns

- 凭记忆答时效/需引用的问题  
- 只搜一次或只贴搜索摘要  
- **编造** DOI/链接  
- 未打开就引用视频/论文  
- 用近似结果充「依据」  
- 二手：比价爬虫当成交；新价混进二手表不标注  
## Domain extras

- **Unity**：项目版本 + `docs.unity3d.com`  
- **旧游戏/影像**：reference「Obscure entity」  
- **论文**：reference「Academic & papers」  
- 全文模板：[reference.md](reference.md)
