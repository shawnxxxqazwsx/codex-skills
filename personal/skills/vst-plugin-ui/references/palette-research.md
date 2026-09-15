# Autonomous Palette Research and Transfer

Use this workflow when the user asks the agent to find visual references,
choose a palette, improve taste autonomously, or adapt current online design
cases to an audio plug-in or host. The goal is evidence-informed synthesis, not
a scraped mood board or a clone of one competitor. Search beyond audio software:
professional tools, design systems, websites, editorial work, industrial
products, architecture, fashion, and visual culture can all contribute when the
transfer is explicit and useful.

## 1. Fingerprint the existing surface

Inspect the real UI before searching. Capture the target page at a
representative size and record:

- product class, primary job, and locked functional zones;
- current surface ladder: shell, panel, raised plate, recess, border;
- text, control, selection/focus, semantic status, and meter roles;
- dominant temperature, approximate OKLCH lightness/chroma relationships,
  accent area, and the adjacency where the new palette must fit;
- brand or semantic colors that are fixed, and whether the scope is one control
  island or a full visual system.

Do not search for a generic “best UI palette.” Turn the fingerprint into a
visual problem such as “warm light host shell + modular graph + restrained
category identity” or “dark spectral work surface + one direct-manipulation
accent.”

## 2. Research with a wide-scan and deep-shortlist funnel

Browse when the user requests online/current cases, delegates visual direction,
or the local reference library is insufficient. Search by both product problem
and visual property. A graph host may need queries for node navigation and port
states, but also for warm neutral editorial systems, compact data typography,
industrial labeling, or restrained motion.

### Wide scan

Start with roughly 12–20 candidates across four or more source families. These
numbers are starting points, not quotas; stop when new cases repeat an existing
move. Include only families that can answer a concrete part of the brief:

1. **Direct operational analogues:** audio plug-ins, DAWs, modular graphs, patch
   bays, and consoles. Use these to ground workflow, density, states, and
   musician expectations.
2. **Adjacent professional tools:** 3D, video, CAD, scientific visualization,
   data analysis, mapping, and developer tools. Use these for dense hierarchy,
   navigation, graph editing, inspectors, and long-session ergonomics.
3. **Design systems:** current official systems such as Material, Spectrum, or
   Carbon. Use these for semantic roles, token architecture, interaction states,
   contrast, and theme construction—not for a generic component skin.
4. **Websites, editorial, and brand systems:** product sites, studios,
   publications, cultural institutions, fashion, architecture, and portfolios.
   Use these for palette rhythm, type pairing, negative space, image treatment,
   transitions, and a contemporary visual voice.
5. **Physical and industrial products:** instruments, test equipment, broadcast
   hardware, cameras, vehicles, furniture, packaging, and signage. Use these for
   tactile hierarchy, material transitions, labeling, and accent placement.
6. **Art and visual culture:** print, exhibition graphics, film titles,
   photography, painting, and generative art. Use only when a concrete motif,
   composition, temperature, or motion principle transfers to the product.

Curated galleries and social feeds are discovery indexes, not acceptance
evidence. Use their filters to broaden the scan, then open the creator's or
product's real page whenever possible.

### Deep shortlist

Reduce the scan to roughly 4–6 cases. Do not let more than two cases from the
same visual family dominate. Include a close operational analogue, a strong
visual/material analogue, and at least one useful counterexample. Prefer:

1. current official product pages, manuals, release pages, and press assets that
   show the real shipping UI;
2. official videos or documentation that expose live, idle, selected, bypassed,
   and error states;
3. independent practitioner or award/editorial material for critique and use
   context;
4. galleries and social posts for inspiration only, never as the sole evidence
   of usability, accessibility, or product identity.

Open every case used in the decision and inspect the actual image or rendered
page, not only search snippets or alt text. Record product/version/date, URL,
view/state shown, transferable relationship, and what must not be copied.
Screenshots may be compressed, colour-managed, graded, or photographed; sampled
pixels are approximate inspiration unless an official token specification is
available.

### Transfer by layer, not by resemblance

