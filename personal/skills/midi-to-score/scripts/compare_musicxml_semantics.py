#!/usr/bin/env python3
"""Compare performer-relevant fields in two score-partwise MusicXML or MXL files."""

from __future__ import annotations

import argparse
import json
import sys
import xml.etree.ElementTree as ET
import zipfile
from fractions import Fraction
from pathlib import Path
from typing import Any


def local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def children(node: ET.Element, name: str) -> list[ET.Element]:
    return [child for child in node if local(child.tag) == name]


def first(node: ET.Element, name: str) -> ET.Element | None:
    return next((child for child in node if local(child.tag) == name), None)


def text(node: ET.Element | None, name: str | None = None, default: str = "") -> str:
    target = first(node, name) if node is not None and name else node
    return default if target is None or target.text is None else target.text.strip()


def signature(node: ET.Element) -> tuple[Any, ...]:
    return (
        local(node.tag),
        text(node),
        tuple(sorted(node.attrib.items())),
        tuple(signature(child) for child in node),
    )


def read_root(path: Path) -> ET.Element:
    if path.suffix.lower() != ".mxl":
        return ET.parse(path).getroot()
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        rootfile = ""
        if "META-INF/container.xml" in names:
            container = ET.fromstring(archive.read("META-INF/container.xml"))
            for node in container.iter():
                if local(node.tag) == "rootfile" and node.get("full-path"):
                    rootfile = node.get("full-path", "")
                    break
        if not rootfile:
            rootfile = next((name for name in names if name.lower().endswith((".musicxml", ".xml")) and not name.startswith("META-INF/")), "")
        if not rootfile:
            raise ValueError(f"{path}: no MusicXML root file in MXL container")
        return ET.fromstring(archive.read(rootfile))


def pitch_of(note: ET.Element) -> tuple[Any, ...]:
    pitch = first(note, "pitch")
    if pitch is not None:
        return ("pitch", text(pitch, "step"), text(pitch, "alter", "0"), text(pitch, "octave"))
    unpitched = first(note, "unpitched")
    if unpitched is not None:
        return ("unpitched", text(unpitched, "display-step"), text(unpitched, "display-octave"))
    return ("rest",) if first(note, "rest") is not None else ("none",)


def note_record(note: ET.Element, divisions: int, onset: Fraction, mode: str) -> dict[str, Any]:
    duration_text = text(note, "duration")
    duration = None if not duration_text else str(Fraction(int(duration_text), divisions))
    modification = first(note, "time-modification")
    record: dict[str, Any] = {
        "pitch": pitch_of(note),
        "onset_quarters": str(onset),
        "duration_quarters": duration,
        "voice": text(note, "voice", "1"),
        "staff": text(note, "staff", "1"),
        "chord": first(note, "chord") is not None,
        "grace": first(note, "grace") is not None,
        "tuplet_ratio": None if modification is None else (
            text(modification, "actual-notes"),
            text(modification, "normal-notes"),
            text(modification, "normal-type"),
        ),
        "ties": sorted(node.get("type", "") for node in children(note, "tie")),
    }
    if mode == "notation":
        notations = first(note, "notations")
        record.update({
            "type": text(note, "type"),
            "dots": len(children(note, "dot")),
            "accidental": text(note, "accidental"),
            "stem": text(note, "stem"),
            "beams": [(node.get("number", "1"), text(node)) for node in children(note, "beam")],
            "tuplets": [] if notations is None else [
                (node.get("type", ""), node.get("number", "1"), node.get("bracket", ""), node.get("placement", ""), node.get("show-number", ""))
                for node in children(notations, "tuplet")
            ],
            "tied": [] if notations is None else sorted(node.get("type", "") for node in children(notations, "tied")),
            "slurs": [] if notations is None else [(node.get("type", ""), node.get("number", "1")) for node in children(notations, "slur")],
            "notations": None if notations is None else signature(notations),
            "lyrics": [signature(node) for node in children(note, "lyric")],
        })
    return record


