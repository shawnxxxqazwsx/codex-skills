---
name: midi-to-score
description: Interpret performed MIDI and write a musician-readable score with AI-authored rhythm, voices, spelling, expression, transposition, and layout, producing a score plan and MusicXML instead of trusting a DAW's automatic notation. Use for Studio One or other DAW MIDI-to-score work; do not use for audio-only transcription unless reliable note data is first derived.
---

# MIDI to Score

Write the score from musical evidence. DAW notation is a comparison view, never the authority.

## Source and authorization

When the source is Studio One, use the available live computer-control or DAW workflow to inspect it. Record the application version, Song name, requested inclusive measure range, Instrument Tracks, event coverage, layers/mutes, tempo, time/key signatures, markers, controllers, and available reference audio.

Export a Type 1 Standard MIDI File with the tempo map and track names. Prefer Studio One **File > Save As** with `.mid`/`.midi` for a full-song interchange export. Keep the original `.song` unchanged. If MIDI cleanup is required, first use **Save New Version** or a user-approved duplicate.

Do not derive a staff from folders, buses, control tracks, audio references, or duplicate layers. Do not upload private MIDI/audio to an online converter without specific authorization.

Treat “measure 5 through the end of measure 41” as `[5.1.1, 42.1.1)`. Verify Song Start/End markers separately from left/right loop locators.

## Extract facts; do not auto-engrave

Run the deterministic tools from this skill:

```bash
python3 scripts/audit_midi.py /absolute/path/source.mid --start-bar 5 --end-bar 41
python3 scripts/extract_midi_context.py /absolute/path/source.mid \
  --start-bar 5 --end-bar 41 --output /absolute/path/midi-context.json
```

The scripts expose timing, notes, velocities, controllers, meter, key, tempo, track identity, boundaries, and anomalies. They must not decide rhythm spelling, voices, phrasing, enharmonics, dynamics, or layout.

Read [references/engraving-workflow.md](references/engraving-workflow.md) before interpretation. For the authoring format and supported MusicXML features, read [references/score-plan-schema.md](references/score-plan-schema.md).

For ambiguous quantization, substantial rewrites, renderer round-trips, or repeated revisions, also read [references/evaluation-and-revision.md](references/evaluation-and-revision.md). It defines the interpretation ledger, semantic-diff gate, and stopping rule.

## Interpret like an arranger and copyist

Work from global structure to local detail:

1. Establish score order, instrument identity, written transposition, clefs, score pitch convention, meter map, key/no-key policy, and tempo landmarks.
2. In a derived analysis layer, repair spurious overlaps and near-duplicate attacks without changing the raw MIDI. Segment each track into phrases and infer meter/barlines, harmonic context, streams, and the intended rhythmic grid together from repeated patterns and ensemble alignment—not from the shortest performance deviation.
3. Quantize notation conceptually while preserving the original onset/duration data as evidence. Prefer simple, performer-readable spellings; retain genuine tuplets and irregular rhythm.
4. Separate independent lines into voices. For piano, allocate notes by musical hand and contrapuntal role, not a fixed pitch split.
5. Infer enharmonic spelling from line direction, harmony, neighboring voices, and key context.
6. Translate velocity, CC1/2/11/64, overlap, gaps, keyswitches, and reference audio into restrained dynamics, hairpins, articulations, slurs, breathing, pedal, and technique text. Treat these as evidence, not one-to-one mappings.
7. Translate continuous tempo automation into a few metronome anchors plus `accel.`, `rit.`, `a tempo`, or `Tempo I` where musically justified.

Resolve uncertain passages explicitly. Preserve at least two candidate readings in working notes when the evidence is genuinely ambiguous, then choose using ensemble alignment and playback comparison. Never hide interpretive uncertainty behind mechanical quantization.

## Author the score

Write an AI-authored score plan JSON measure by measure. The plan is the notation source of truth; raw MIDI remains evidence. Generate MusicXML with:

```bash
python3 scripts/build_musicxml.py /absolute/path/score-plan.json \
  --output /absolute/path/full-score.musicxml
```

The builder validates structure and serializes the AI's explicit decisions. It does not invent notation. Keep the score plan alongside MusicXML so decisions remain inspectable and recoverable.

For substantive interpretation, keep a compact decision ledger beside the score plan. Record the affected bars/parts, evidence, alternatives, chosen reading, and every intentional departure from literal MIDI. The plan remains the semantic source of truth; renderer-native files may own layout-only adjustments. Backport any native edit that changes musical semantics to the plan or record it as an unresolved divergence.

Use a local notation renderer/editor such as MuseScore, Dorico, Sibelius, or Notion only to import/render and make layout adjustments. Do not silently install software. If no renderer is installed, deliver the validated score plan and MusicXML, report that PDF rendering remains blocked, and ask before installing or connecting a renderer.

Studio One Score View may be opened for spot comparison, but do not copy its automatic tuplets, voices, beaming, spelling, or dynamics without independent musical validation.

## Verify

Validation is five-way:

1. immutable-source and boundary audit against the extracted MIDI context;
2. schema/build validation of the score plan and MusicXML;
3. notation-dimension audit for meter/barlines, pitch spelling, durations/rests/ties, voices/staves, tuplets/beams, expression, and documented intentional deviations;
4. playback comparison against original MIDI/audio at the beginning, dense passages, every tempo/meter transition, and the ending;
5. renderer round-trip plus visual inspection of every final page at print size.

When a renderer can export MusicXML, compare the pre-import and round-tripped files with:

```bash
python3 scripts/compare_musicxml_semantics.py before.musicxml after.musicxml
```

A layout-only pass should not silently change score semantics. The comparator covers score-partwise pitch, onset, duration, voice/staff, tuplets, ties, selected engraving fields, one leading attributes block per measure, and directions. It rejects multiple attributes blocks or an attributes block after a note, backup, or forward because it does not model mid-measure state changes. It is not a complete MusicXML equivalence proof. Review every reported field rather than accepting parse success or a zero diff alone.

Check the inclusive final measure, staff order, written/sounding pitch, clefs, voice completeness, ties, rests, tuplets, beaming, collisions, dynamics, pedal, rehearsal marks, page turns, and tempo/meter changes. Report what was observed, what was inferred, and what remains unrendered or interpretive.
