# Engraving workflow and QA

Read this reference for substantive cleanup, layout, or final verification.

## Source inventory

Create a compact inventory before editing:

| Field | What to verify |
|---|---|
| Range | Inclusive requested measures and exclusive end marker |
| Track role | Instrument staff, folder, bus, control track, duplicate, or audio reference |
| Event coverage | First/last note, silent spans, event gaps, muted/layered material |
| Instrument | Full/short name, score order, clef, transposition, practical range |
| Global map | Meter, key, tempo, rehearsal/arranger markers |
| Expression | Velocity, CC1/2/11/64, keyswitches, articulations, slurs, pedal |
| Output | Full score, parts, PDF, MIDI, optional MusicXML |

## Recommended score order

For piano and woodwind quartet, default to:

1. Flute
2. Oboe
3. Clarinet in B-flat
4. Bassoon
5. Piano

Use a bracket for the woodwind group and a brace for the piano grand staff when the available layout supports it. Do not print a folder track as a staff.

Confirm whether the clarinet is actually in B-flat before applying transposition. Flute, oboe, bassoon, and piano are normally shown at concert pitch; bassoon normally uses bass clef with tenor clef only where it improves readability. Keep the conductor score consistently concert-pitch or transposed and label the choice.

## Rhythm cleanup

- Decide the smallest legitimate rhythmic unit from the musical phrase, not from the shortest recorded MIDI deviation.
- Prefer notation quantization or display quantization over playback quantization.
- Split independent lines into voices; use ties across beats/bars instead of opaque long values.
- Retain genuine tuplets, but remove tuplets produced only by human timing drift.
- For dense monophonic wind MIDI, preserve attack order and pitch contour while rewriting the rhythm onto the simplest grid that matches what is heard. If the irregularity is not perceived as a tuplet, do not print a forest of tuplets and short rests merely because the performed onsets are uneven.
- For piano, allocate notes by musical hand/voice rather than a fixed pitch split. Check cross-staff phrases, inner voices, sustained bass, and pedal-held harmony.
- Replace genuine event-boundary silences with explicit rests in the printed interval. In a continuous pedaled or ornamental texture, do not turn short performance gaps inside an ongoing gesture into printed rests.
- Check notes that begin before the range or sustain beyond it; decide whether to show ties, cut the excerpt, or add an explanatory continuation.

### Piano tuplet-texture gate

For continuous virtuoso textures, infer a small number of musical streams before writing individual notes. Assign each stream a hand or cross-staff trajectory, pulse span, tuplet ratio, beaming pattern, and sustained harmonic layer. Do not create voices by greedy interval coloring or by a fixed pitch threshold when the result is meant to be played as one gesture.

- Write complete tuplet groups against an explicit pulse. Keep a stream in one voice through register crossings; use cross-staff notation or clef changes when that reads better than splitting the line.
- When a dense attack chain may be two concurrent irregular grids, test its onset lattice over the full beat before grouping by attack count. Interleaved septuplet and sextuplet streams can appear as alternating 6/7-note half-beat clusters even though the intended notation is 7 against 6 across one pulse. Preserve each grid as its own complete voice, and infer isolated missing slots only after the two rhythmic identities are established.
- Treat continuity as a musical invariant when the passage is heard as an unbroken wave, tremulation, arpeggiation, or ornamental field. A rest in the fast stream requires an audible structural interruption, not merely a missing MIDI attack, a lifted finger, or quantization residue. When the user prioritizes readability over literal fidelity, it is acceptable to redistribute, sustain, omit, or infer pitches inside a repeated figure so that every printed tuplet slot carries the continuous gesture.
- Separate pedal-held harmony from attacked voices. Pedal overlap must not create additional printed attacks, fragmented rests, or extra contrapuntal voices.
- Prefer one continuous beamed figure plus at most one sustained layer per staff. Nested or partial tuplets require positive musical evidence; importer-generated orphan numbers, isolated brackets, and tuplets spanning hidden forwards are a failure.
- When a reference score or style is named, inspect how it communicates pulse, hand distribution, register crossing, and repeated irregular groups. Borrow the organizational principle, not copyrighted note content.

Before accepting a dense piano passage, inspect it at print size with playback ignored. A pianist must be able to identify every beat, tuplet boundary, hand/voice path, and sustained layer from the page alone. Source-note completeness, valid MusicXML, successful playback, and collision-free rendering do not prove this. If the pulse cannot be counted visually or either staff needs more than two simultaneous printed voices, rewrite the notation model rather than adjusting spacing.

## Tempo and meter

MIDI tempo automation may contain many tempo points. Printed notation should usually show:

- a metronome mark at the beginning and at stable anchor tempos;
- `accel.` or `rit.` over continuous ramps;
- a destination metronome mark where the new tempo settles;
- explicit `a tempo` or `Tempo I` when the music returns.

Do not place a tempo mark for every automation node. Verify every time-signature change at the exact bar boundary. If a signature changes mid-measure, confirm whether it represents a pickup, split bar, or mistaken map.

## Pitch, transposition, and spelling

- Choose a key signature or no-key-signature policy deliberately.
- Correct enharmonic spelling by harmonic/voice context, especially chromatic lines and piano chords.
- Check written and sounding ranges after transposition.
- Confirm octave-transposing instruments if present.
- Avoid changing MIDI pitch merely to improve spelling; use notation spelling controls when available.

## Expression

Velocity and controller curves are evidence, not finished notation. Translate them into a restrained set of dynamics and hairpins that performers can execute. Add slurs, accents, staccato, tenuto, breath marks, fermatas, pedal, and technique text only when supported by phrasing or playback intent.

For piano, inspect CC64 and decide where pedal marks or `Ped.`/release symbols are needed. For winds, distinguish MIDI overlap used for legato playback from actual slurred phrasing.

