# Web Research — Reference

专业检索补充材料。

## Query templates

```
{Product} {Version} {Feature} official documentation site:{official-domain}
{Product} {Version} {Feature} changelog OR release notes {Year}
{Error message exact string} {Product} {Version}
{Product} vs {Alternative} {Year} comparison {specific criterion}
"{Paper title}" {First author} {Year} (site:arxiv.org OR DOI)
{Topic} review OR survey {Year} filetype:pdf site:arxiv.org
site:forum.cursor.com {topic}
site:discussions.unity.com {topic}
site:github.com {org}/{repo} {issue keyword}
site:scholar.google.com {topic}  → then open the real DOI/arXiv from the hit
```

### Cursor / Unity / Models

| Topic | Example query |
|-------|----------------|
| Pricing | `Cursor Pro Plus Ultra included API usage site:cursor.com/docs` |
| Unity API | `Unity 6 {ClassName} site:docs.unity3d.com` |
| Model pricing | `{Provider} {Model} pricing per million tokens site:{official-domain}` |

### Academic

| Topic | Example query |
|-------|----------------|
| Known paper | `"{Exact title}" {author} {year} site:arxiv.org` |
| By DOI | `https://doi.org/{doi}` then fetch |
| Survey | `{field} survey OR "systematic review" {year}` then land on publisher/arXiv |

### Consumer / second-hand (audio example)

| Topic | Example query |
|-------|----------------|
| 国行 MSRP | `{Model} site:store.kef.cn OR site:kef.com` |
| 港二手 | `{Model} 二手 site:post76.hk OR site:review33.com` |
| 欧美二手 | `{Model} used pair site:audiogon.com OR site:ebay.com` |

---

## Academic & papers

```
[ ] Prefer primary: arXiv abs/pdf, doi.org, ACM/IEEE/ACL Anthology, journal page
[ ] Fetch landing page — confirm title, authors, year
[ ] In 依据: Title (Authors, Year) + URL + DOI or arXiv id
[ ] Never invent citations; reject broken DOI / SEO paper farms
[ ] Preprints: label preprint; don't invent venue
[ ] Quotes: prefer full text; else verified abstract only + say so
```

Trusted: `arxiv.org/abs/`, `arxiv.org/pdf/`, `doi.org/`, `aclanthology.org/`, `openreview.net/`.

---

## URL verification (cite rule)

依据中的链接必须在本回合：

1. 经 fetch / browser / API 打开，且  
2. 非 404/停放页，且  
3. 页面身份与声称一致  

否则省略，或写入未覆盖为「候选未验证」。

---

## Market & second-hand pricing

```
[ ] Model matrix first
[ ] Official MSRP (pair, currency, date)
[ ] Regional + global listings; classify sold | asking | dealer | MSRP
[ ] Reject BigGo/Feebee/ZOL as 成交; reject Synthesis-only prices
[ ] Band (low–high), not false precision
```

| Region | Domains |
|--------|---------|
| CN/HK | `erji.net`, `post76.hk`, `review33.com`, `dcfever.com` |
| Global audio | `audiogon.com`, `ebay.com`, `hifizero.com` |

---

## Official domains

| Area | Domains |
|------|---------|
| Cursor | `cursor.com`, `forum.cursor.com` |
| Unity | `docs.unity3d.com`, `discussions.unity.com` |
| Anthropic / OpenAI | `docs.anthropic.com`, `platform.openai.com` |
| Papers | `arxiv.org`, `doi.org`, `aclanthology.org`, `openreview.net` |

---

## Multi-step checklist

```
[ ] Follow SKILL.md Parallel research: at least 3 independent search sub-agents; lead excluded
[ ] Dispatch all 3 before waiting; search tasks run in parallel
[ ] Collect reports from 3 different search sub-agents, including documented no-result reports
[ ] Identity anchors if name collision
[ ] Official → practical → academic as needed
[ ] Lead opens and verifies every final cited URL
[ ] Media: mid-frame before cite
[ ] Lead deduplicates claims and sources, resolves conflicts from evidence, and synthesizes
[ ] Conflicts explicit; near-misses → 易混淆 only
[ ] Record agent IDs, roles, query records and returns; disclose any unmet parallel requirement
```

---

## Obscure entity & media hunts

```
[ ] EN/CN title, developer, App ID, year, platform
[ ] Unique tokens + exclusion list
[ ] Registry lookup; media + region rounds
[ ] Verify frames; none → 未找到
```

```
"{Exact Title HD}" (gameplay OR trailer) {Developer}
itunes.apple.com/lookup?id={AppID}
"{Exact Title}" (archive.org) {Developer}
```

---

## Integration

- Active presentation guidance may shorten the answer, but must not remove evidence needed for the claims made.
- For Unity documentation, include the inspected project version in queries.
- When a domain skill is active, let it own specialist judgment while this workflow verifies current source URLs.
- For a handoff, preserve verified URLs, access dates, and the exclusion list.
