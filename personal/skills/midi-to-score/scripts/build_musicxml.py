#!/usr/bin/env python3
"""Build MusicXML 4.0 from an AI-authored score-plan JSON file."""

from __future__ import annotations

import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict
from datetime import date
from pathlib import Path
from typing import Any


class PlanError(ValueError):
    pass


PITCH_RE = re.compile(r"^([A-Ga-g])((?:bb|##|b|#)?)(-?\d+)$")
ALTER = {"": 0, "#": 1, "##": 2, "b": -1, "bb": -2}


def child(parent: ET.Element, tag: str, text: Any | None = None, **attrs: Any) -> ET.Element:
    node = ET.SubElement(parent, tag, {key.replace("_", "-"): str(value) for key, value in attrs.items()})
    if text is not None:
        node.text = str(text)
    return node


def parse_pitch(value: str) -> tuple[str, int, int]:
    match = PITCH_RE.match(value)
    if not match:
        raise PlanError(f"invalid pitch {value!r}; use values such as C4, F#5, or Bb3")
    step, accidental, octave = match.groups()
    return step.upper(), ALTER[accidental], int(octave)


def add_attributes(measure_el: ET.Element, spec: dict[str, Any]) -> None:
    attrs = child(measure_el, "attributes")
    if "divisions" in spec:
        child(attrs, "divisions", spec["divisions"])
    if "key" in spec:
        key = child(attrs, "key")
        child(key, "fifths", spec["key"].get("fifths", 0))
        if spec["key"].get("mode"):
            child(key, "mode", spec["key"]["mode"])
    if "time" in spec:
        time = child(attrs, "time")
        child(time, "beats", spec["time"]["beats"])
        child(time, "beat-type", spec["time"]["beat_type"])
    if "staves" in spec:
        child(attrs, "staves", spec["staves"])
    for clef_spec in spec.get("clefs", []):
        clef_attrs = {"number": clef_spec["number"]} if "number" in clef_spec else {}
        clef = child(attrs, "clef", **clef_attrs)
        child(clef, "sign", clef_spec["sign"])
        child(clef, "line", clef_spec["line"])
        if clef_spec.get("octave_change") is not None:
            child(clef, "clef-octave-change", clef_spec["octave_change"])
    if "transpose" in spec:
        transpose = child(attrs, "transpose")
        if spec["transpose"].get("diatonic") is not None:
            child(transpose, "diatonic", spec["transpose"]["diatonic"])
        child(transpose, "chromatic", spec["transpose"].get("chromatic", 0))
        if spec["transpose"].get("octave_change") is not None:
            child(transpose, "octave-change", spec["transpose"]["octave_change"])


def add_direction(measure_el: ET.Element, spec: dict[str, Any]) -> None:
    attrs = {}
    if spec.get("placement"):
        attrs["placement"] = spec["placement"]
    direction = child(measure_el, "direction", **attrs)
    dtype = child(direction, "direction-type")
    if "words" in spec:
        child(dtype, "words", spec["words"], **spec.get("words_attributes", {}))
    elif "rehearsal" in spec:
        child(dtype, "rehearsal", spec["rehearsal"])
    elif "dynamics" in spec:
        dynamics = child(dtype, "dynamics")
        child(dynamics, spec["dynamics"])
    elif "wedge" in spec:
        child(dtype, "wedge", type=spec["wedge"], number=spec.get("number", 1))
    elif "pedal" in spec:
        pedal = spec["pedal"]
        child(dtype, "pedal", type=pedal["type"], line=str(pedal.get("line", True)).lower(), number=pedal.get("number", 1))
    elif "metronome" in spec:
        metronome = child(dtype, "metronome")
        child(metronome, "beat-unit", spec["metronome"].get("beat_unit", "quarter"))
        for _ in range(spec["metronome"].get("dots", 0)):
            child(metronome, "beat-unit-dot")
        child(metronome, "per-minute", spec["metronome"]["per_minute"])
    else:
        raise PlanError(f"unsupported direction: {spec}")
    if spec.get("offset") is not None:
        child(direction, "offset", spec["offset"])
    if spec.get("voice") is not None:
        child(direction, "voice", spec["voice"])
    if spec.get("staff") is not None:
        child(direction, "staff", spec["staff"])
    sound_attrs = {}
    if spec.get("sound_tempo") is not None:
        sound_attrs["tempo"] = spec["sound_tempo"]
    if spec.get("sound_dynamics") is not None:
        sound_attrs["dynamics"] = spec["sound_dynamics"]
    if sound_attrs:
        child(direction, "sound", **sound_attrs)


