# Score plan schema

Use `score-plan-v1` as the inspectable notation source of truth. The plan records the AI's decisions; it is not a dump of MIDI events.

## Top level

```json
{
  "schema": "score-plan-v1",
  "title": "Quartet_001",
  "composer": "Composer Name",
  "groups": [
    {
      "number": 1,
      "name": "Woodwinds",
      "symbol": "bracket",
      "barline": "yes",
      "start_part_id": "P1",
      "end_part_id": "P4"
    }
  ],
  "parts": []
}
```

Optional top-level fields are `work_title`, `movement_title`, and `rights`.

## Parts

```json
{
  "id": "P3",
  "name": "Clarinet in B-flat",
  "abbreviation": "Cl.",
  "instrument_name": "B-flat Clarinet",
  "midi_channel": 1,
  "midi_program": 72,
  "measures": []
}
```

Part IDs must be unique. MusicXML MIDI programs are one-based. Score order is the order of `parts`.

## Measures and attributes

Every part contains the complete requested measure range. Use explicit rests for silence.

```json
{
  "number": 5,
  "attributes": {
    "divisions": 480,
    "key": {"fifths": 0, "mode": "minor"},
    "time": {"beats": 4, "beat_type": 4},
    "staves": 1,
    "clefs": [{"number": 1, "sign": "G", "line": 2}],
    "transpose": {"diatonic": -1, "chromatic": -2}
  },
  "directions": [],
  "events": []
}
```

Repeat attributes only when they change. For a B-flat clarinet written a major second above sounding pitch, MusicXML commonly uses `diatonic: -1` and `chromatic: -2` to describe the sounding transposition. Confirm the imported result in the chosen renderer; never transpose note pitches twice.

For piano, use `staves: 2` and G/F clefs numbered 1 and 2. Use `implicit: true` only for a real pickup or intentionally incomplete bar.

## Directions

Directions occur before measure events and can carry an `offset`, `staff`, `voice`, and `placement`.

```json
[
  {
    "metronome": {"beat_unit": "quarter", "per_minute": 90},
    "sound_tempo": 90,
    "placement": "above"
  },
  {"words": "rit.", "offset": 960, "placement": "above"},
  {"dynamics": "p", "placement": "below", "staff": 1},
  {"wedge": "crescendo", "number": 1, "placement": "below"},
  {"wedge": "stop", "number": 1, "offset": 1440, "placement": "below"},
  {"rehearsal": "A", "placement": "above"},
  {"pedal": {"type": "start", "line": true, "number": 1}, "staff": 2}
]
```

Supported direction alternatives are `words`, `rehearsal`, `dynamics`, `wedge`, `pedal`, and `metronome`.

## Notes and rests

Durations use the current `divisions` value. A quarter note is `divisions`; a full 4/4 bar is `4 * divisions`.

```json
{
  "type": "note",
  "pitch": "F#4",
  "duration": 240,
  "voice": 1,
  "staff": 1,
  "type_name": "eighth",
  "accidental": "sharp",
  "beams": [{"number": 1, "value": "begin"}],
  "notations": {
    "articulations": ["staccato"],
    "slurs": [{"type": "start", "number": 1}]
  }
}
```

Pitch syntax accepts `C4`, `F#5`, `Bb3`, `C##4`, and `Ebb4`. The pitch spelling in the plan is authoritative.

For rests:

```json
{"type": "rest", "rest": true, "duration": 1920, "voice": 1, "staff": 1, "measure_rest": true}
```

For simultaneous chord tones, set `chord: true` on every tone after the first. Chord notes do not advance the measure cursor.

For ties, use `"ties": ["start"]`, `"ties": ["stop"]`, or both. For dots, set `dots`. Grace notes use `grace: true` or a MusicXML grace-attribute object and omit duration.

Tuplets require both playback ratio and visual start/stop:

```json
{
  "type": "note",
  "pitch": "D5",
  "duration": 160,
  "voice": 1,
  "type_name": "eighth",
  "time_modification": {"actual_notes": 3, "normal_notes": 2, "normal_type": "eighth"},
  "notations": {"tuplets": [{"type": "start", "number": 1, "bracket": false, "placement": "above"}]}
}
```

Supported note notation keys include `articulations`, `ornaments`, `slurs`, `tuplets`, `fermata`, and `arpeggiate`. Supported direct fields include `stem`, `beams`, `lyrics`, `print_object`, `staff`, and `voice`.

For simultaneous tuplets, give the concurrent spans different `number` values. Use optional tuplet `placement` (`above` or `below`) when their numerals would otherwise collide between piano staves. Repeated groups may set `show_number` to `none` after the ratio is established, while retaining the time modification and tuplet span.

## Multiple voices and staves

Serialize one complete voice, use `backup` to return the cursor, then serialize the next voice:

```json
[
  {"type": "note", "pitch": "C5", "duration": 1920, "voice": 1, "staff": 1, "type_name": "whole"},
  {"type": "backup", "duration": 1920},
  {"type": "note", "pitch": "C3", "duration": 1920, "voice": 2, "staff": 2, "type_name": "whole"}
]
```

`forward` advances without a printed rest. Prefer printed rests for performer-facing silence; use `forward` only for MusicXML sequencing/layout needs.

The builder verifies that the final event cursor equals the measure duration. It does not verify contrapuntal completeness inside every voice, so inspect each voice manually.

## Barlines and layout breaks

Barline events can specify `bar_style`, `repeat`, and `ending`. A measure-level `print` object can request MusicXML print attributes such as `new_system` or `new_page` (underscores become hyphens).

Do not hard-code system/page breaks until musical content is stable and a renderer has shown the actual spacing.