def attribute_state(measure: ET.Element, state: dict[str, Any]) -> None:
    attrs = first(measure, "attributes")
    if attrs is None:
        return
    divisions = text(attrs, "divisions")
    if divisions:
        state["divisions"] = int(divisions)
    key = first(attrs, "key")
    if key is not None:
        state["key"] = (text(key, "fifths", "0"), text(key, "mode"))
    time = first(attrs, "time")
    if time is not None:
        state["time"] = (text(time, "beats"), text(time, "beat-type"))
    clefs = children(attrs, "clef")
    if clefs:
        state["clefs"] = [(node.get("number", "1"), text(node, "sign"), text(node, "line"), text(node, "clef-octave-change")) for node in clefs]
    transpose = first(attrs, "transpose")
    if transpose is not None:
        state["transpose"] = (text(transpose, "diatonic", "0"), text(transpose, "chromatic", "0"), text(transpose, "octave-change", "0"))


def validate_attribute_placement(measure: ET.Element, part_name: str) -> None:
    """Reject measure-level attribute layouts this bounded comparator cannot model."""
    nodes = list(measure)
    attribute_indexes = [index for index, node in enumerate(nodes) if local(node.tag) == "attributes"]
    measure_number = measure.get("number", "")
    location = f"part {part_name or '<unnamed>'}, measure {measure_number or '<unnumbered>'}"
    if len(attribute_indexes) > 1:
        raise ValueError(f"{location}: multiple <attributes> blocks are unsupported")
    if not attribute_indexes:
        return
    attribute_index = attribute_indexes[0]
    if any(local(node.tag) in {"note", "backup", "forward"} for node in nodes[:attribute_index]):
        raise ValueError(f"{location}: <attributes> after note/backup/forward is unsupported")


def directions_of(measure: ET.Element) -> list[tuple[Any, ...]]:
    output = []
    for direction in children(measure, "direction"):
        dtype = first(direction, "direction-type")
        payload = [] if dtype is None else [signature(node) for node in dtype]
        sound = first(direction, "sound")
        output.append((direction.get("placement", ""), text(direction, "offset", "0"), text(direction, "voice", ""), text(direction, "staff", ""), payload, () if sound is None else tuple(sorted(sound.attrib.items()))))
    return output


def notes_of(measure: ET.Element, divisions: int, mode: str) -> list[dict[str, Any]]:
    cursor = Fraction(0)
    previous_onset = Fraction(0)
    indexed: list[tuple[Fraction, int, dict[str, Any]]] = []
    order = 0
    for node in measure:
        kind = local(node.tag)
        if kind in {"backup", "forward"}:
            amount_text = text(node, "duration")
            if not amount_text:
                continue
            amount = Fraction(int(amount_text), divisions)
            cursor = cursor - amount if kind == "backup" else cursor + amount
            continue
        if kind != "note":
            continue
        is_chord = first(node, "chord") is not None
        is_grace = first(node, "grace") is not None
        onset = previous_onset if is_chord else cursor
        if not is_chord:
            previous_onset = onset
        record = note_record(node, divisions, onset, mode)
        indexed.append((onset, order, record))
        order += 1
        duration_text = text(node, "duration")
        if not is_chord and not is_grace and duration_text:
            cursor += Fraction(int(duration_text), divisions)

    def sort_key(item: tuple[Fraction, int, dict[str, Any]]) -> tuple[Any, ...]:
        onset, order_index, record = item
        return (onset, record["staff"], record["voice"], record["pitch"], order_index)

    return [record for _, _, record in sorted(indexed, key=sort_key)]


