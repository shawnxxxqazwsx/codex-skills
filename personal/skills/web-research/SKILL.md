---
name: web-research
description: >-
  Professional multi-source web research requiring at least three parallel
  research sub-agents plus lead-agent synthesis, with verified live URLs and
  papers (fetch before cite). Auto-apply for technical docs, APIs, papers, product
  compare, market pricing, policy tables, obscure-entity/media hunts, or when
  the user attaches @web-research / says 调研 / 全面调研 / look up sources. For
  OpenAI and Codex product questions, use the official-source `openai-docs`
  workflow instead.
---

# Web Research

专业向联网调研。目标：**准、全、可复核** —— 结论可跟、依据可点开、论文/链接须经抓取确认。  
**错误正例差过「未找到」。禁止编造 URL / DOI / 文献。**

范围：**技术文档、学术论文、产品/政策/行情、专业对比与溯源**。

## Parallel research（强制）

使用本 Skill 执行联网调研时，**主代理必须实际调用至少 3 个独立 sub-agent
并行搜索，主代理不计入这 3 个**。所有深度（包括 Standard 和单事实查询）
均适用；不得以任务简单、已有答案或主代理自行搜索为由省略。

1. **先分工并派发** — 将任务拆成至少 3 个有明确目标的检索方向，并实际
   创建、派发给 3 个不同的 sub-agent（例如使用 `spawn_agent`）。先派发全部
   3 个，再等待结果；各检索任务应并行推进，不得逐个完成后才启动下一个。
   窄题可分别负责主来源定位、独立交叉核对、反证/版本边界/冲突搜索。
   不得为凑数量引入无关议题或低质量来源。
2. **每个子代理都要搜索** — 指定问题范围、实体/版本/日期、来源要求及返回格式。
   每个子代理须实际检索并打开来源，返回结论、已打开的 URL、支持该结论的
   页面证据、适用时间/版本，以及冲突和缺口；确无结果时返回实际查询及失败
   范围。仅做摘要、审阅或改写的代理不计入这 3 个。子代理沿用本 Skill 的
   来源与引用规则，但不递归创建另外 3 个代理；数量要求由顶层主代理履行。
3. **主代理可同步搜索** — 可补洞、查证或独立检索；这些工作均不抵扣子代理数量。
4. **收齐后核验整合** — 主代理必须收集至少 3 名不同子代理的实际检索报告
   （含记录了查询及失败范围的「未找到」报告），
   亲自打开拟用于最终回答的来源，核对其是否支持对应主张。按实体、原始来源
   和主张去重；同源转载不算独立证据。冲突须对照原始证据、日期、版本、地区
   和统计口径判断，不能按代理多数票决定；无法解决时明确呈现分歧与不确定性。
   最后由主代理统一组织结论与引用，不直接拼接子代理答案。
5. **完成门槛** — 主代理保留实际代理标识、分工、搜索调用/查询记录和返回状态，
   确认至少 3 名不同子代理的实际检索报告已收集后才交付完成的调研。
   创建失败或未执行搜索的代理不计数，应及时重派或替换并保持三路并行要求；
   若其他分支均已结束，须重新组织合规的并行检索轮次（可复用原代理补查），
   不得用事后串行补跑冒充三路并行。工具或并发容量无法满足
   时，明确告知未满足本 Skill 的并行要求及原因，不得静默降级后声称已完成。

单个代理的多轮检索、并发搜索请求或 3 个子问题，均不能替代 3 个独立 sub-agent。

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
2. **Anchors & dispatch** — 实体全名 + 消歧项（开发商 / ID / 作者 / 年份）；按上节拆分并派发至少 3 个并行检索方向
3. **Search rounds**（各子代理按需叠加；主代理可同步补检）  
   - A 官方 / 主键（`site:`、商店 API、机构站）  
   - B 实务（GitHub、论坛、SO、区域站）  
   - C 学术（Scholar 线索 → DOI/arXiv 落地页）  
   - D 补洞（冲突、过时、SEO 污染 → 更窄 query）
4. **Collect & verify then cite** — 收集至少 3 名不同子代理的实际检索报告；主代理逐项核验最终引用，见下表；失败则剔除
5. **Synthesize** — 主代理去重、处理冲突并统一交付；缺口进「未覆盖」

每轮后自问：*还有什么未知？*  
**停止**：子问题已答，或两个独立权威来源在相同口径下一致；锚点已穷尽仍无结果 → **未找到**，不塞近似结果。
停止条件只控制各检索方向的深度，不能跳过 3 个子代理的派发、搜索与结果收集。

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
- 仅做单路搜索或只贴搜索摘要  
- **编造** DOI/链接  
- 未打开就引用视频/论文  
- 用近似结果充「依据」  
- 二手：比价爬虫当成交；新价混进二手表不标注  
## Domain extras

- **Unity**：项目版本 + `docs.unity3d.com`  
- **旧游戏/影像**：reference「Obscure entity」  
- **论文**：reference「Academic & papers」  
- 全文模板：[reference.md](reference.md)
