#!/usr/bin/env python3
"""Extract bar-grouped MIDI evidence for AI score interpretation."""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from fractions import Fraction
from pathlib import Path
from typing import Any

from audit_midi import MidiError, make_self_test_midi, meter_segments, parse_midi, pitch_name


def locate_tick(tick: int, segments: list[dict[str, Any]], ppq: int) -> dict[str, Any]:
    segment = segments[0]
    for candidate in segments:
        if candidate["tick"] <= tick:
            segment = candidate
        else:
            break
    offset = Fraction(tick - segment["tick"], 1)
    bars = int(offset / segment["measure_ticks"])
    within = offset - bars * segment["measure_ticks"]
    bar = segment["bar"] + bars
    return {
        "bar": bar,
        "offset_ticks": int(within),
        "offset_quarters": float(within / ppq),
        "beat": float(within / (segment["measure_ticks"] / segment["numerator"])) + 1.0,
    }


def bar_to_tick(bar: int, segments: list[dict[str, Any]]) -> int:
    for index, segment in enumerate(segments):
        next_bar = segments[index + 1]["bar"] if index + 1 < len(segments) else None
        if next_bar is None or bar < next_bar:
            value = Fraction(segment["tick"], 1) + (bar - segment["bar"]) * segment["measure_ticks"]
            if value.denominator != 1:
                raise MidiError(f"bar {bar} does not resolve to an integer tick")
            return int(value)
    raise AssertionError("unreachable")


def extract(parsed: dict[str, Any], source: str, start_bar: int, end_bar: int) -> dict[str, Any]:
    if end_bar < start_bar:
        raise MidiError("end bar must not precede start bar")
    segments, meter_warnings = meter_segments(parsed)
    ppq = parsed["ppq"]
    start_tick = bar_to_tick(start_bar, segments)
    end_tick = bar_to_tick(end_bar + 1, segments)
    notes_by_track: dict[int, list[Any]] = defaultdict(list)
    for note in parsed["notes"]:
        if note.start < end_tick and note.end > start_tick:
            notes_by_track[note.track].append(note)
    controls_by_track: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for event in parsed["controllers"]:
        if start_tick <= event["tick"] < end_tick and event["controller"] in (1, 2, 11, 64):
            controls_by_track[event["track"]].append(event)

    result: dict[str, Any] = {
        "schema": "midi-context-v1",
        "source": source,
        "midi": {"format": parsed["format"], "ppq": ppq},
        "range": {
            "start_bar": start_bar,
            "end_bar_inclusive": end_bar,
            "start_tick": start_tick,
            "end_tick_exclusive": end_tick,
        },
        "global": {
            "time_signatures": [],
            "tempos": [],
            "key_signatures": [],
        },
        "tracks": [],
        "warnings": parsed["warnings"][:] + meter_warnings,
    }

    for key, target in (
        ("time_signatures", "time_signatures"),
        ("tempos", "tempos"),
        ("key_signatures", "key_signatures"),
    ):
        for event in parsed[key]:
            if event["tick"] == 0 or start_tick <= event["tick"] < end_tick:
                result["global"][target].append({**event, **locate_tick(event["tick"], segments, ppq)})

    for track in parsed["tracks"]:
        index0 = track["index"] - 1
        measures: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for note in sorted(notes_by_track[index0], key=lambda item: (item.start, item.pitch, item.end)):
            position = locate_tick(note.start, segments, ppq)
            bucket_bar = min(max(position["bar"], start_bar), end_bar)
            measures[str(bucket_bar)].append(
                {
                    "midi_pitch": note.pitch,
                    "pitch_name_sharp": pitch_name(note.pitch),
                    "channel": note.channel,
                    "velocity": note.velocity,
                    "start_tick": note.start,
                    "end_tick": note.end,
                    "duration_ticks": note.end - note.start,
                    "duration_quarters": (note.end - note.start) / ppq,
                    "bar": position["bar"],
                    "beat": position["beat"],
                    "offset_ticks": position["offset_ticks"],
                    "offset_quarters": position["offset_quarters"],
                    "crosses_excerpt_start": note.start < start_tick,
                    "crosses_excerpt_end": note.end > end_tick,
                    "heuristic_control_note": note.pitch < 24,
                }
            )
        controls = []
        for event in controls_by_track[index0]:
            controls.append({**event, **locate_tick(event["tick"], segments, ppq)})
        track_result = {
            "index": track["index"],
            "name": track["name"],
            "channels": track["channels"],
            "source_note_count": track["note_count"],
            "notes_in_excerpt": sum(len(items) for items in measures.values()),
            "measures": dict(measures),
            "controllers": controls,
            "anomalies": {
                "overlapping_same_pitch": track["overlapping_same_pitch"],
                "unmatched_note_off": track["unmatched_note_off"],
                "dangling_note_on": track["dangling_note_on"],
            },
        }
        result["tracks"].append(track_result)
    return result


def self_test() -> None:
    parsed = parse_midi(make_self_test_midi())
    context = extract(parsed, "self-test.mid", 1, 1)
    piano = context["tracks"][1]
    assert piano["name"] == "Piano"
    assert piano["measures"]["1"][0]["midi_pitch"] == 60
    assert piano["measures"]["1"][0]["duration_quarters"] == 1.0
    assert piano["controllers"][0]["controller"] == 64
    print("self-test passed")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("midi", nargs="?", type=Path)
    parser.add_argument("--start-bar", type=int, default=1)
    parser.add_argument("--end-bar", type=int)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return 0
    if args.midi is None:
        parser.error("midi path is required unless --self-test is used")
    try:
        parsed = parse_midi(args.midi.read_bytes())
        segments, _ = meter_segments(parsed)
        if args.end_bar is None:
            max_tick = max((track["end_tick"] for track in parsed["tracks"]), default=0)
            end_bar = locate_tick(max_tick, segments, parsed["ppq"])["bar"]
        else:
            end_bar = args.end_bar
        context = extract(parsed, str(args.midi.resolve()), args.start_bar, end_bar)
        rendered = json.dumps(context, ensure_ascii=False, indent=2) + "\n"
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(rendered, encoding="utf-8")
        else:
            print(rendered, end="")
    except (OSError, MidiError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