def snapshot(path: Path, mode: str) -> dict[str, Any]:
    root = read_root(path)
    if local(root.tag) != "score-partwise":
        raise ValueError(f"{path}: only score-partwise MusicXML is supported")
    names: dict[str, str] = {}
    part_list = first(root, "part-list")
    if part_list is not None:
        for score_part in children(part_list, "score-part"):
            names[score_part.get("id", "")] = text(score_part, "part-name")
    parts = []
    for part_index, part in enumerate(children(root, "part"), start=1):
        state: dict[str, Any] = {"divisions": 1, "key": None, "time": None, "clefs": [], "transpose": None}
        measures = []
        for measure in children(part, "measure"):
            validate_attribute_placement(measure, names.get(part.get("id", ""), ""))
            attribute_state(measure, state)
            measures.append({
                "number": measure.get("number", ""),
                "attributes": {key: value for key, value in state.items() if key != "divisions"},
                "notes": notes_of(measure, state["divisions"], mode),
                "directions": directions_of(measure),
                "harmonies": [signature(node) for node in children(measure, "harmony")],
                "barlines": [signature(node) for node in children(measure, "barline")],
            })
        parts.append({"index": part_index, "name": names.get(part.get("id", ""), ""), "measures": measures})
    return {"parts": parts}


def compare(before: dict[str, Any], after: dict[str, Any], max_diffs: int) -> tuple[list[dict[str, Any]], int]:
    diffs: list[dict[str, Any]] = []
    total = 0

    def add(location: dict[str, Any], field: str, left: Any, right: Any) -> None:
        nonlocal total
        total += 1
        if len(diffs) < max_diffs:
            diffs.append({**location, "field": field, "before": left, "after": right})

    before_parts, after_parts = before["parts"], after["parts"]
    for part_index in range(max(len(before_parts), len(after_parts))):
        left = before_parts[part_index] if part_index < len(before_parts) else None
        right = after_parts[part_index] if part_index < len(after_parts) else None
        if left is None or right is None or left["name"] != right["name"]:
            add({"part_index": part_index + 1}, "part", left and left["name"], right and right["name"])
            continue
        left_measures, right_measures = left["measures"], right["measures"]
        for measure_index in range(max(len(left_measures), len(right_measures))):
            lm = left_measures[measure_index] if measure_index < len(left_measures) else None
            rm = right_measures[measure_index] if measure_index < len(right_measures) else None
            location = {"part": left["name"] or part_index + 1, "measure_index": measure_index + 1, "measure_number": (lm or rm or {}).get("number", "")}
            if lm is None or rm is None:
                add(location, "measure", lm and lm.get("number"), rm and rm.get("number"))
                continue
            if lm["number"] != rm["number"]:
                add(location, "number", lm["number"], rm["number"])
            for field in sorted(set(lm["attributes"]) | set(rm["attributes"])):
                if lm["attributes"].get(field) != rm["attributes"].get(field):
                    add(location, f"attributes.{field}", lm["attributes"].get(field), rm["attributes"].get(field))
            if lm["directions"] != rm["directions"]:
                add(location, "directions", lm["directions"], rm["directions"])
            if lm["harmonies"] != rm["harmonies"]:
                add(location, "harmonies", lm["harmonies"], rm["harmonies"])
            if lm["barlines"] != rm["barlines"]:
                add(location, "barlines", lm["barlines"], rm["barlines"])
            left_notes, right_notes = lm["notes"], rm["notes"]
            if len(left_notes) != len(right_notes):
                add(location, "note_count", len(left_notes), len(right_notes))
            for note_index in range(min(len(left_notes), len(right_notes))):
                ln, rn = left_notes[note_index], right_notes[note_index]
                for field in sorted(set(ln) | set(rn)):
                    if ln.get(field) != rn.get(field):
                        add({**location, "note_index": note_index + 1}, f"note.{field}", ln.get(field), rn.get(field))
    return diffs, total


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("before", type=Path)
    parser.add_argument("after", type=Path)
    parser.add_argument("--mode", choices=("notation", "musical"), default="notation")
    parser.add_argument("--max-diffs", type=int, default=20)
    args = parser.parse_args()
    try:
        before = snapshot(args.before, args.mode)
        after = snapshot(args.after, args.mode)
        diffs, total = compare(before, after, max(0, args.max_diffs))
    except (OSError, ValueError, ET.ParseError, zipfile.BadZipFile) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2))
        return 2
    result = {"ok": total == 0, "mode": args.mode, "difference_count": total, "reported_differences": diffs}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if total == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