def add_notations(note_el: ET.Element, spec: dict[str, Any], ties: list[str]) -> None:
    if not spec and not ties:
        return
    notations = child(note_el, "notations")
    for tie_type in ties:
        child(notations, "tied", type=tie_type)
    for slur in spec.get("slurs", []):
        child(notations, "slur", type=slur["type"], number=slur.get("number", 1), **({"placement": slur["placement"]} if slur.get("placement") else {}))
    for tuplet in spec.get("tuplets", []):
        attributes = {
            "type": tuplet["type"],
            "number": tuplet.get("number", 1),
            "bracket": str(tuplet.get("bracket", False)).lower(),
        }
        if tuplet.get("placement"):
            attributes["placement"] = tuplet["placement"]
        if tuplet.get("show_number"):
            attributes["show_number"] = tuplet["show_number"]
        child(notations, "tuplet", **attributes)
    articulations = spec.get("articulations", [])
    if articulations:
        art_el = child(notations, "articulations")
        for articulation in articulations:
            child(art_el, articulation)
    ornaments = spec.get("ornaments", [])
    if ornaments:
        orn_el = child(notations, "ornaments")
        for ornament in ornaments:
            child(orn_el, ornament)
    if spec.get("fermata"):
        child(notations, "fermata", spec["fermata"] if isinstance(spec["fermata"], str) else None)
    if spec.get("arpeggiate"):
        child(notations, "arpeggiate", number=spec.get("arpeggiate_number", 1))


def add_note(measure_el: ET.Element, spec: dict[str, Any]) -> None:
    note = child(measure_el, "note", **({"print_object": "no"} if spec.get("print_object") is False else {}))
    if spec.get("grace"):
        grace = spec["grace"] if isinstance(spec["grace"], dict) else {}
        child(note, "grace", **grace)
    if spec.get("chord"):
        child(note, "chord")
    if spec.get("rest") or spec.get("type") == "rest":
        rest_attrs = {"measure": "yes"} if spec.get("measure_rest") else {}
        child(note, "rest", **rest_attrs)
    else:
        if "pitch" not in spec:
            raise PlanError(f"note event missing pitch: {spec}")
        step, alter, octave = parse_pitch(spec["pitch"])
        pitch = child(note, "pitch")
        child(pitch, "step", step)
        if alter:
            child(pitch, "alter", alter)
        child(pitch, "octave", octave)
    if not spec.get("grace"):
        duration = spec.get("duration")
        if not isinstance(duration, int) or duration <= 0:
            raise PlanError(f"note/rest duration must be a positive integer: {spec}")
        child(note, "duration", duration)
    for tie_type in spec.get("ties", []):
        child(note, "tie", type=tie_type)
    if spec.get("voice") is not None:
        child(note, "voice", spec["voice"])
    if spec.get("type_name"):
        child(note, "type", spec["type_name"])
    for _ in range(spec.get("dots", 0)):
        child(note, "dot")
    if spec.get("accidental"):
        child(note, "accidental", spec["accidental"])
    if spec.get("time_modification"):
        modification = child(note, "time-modification")
        child(modification, "actual-notes", spec["time_modification"]["actual_notes"])
        child(modification, "normal-notes", spec["time_modification"]["normal_notes"])
        if spec["time_modification"].get("normal_type"):
            child(modification, "normal-type", spec["time_modification"]["normal_type"])
    if spec.get("stem"):
        child(note, "stem", spec["stem"])
    for beam in spec.get("beams", []):
        child(note, "beam", beam["value"], number=beam.get("number", 1))
    add_notations(note, spec.get("notations", {}), spec.get("ties", []))
    if spec.get("staff") is not None:
        child(note, "staff", spec["staff"])
    for lyric_spec in spec.get("lyrics", []):
        lyric = child(note, "lyric", number=lyric_spec.get("number", 1))
        if lyric_spec.get("syllabic"):
            child(lyric, "syllabic", lyric_spec["syllabic"])
        child(lyric, "text", lyric_spec["text"])