| Source family | May influence | Must not dictate |
|---|---|---|
| Direct and adjacent professional tools | Density, graph behavior, navigation, state visibility, inspector patterns | Another product's brand skin or exact workflow |
| Design systems | Semantic tokens, surface roles, focus/hover/disabled states, contrast strategy | A generic web component appearance |
| Websites and editorial systems | Colour rhythm, typography, spacing cadence, composition, material, transition and motion language | Marketing information architecture, CTA hierarchy, oversized heroes, scroll gimmicks, or sparse desktop ergonomics |
| Industrial and physical products | Affordance, tactile depth, labeling, accent placement, durable material cues | Tiny hardware controls, decorative realism, or fake mechanical constraints |
| Art and visual culture | One motif, temperature relationship, composition, texture, or motion principle | Operational hierarchy or interaction rules |

Do not average all references into a tasteful but anonymous middle. Cluster the
scan into coherent visual families, choose one family as the foundation, then
borrow at most one or two contrasting moves that reinforce the product's
signature.

## 3. Extract relationships, then synthesize

Do not lift a whole palette from one product or website. Extract relational
decisions:

- relative lightness between shell, module, header, recess, and border;
- where chroma is spent and the approximate accented area;
- warm/cool tension and whether hue identifies type, status, or selection;
- how wires, meters, values, and focus remain distinct at the same time;
- how the palette behaves in idle, active, selected, disabled, and clipped
  states.

When the brief extends beyond colour, also record type scale and numeral style,
spacing cadence, corner/edge character, shadow or light behavior, image/texture
treatment, and motion timing. Keep each extracted property attached to its
source and intended UI layer.

Synthesize those relationships around the existing product identity. Preserve
working visual DNA unless the task explicitly requests a full rebrand. Build
complete role-token candidates—never just a base hex—including raised/header,
border, ink/dim, control track/body/handle, hover/pressed/focus, semantic status,
and meter roles. Record working OKLCH values and final gamut-checked sRGB/ARGB.

Generate a small controlled set on the actual surface:

- **Native fit:** minimal departure, strongest continuity with current chrome.
- **Reference-led:** clearer transfer of the best researched relationships.
- **Signature:** one bolder but still product-specific aesthetic move.

These are decision roles, not mandatory styles. Remove redundant candidates.

## 4. Select autonomously without faking objectivity

When the user delegates the choice, rank the candidates and choose the strongest
passing direction without asking them to supply a color. Judge:

- coherence with the existing shell, geometry, and subject world;
- visual hierarchy and scanability at realistic density;
- text/control contrast and non-hue state discrimination;
- separation of brand accents, semantic status, routing, and meter information;
- distinctiveness without trademark, exact-artwork, or competitor-skin copying;
- implementation feasibility, renderer cost, and behavior at minimum size.

Keep the current palette as the baseline candidate. If it passes the gates and
the researched alternatives do not materially improve hierarchy, coherence, or
identity, retain it and report that decision instead of manufacturing visual
churn. Autonomous judgment means owning the no-change decision too.

Accessibility, missing states, or broken meter/route semantics are hard
failures, not scores that visual novelty can average away. Use design-lead
judgment for the remaining aesthetic tradeoffs and state why the selected
direction fits this product better than the alternatives.

## 5. Apply and prove the selected palette

If implementation is in scope, apply the selected complete token set without
pausing for a hex-value handoff. For WebUI, audition through temporary token
overrides or a Theme Lab first, then write the selected production tokens once.
Do not restructure locked zones, reinterpret controls, or recolor established
semantic/meter roles unless that is explicitly in scope and independently
validated.

Produce an audit trail:

```text
Current palette fingerprint:
Wide-scan source matrix (domain / useful layer / direct link):
Deep shortlist and direct links:
Transferable relationships / forbidden copying:
Candidate role-token sets:
Selected direction and rejected alternatives:
Before/after real-surface captures:
Contrast, grayscale, state, minimum-size, and source-to-bundle checks:
Implementation and deployment scope:
```

Follow [color.md](color.md) for perceptual construction, controlled audition,
preview provenance, contrast, and final handoff. Follow project-specific build
and deployment rules separately. Autonomous palette selection does not grant
permission for unrelated source changes, external publishing, or deployment.
