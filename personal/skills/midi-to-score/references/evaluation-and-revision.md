# Evaluation and revision

Read this reference when the score contains ambiguous performed rhythm, polyphonic or cross-staff writing, a renderer round-trip, or more than one revision pass.

## Keep the artifact ladder explicit

Treat these as separate layers:

1. original MIDI/audio and extracted context: immutable evidence;
2. score plan and interpretation ledger: AI-authored musical decisions;
3. MusicXML: portable notation semantics;
4. renderer-native score: layout and renderer-specific adjustments;
5. final PDF and optional playback export: performer-facing deliverables.

Do not let a later layer silently become the only source of a musical decision. The score plan remains authoritative for rhythm, pitch, voice, staff, expression, and transposition. A native score may own layout-only changes. If a native edit changes notes, durations, voices, tuplets, articulations, or transposition, backport it to the plan/MusicXML or record the unresolved divergence before delivery.

## Interpretation ledger

Use JSONL or a compact table. One entry covers one coherent decision, not every note:

```json
{"parts":["Piano"],"bars":"35-40","dimension":"rhythm_voice","source_evidence":"two interleaved onset lattices","alternatives":["fragmented mixed tuplets","7:6 quarter-pulse streams"],"decision":"7:6 quarter-pulse streams","intentional_deviation":"infer four missing slots to preserve the continuous gesture","status":"accepted"}
```

Required fields are affected parts/bars, dimension, source evidence, alternatives when genuinely ambiguous, decision, intentional deviation or `none`, and status. Useful dimensions are:

- meter and barline;
- pitch and enharmonic spelling;
- duration, rest, tie, and tuplet;
- stream, voice, hand, staff, stem, and beam;
- articulation, slur, dynamics, pedal, and technique;
- renderer/layout;
- submission packaging.

This ledger is the loss report between performed data and readable notation. It should make inferred, omitted, sustained, redistributed, or simplified material auditable without demanding literal MIDI fidelity.

## Revision loop

1. Save a baseline score plan, MusicXML, renderer-native file, and PDF before a substantive rewrite.
2. Rank defects by performer impact. Fix one coherent notation model or at most three closely related defects per pass.
3. Rebuild, parse, compare semantics, render, and inspect the affected pages. Then run the representative playback check.
4. Accept the pass only if its target dimension improves without a new regression in another dimension. Preserve the rejected artifact long enough to explain the comparison.
5. Stop when the requested acceptance condition is met, evidence is genuinely ambiguous and documented, or the next change would merely chase a generic feature count or aesthetic score.

Treat automated profiles and corpus statistics as suggestions. They may identify missing dynamics, unusual density, or structural outliers, but they do not authorize adding markings or rewriting music without a phrase-level reason. More iterations are not inherently better.

## Notation-dimension audit

Do not collapse quality into note accuracy. Audit and report these dimensions separately:

| Dimension | Objective checks | Musician-facing check |
|---|---|---|
| Structure | requested range, part order, meter, barlines | form and pulse are immediately apparent |
| Pitch | sounding/written pitch, transposition, spelling | lines and harmony read naturally |
| Rhythm | durations, rests, ties, tuplets | beats and groups can be counted without MIDI |
| Voice | voice/staff IDs, stems, beams, hand groups | each line or hand can be traced continuously |
| Expression | dynamics, slurs, pedal, techniques | markings are sparse, specific, and executable |
| Layout | page size, systems, collisions, page turns | readable at print size |
| Delivery | file set, page count, preserved score pages | final submission opens and contains all required material |

The relative weight depends on the user. If readability is explicitly prioritized over literal fidelity, intentional source deviations may pass only when they are logged and the performer-facing rhythm/voice result is clearer.

## Renderer round-trip

Record the renderer name/version, import settings, installed notation/text fonts, page size, and export path. MusicXML interchange commonly preserves notes and instruments better than exact spacing, fonts, page breaks, or custom text placement, so reproduce the same import settings before comparing revisions.

Use `scripts/compare_musicxml_semantics.py` when the renderer can export score-partwise MusicXML. Run the default notation comparison first. `--mode musical` is a coarser comparison of the covered pitch, onset, duration, voice/staff, tuplet-ratio, and sounding-tie fields; a zero result there suggests that differences reported only by notation mode are engraving-related, but it is not proof of full semantic equivalence. The comparator supports at most one leading attributes block per measure. Multiple attributes blocks and attributes appearing after a note, backup, or forward are rejected with exit 2 because mid-measure divisions, key, time, clef, and transpose changes are outside its model. Any layout-only workflow that changes a covered core field, meter, key, clef, transpose, or direction requires review. Score-timewise input is rejected rather than normalized silently.

## Evidence anchors

- [Transcribing Human Piano Performances into Music Notation](https://archives.ismir.net/ismir2016/paper/000088.pdf) supports staged correction of performance overlaps plus joint meter, harmony, stream, quantization, spelling, staff, and voice inference.
- [A Metric for Music Notation Transcription Accuracy](https://archives.ismir.net/ismir2017/paper/000131.pdf) motivates separate checks for barlines, clefs, signatures, pitch/spelling, duration, stems, grouping, rests, and staff assignment instead of note F-measure alone.
- [MusicXML tuplet reference](https://www.w3.org/2021/06/musicxml40/musicxml-reference/elements/tuplet/) distinguishes sounding `time-modification` from visible tuplet start/stop, bracket, placement, and number policy.
- [MuseScore MusicXML handbook](https://handbook.musescore.org/file-management/working-with-musicxml-files) documents that interchange usually needs cleanup and that fonts, spacing, and import options can change page/system layout.
- [mcp-score score-generation skill](https://raw.githubusercontent.com/tskovlund/mcp-score/main/.claude/skills/score-generate/SKILL.md) demonstrates an executable plan-to-MusicXML workflow with parse validation.
- [musiclaude composition skill](https://github.com/Eirawen/musiclaude/blob/main/.claude/skills/compose/SKILL.md) demonstrates scratchpad decisions, ranked feedback, and revision logging; its project evidence also cautions that feedback should remain optional and repeated iteration can degrade music.