def add_barline(measure_el: ET.Element, spec: dict[str, Any]) -> None:
    barline = child(measure_el, "barline", location=spec.get("location", "right"))
    if spec.get("bar_style"):
        child(barline, "bar-style", spec["bar_style"])
    if spec.get("ending"):
        child(barline, "ending", spec["ending"].get("text"), number=spec["ending"]["number"], type=spec["ending"]["type"])
    if spec.get("repeat"):
        child(barline, "repeat", direction=spec["repeat"]["direction"], times=spec["repeat"].get("times", 2))


def validate_measure(measure: dict[str, Any], state: dict[str, int]) -> None:
    attrs = measure.get("attributes", {})
    if "divisions" in attrs:
        state["divisions"] = int(attrs["divisions"])
    if "time" in attrs:
        state["beats"] = int(attrs["time"]["beats"])
        state["beat_type"] = int(attrs["time"]["beat_type"])
    if state.get("divisions", 0) <= 0:
        raise PlanError(f"measure {measure.get('number')} has no valid divisions")
    cursor = 0
    for event in measure.get("events", []):
        kind = event.get("type", "note")
        if kind in ("note", "rest"):
            if not event.get("grace") and not event.get("chord"):
                duration = event.get("duration")
                if not isinstance(duration, int) or duration <= 0:
                    raise PlanError(f"measure {measure.get('number')}: invalid duration")
                cursor += duration
            if kind == "note" and not event.get("rest"):
                parse_pitch(event.get("pitch", ""))
        elif kind == "backup":
            cursor -= int(event["duration"])
            if cursor < 0:
                raise PlanError(f"measure {measure.get('number')}: backup moves before measure start")
        elif kind == "forward":
            cursor += int(event["duration"])
        elif kind == "barline":
            continue
        else:
            raise PlanError(f"measure {measure.get('number')}: unsupported event type {kind!r}")
    if not measure.get("implicit") and state.get("beats") and state.get("beat_type"):
        expected_num = state["divisions"] * state["beats"] * 4
        if expected_num % state["beat_type"]:
            raise PlanError(f"measure {measure.get('number')}: non-integral expected duration")
        expected = expected_num // state["beat_type"]
        if cursor != expected:
            raise PlanError(
                f"measure {measure.get('number')}: event cursor ends at {cursor}, expected {expected}; "
                "use rests/forward/backup or set implicit=true for a pickup"
            )