- In two-hand piano notation, determine hand, voice, and the complete pulse-sized gesture before setting staff or stems. Do not assign every note independently by pitch. A brief register crossing should normally remain with the hand that owns the surrounding tuplet or ornamental group; reassign the whole gesture only when that produces the clearer physical and visual result. When using a named reference score, compare its actual hand layers, staff assignment, clef changes, and beam continuity instead of borrowing a superficial stem rule.
- When the user relies on stems to distinguish the hands, record and enforce that visual convention separately from abstract voice-leading. For example, if high/right-hand groups must stem upward and low/left-hand groups downward, allocate each complete group to a hand first and then apply that convention. Do not use inward-pointing cross-staff beams that obscure the requested split. Validate the rendered page by tracing every hand-group from beginning to end and count any mid-group staff swaps.
- Treat the renderer as authoritative for stem and beam appearance. Cross-staff beaming may override explicit MusicXML stem declarations, while breaking a beam at a staff change may produce diagonal or detached tuplet brackets. If either happens, reject that notation model and reassign the complete gesture; do not try to conceal the structural problem with spacing alone.
- Do not convert every continuous or overlapping wind MIDI passage into a long slur. Prefer a written legato instruction plus a few short, specific same-breath groups; avoid automatic multi-bar arcs and verify that each remaining slur has a clear musical endpoint.

## Page layout

- Enter title and composer metadata before printing.
- Use Full Score Page Layout, not Continuous Layout, for PDF/printing.
- Make system density consistent; avoid a final page with one stranded system when a modest spacing change fixes it.
- Keep bar numbers at each system or at every measure according to rehearsal needs.
- Place rehearsal marks at structural points and before difficult meter/tempo changes.
- Prevent collisions among tuplets, slurs, dynamics, hairpins, tempo text, and staff labels.
- For parts, create sensible multi-measure rests and page turns; full-score layout alone is not part extraction.

## Renderer round-trip gate

The score plan and MusicXML define intended semantics; the notation engine's exported PDF defines what the musician actually receives. After every meaningful rhythm, hand-allocation, beam, tuplet, or layout change, round-trip through the actual notation engine and inspect the rendered result before continuing.

- Confirm the output path and modification time after command-line conversion. Use any required force-overwrite option explicitly; a successful process exit without a newly written file is not a successful render.
- Check automatic tuplet numbers and brackets, cross-staff stem overrides, beam geometry, direction text, part order, and page breaks in the rendered PDF. XML declarations alone are not acceptance evidence.
- If the native score container must be postprocessed, make the operation idempotent and count the exact objects changed. Verify that rerunning it creates no duplicate labels, hidden objects, or accumulated formatting changes.
- Inspect representative dense pages after a local change before rebuilding the full deliverable. Reject an iteration immediately if it introduces diagonal tuplet brackets, clipped labels, collisions, or a less legible hand path.

## Submission packaging

- If the assignment requires an explanation on the score, place it in a score text frame or prepend a dedicated page. Name the chosen composer/style and identify concrete features visible in the notation rather than giving only a general biography.
- Keep the score-only PDF as an immutable intermediate and rebuild the submission from it each time. Never merge a new cover into a PDF that may already contain a cover.
- For Japanese or other CJK text, verify visible glyphs by rendering the PDF with the same inspection tool used for final QA. Successful PDF creation, extractable metadata, or a declared CID font does not prove that the page is visible. If portable vector font embedding is unreliable, a high-resolution rasterized text page using a known local font is an acceptable fallback.
- After merging, verify the expected total page count, uniform paper size, legibility of the explanation page, and byte/content-stream preservation of every original score page where feasible. Render and inspect every page of the final merged PDF.

## Final acceptance checks

- The PDF begins at the requested first bar and contains the complete requested last bar.
- No hidden, folder, bus, or duplicate staff is printed.
- All intended instruments appear in the correct order on every applicable system.
- Clefs, transposition, key signatures, and bar numbers are coherent.
- All tempo and meter changes in the Song are represented musically.
- Dense passages are readable at print size, not only at screen zoom.
- Tuplet labels must identify complete, countable groups without colliding with
  the other staff or resembling a different number. A tuplet made primarily of
  rests, or an incomplete group whose ratio cannot be understood without the
  MIDI, must be rhythmically rewritten rather than merely spaced apart.
- Inspect stem direction as voice semantics wherever two layers share a staff:
  the sustained, ornamental, and bass layers must remain distinguishable across
  the entire gesture. Correct staff assignment or successful automatic layout
  is not sufficient evidence.
- When a stem convention has been requested, sample every dense section in the
  rendered PDF and count violations by hand region. A declaration in MusicXML
  or a structurally continuous cross-staff beam is not proof that the player's
  right/left-hand split reads correctly.
- No complete piano tuplet or ornamental hand-group changes staff midway merely
  because individual pitches cross a threshold. Any exception has an explicit
  musical reason and remains immediately traceable in the rendered page.
- Audit enharmonic spelling by phrase and harmony. A chromatic score generated
  almost entirely with one accidental direction is a failed spelling pass even
  when every sounding pitch is correct.
- Count systems and measures per page. Rebalance a full score with isolated
  one-measure pages or unusable performance page turns; if the full score cannot
  serve the players, produce readable parts before calling the delivery final.
- First and last notes, tied notes, long rests, and notes crossing event boundaries match the source.
- A representative playback comparison has been done at the beginning, a dense middle passage, every meter/tempo transition, and the ending.
- Every PDF page has been rendered/opened and visually inspected.
- Required explanatory front matter is present, legible, and free of missing
  CJK glyphs; merging it has not altered or dropped any original score page.
