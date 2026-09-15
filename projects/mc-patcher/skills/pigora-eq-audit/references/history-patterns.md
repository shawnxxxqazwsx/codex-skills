# History-derived audit priorities

Reviewed local user-task messages within 2026-09-04 01:25:16 UTC through
2026-09-05 01:25:16 UTC (Japan 09-04 10:25:16 through 09-05 10:25:16), including
archived tasks. Conversation reports are reproduction leads; measured artifacts
support only their bound historical versions. No current installed PASS follows
from this review. Duplicate/forked conversations are not independent defects.

| Repeated observation | Audit consequence |
|---|---|
| SPL PQ LF Prop Q: initial repair, later shoulder/fold reports, then Q32–40 reported again | Preserve unresolved interval and every implicated detent; inspect slope/curvature even when magnitude is bounded and monotone |
| Shelford MID then HF narrow anomalies between source anchors; LF siblings also affected | Probe pole neighborhoods and actual audio at localized extrema; a huge gain grid cannot compensate for sparse frequency sampling |
| Shelford extreme MID cut: small tail staircase despite magnitude gate success | Negative extremes and exterior slope are separate checks; do not chase raster texture as a required product feature |
| ngTubeEQ Prop Q appeared ineffective, then Gain travel and LMF smoothness were questioned repeatedly | Distinguishing non-neutral switch states, gain-dependent Q tracks, intermediate response checks |
| MBT HF Shelf: frequency travel, 24 kHz and repeated 12 kHz/11 kHz inflection reports | Shelf plateau/transition tests, frequency tracks and high-frequency mapping seams; never inherit Bell acceptance |
| Rack insertion near Nyquist reported high-cut/phase effects across EQ modules | Empty/neutral/bypass complex-response comparison per shared processing route |
| W492 single-node improvements did not settle continuous-cell behavior; runtime capacity remained separate | Cell-interior probes and separate real-time/installed evidence; fitting progress is not deployment acceptance |

Useful measured historical artifacts (repository-relative):

- `.codex/shelford-mid-audit-20260905/AUDIT.md`: 0.382 Hz-scale pole feature
  between anchors about 44.60 Hz apart; endpoint gain could hide the defect.
- `.codex/shelford-hf-repair-20260905/REPORT.md`: HF installed-audio spike,
  MID cut tail, and LF sibling probes; keep version-specific claims separate.
- `tests/fixtures/hardware_eq/spl_pq/shape_repair_v1/REPORT.md`
- `tests/fixtures/hardware_eq/spl_pq/propq_repair_v2/REPORT.md`
- `tests/fixtures/hardware_eq/spl_pq/lf_propq_repair_v3/review-final.json`:
  derivative flags explicitly remained diagnostic, not all-Q acceptance.

Conversation identities for finding exact user sequences:
SPL `01a06dd5-dabf-7512-92d9-842530564d14`;
Shelford `01a06de9-513f-7490-9322-07acca39447b`;
ngTubeEQ `01a06ba2-5750-7333-acd8-7c9123028145`;
MBT `01a06ba3-c828-7923-8aa9-b6af2466a1c3`;
Rack `01a06cb9-052c-7322-b485-5bc1ce5f898c`;
W492 `01a06ed1-95a6-7c91-874a-cfa4a33b09d4`.

Use one representative per distinct failure mechanism, then expand only where
its recorded dependency warrants it. Do not copy historic numeric thresholds
or guessed screenshot settings into a new acceptance contract.