def build(plan: dict[str, Any]) -> ET.ElementTree:
    if plan.get("schema") != "score-plan-v1":
        raise PlanError("schema must be score-plan-v1")
    parts = plan.get("parts")
    if not isinstance(parts, list) or not parts:
        raise PlanError("parts must be a non-empty list")
    ids = [part.get("id") for part in parts]
    if any(not value for value in ids) or len(set(ids)) != len(ids):
        raise PlanError("every part needs a unique id")

    root = ET.Element("score-partwise", version="4.0")
    if plan.get("work_title") or plan.get("title"):
        work = child(root, "work")
        child(work, "work-title", plan.get("work_title") or plan.get("title"))
    if plan.get("movement_title"):
        child(root, "movement-title", plan["movement_title"])
    identification = child(root, "identification")
    if plan.get("composer"):
        child(identification, "creator", plan["composer"], type="composer")
    if plan.get("rights"):
        child(identification, "rights", plan["rights"])
    encoding = child(identification, "encoding")
    child(encoding, "encoding-date", date.today().isoformat())
    child(encoding, "software", "midi-to-score AI score-plan builder")

    part_list = child(root, "part-list")
    groups = plan.get("groups", [])
    starts: dict[str, list[dict[str, Any]]] = defaultdict(list)
    stops: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for group in groups:
        starts[group["start_part_id"]].append(group)
        stops[group["end_part_id"]].append(group)
    for part in parts:
        for group in starts.get(part["id"], []):
            group_el = child(part_list, "part-group", type="start", number=group.get("number", 1))
            if group.get("name"):
                child(group_el, "group-name", group["name"])
            child(group_el, "group-symbol", group.get("symbol", "bracket"))
            child(group_el, "group-barline", group.get("barline", "yes"))
        score_part = child(part_list, "score-part", id=part["id"])
        child(score_part, "part-name", part["name"])
        if part.get("abbreviation"):
            child(score_part, "part-abbreviation", part["abbreviation"])
        score_instrument = child(score_part, "score-instrument", id=f"{part['id']}-I1")
        child(score_instrument, "instrument-name", part.get("instrument_name", part["name"]))
        if part.get("midi_program") is not None:
            midi_instrument = child(score_part, "midi-instrument", id=f"{part['id']}-I1")
            child(midi_instrument, "midi-channel", part.get("midi_channel", 1))
            child(midi_instrument, "midi-program", part["midi_program"])
        for group in stops.get(part["id"], []):
            child(part_list, "part-group", type="stop", number=group.get("number", 1))

    for part in parts:
        part_el = child(root, "part", id=part["id"])
        state = {"divisions": 0, "beats": 0, "beat_type": 0}
        measures = part.get("measures", [])
        if not measures:
            raise PlanError(f"part {part['id']} has no measures")
        for measure in measures:
            validate_measure(measure, state)
            attrs = {"number": measure["number"]}
            if measure.get("implicit"):
                attrs["implicit"] = "yes"
            measure_el = child(part_el, "measure", **attrs)
            if measure.get("print"):
                child(measure_el, "print", **measure["print"])
            if measure.get("attributes"):
                add_attributes(measure_el, measure["attributes"])
            for direction in measure.get("directions", []):
                add_direction(measure_el, direction)
            for event in measure.get("events", []):
                kind = event.get("type", "note")
                if kind in ("note", "rest"):
                    add_note(measure_el, event)
                elif kind in ("backup", "forward"):
                    event_el = child(measure_el, kind)
                    child(event_el, "duration", event["duration"])
                elif kind == "barline":
                    add_barline(measure_el, event)
    ET.indent(root, space="  ")
    return ET.ElementTree(root)


def self_test(tmp_path: Path) -> None:
    plan = {
        "schema": "score-plan-v1",
        "title": "Self Test",
        "composer": "Codex",
        "parts": [
            {
                "id": "P1",
                "name": "Piano",
                "measures": [
                    {
                        "number": 1,
                        "attributes": {
                            "divisions": 480,
                            "key": {"fifths": 0, "mode": "major"},
                            "time": {"beats": 4, "beat_type": 4},
                            "staves": 2,
                            "clefs": [
                                {"number": 1, "sign": "G", "line": 2},
                                {"number": 2, "sign": "F", "line": 4},
                            ],
                        },
                        "directions": [
                            {"metronome": {"beat_unit": "quarter", "per_minute": 90}, "sound_tempo": 90}
                        ],
                        "events": [
                            {"type": "note", "pitch": "C4", "duration": 480, "voice": 1, "staff": 1, "type_name": "quarter"},
                            {"type": "rest", "rest": True, "duration": 1440, "voice": 1, "staff": 1, "type_name": "half", "dots": 1},
                        ],
                    }
                ],
            }
        ],
    }
    tree = build(plan)
    tree.write(tmp_path, encoding="utf-8", xml_declaration=True)
    parsed = ET.parse(tmp_path)
    assert parsed.getroot().tag == "score-partwise"
    assert parsed.findtext("./part/measure/note/pitch/step") == "C"
    print("self-test passed")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan", nargs="?", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        target = Path("/tmp/midi-to-score-self-test.musicxml")
        self_test(target)
        target.unlink(missing_ok=True)
        return 0
    if args.plan is None or args.output is None:
        parser.error("plan and --output are required unless --self-test is used")
    try:
        plan = json.loads(args.plan.read_text(encoding="utf-8"))
        tree = build(plan)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        tree.write(args.output, encoding="utf-8", xml_declaration=True)
    except (OSError, json.JSONDecodeError, PlanError, KeyError, TypeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(f"wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
