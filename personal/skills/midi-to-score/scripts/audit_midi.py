#!/usr/bin/env python3
"""Audit a Standard MIDI File before engraving it as a score.

Uses only the Python standard library. Bar numbers are one-based and
--end-bar is inclusive.
"""

from __future__ import annotations

import argparse
import json
import struct
import sys
from collections import defaultdict
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Any


class MidiError(ValueError):
    pass


@dataclass
class Note:
    track: int
    channel: int
    pitch: int
    velocity: int
    start: int
    end: int


def read_vlq(data: bytes, pos: int) -> tuple[int, int]:
    value = 0
    for _ in range(4):
        if pos >= len(data):
            raise MidiError("truncated variable-length quantity")
        byte = data[pos]
        pos += 1
        value = (value << 7) | (byte & 0x7F)
        if byte < 0x80:
            return value, pos
    raise MidiError("invalid variable-length quantity")


def write_vlq(value: int) -> bytes:
    parts = [value & 0x7F]
    value >>= 7
    while value:
        parts.append(0x80 | (value & 0x7F))
        value >>= 7
    return bytes(reversed(parts))


def signed_byte(value: int) -> int:
    return value - 256 if value >= 128 else value


def parse_midi(data: bytes) -> dict[str, Any]:
    if data[:4] != b"MThd" or len(data) < 14:
        raise MidiError("not a Standard MIDI File")
    header_len = struct.unpack(">I", data[4:8])[0]
    if header_len < 6 or len(data) < 8 + header_len:
        raise MidiError("invalid MIDI header")
    fmt, declared_tracks, division = struct.unpack(">HHH", data[8:14])
    if division & 0x8000:
        raise MidiError("SMPTE time division is not supported; export PPQ MIDI")
    ppq = division
    pos = 8 + header_len
    tracks: list[dict[str, Any]] = []
    tempos: list[dict[str, Any]] = []
    signatures: list[dict[str, Any]] = []
    keys: list[dict[str, Any]] = []
    notes: list[Note] = []
    controllers: list[dict[str, Any]] = []
    programs: list[dict[str, Any]] = []
    warnings: list[str] = []

    while pos + 8 <= len(data) and len(tracks) < declared_tracks:
        chunk_type = data[pos : pos + 4]
        chunk_len = struct.unpack(">I", data[pos + 4 : pos + 8])[0]
        pos += 8
        chunk = data[pos : pos + chunk_len]
        pos += chunk_len
        if chunk_type != b"MTrk":
            warnings.append(f"skipped non-track chunk {chunk_type!r}")
            continue

        track_index = len(tracks)
        tpos = 0
        tick = 0
        running: int | None = None
        name = ""
        active: dict[tuple[int, int], list[tuple[int, int]]] = defaultdict(list)
        overlap_count = 0
        unmatched_off = 0
        track_channels: set[int] = set()
        note_count = 0

        while tpos < len(chunk):
            delta, tpos = read_vlq(chunk, tpos)
            tick += delta
            if tpos >= len(chunk):
                raise MidiError(f"track {track_index + 1}: missing event after delta")
            first = chunk[tpos]
            if first & 0x80:
                status = first
                tpos += 1
                if status < 0xF0:
                    running = status
            elif running is not None:
                status = running
            else:
                raise MidiError(f"track {track_index + 1}: running status without status byte")

            if status == 0xFF:
                if tpos >= len(chunk):
                    raise MidiError("truncated meta event")
                meta_type = chunk[tpos]
                tpos += 1
                length, tpos = read_vlq(chunk, tpos)
                payload = chunk[tpos : tpos + length]
                if len(payload) != length:
                    raise MidiError("truncated meta payload")
                tpos += length
                running = None
                if meta_type == 0x03:
                    name = payload.decode("utf-8", errors="replace")
                elif meta_type == 0x51 and length == 3:
                    micros = int.from_bytes(payload, "big")
                    if micros:
                        tempos.append({"tick": tick, "bpm": round(60_000_000 / micros, 6)})
                elif meta_type == 0x58 and length >= 2:
                    signatures.append(
                        {"tick": tick, "numerator": payload[0], "denominator": 2 ** payload[1]}
                    )
                elif meta_type == 0x59 and length >= 2:
                    keys.append({"tick": tick, "fifths": signed_byte(payload[0]), "minor": bool(payload[1])})
                if meta_type == 0x2F:
                    break
                continue

            if status in (0xF0, 0xF7):
                length, tpos = read_vlq(chunk, tpos)
                tpos += length
                running = None
                continue
            if status >= 0xF0:
                raise MidiError(f"unsupported system event 0x{status:02X}")

            kind = status & 0xF0
            channel = status & 0x0F
            needed = 1 if kind in (0xC0, 0xD0) else 2
            payload = chunk[tpos : tpos + needed]
            if len(payload) != needed:
                raise MidiError("truncated channel event")
            tpos += needed
            track_channels.add(channel + 1)

            if kind == 0x90 and payload[1] > 0:
                key = (channel, payload[0])
                if active[key]:
                    overlap_count += 1
                active[key].append((tick, payload[1]))
            elif kind == 0x80 or (kind == 0x90 and payload[1] == 0):
                key = (channel, payload[0])
                if active[key]:
                    start, velocity = active[key].pop(0)
                    notes.append(Note(track_index, channel + 1, payload[0], velocity, start, tick))
                    note_count += 1
                else:
                    unmatched_off += 1
            elif kind == 0xB0:
                controllers.append(
                    {"track": track_index, "tick": tick, "channel": channel + 1, "controller": payload[0], "value": payload[1]}
                )
            elif kind == 0xC0:
                programs.append(
                    {"track": track_index, "tick": tick, "channel": channel + 1, "program": payload[0]}
                )

        dangling = sum(len(values) for values in active.values())
        tracks.append(
            {
                "index": track_index + 1,
                "name": name,
                "end_tick": tick,
                "channels": sorted(track_channels),
                "note_count": note_count,
                "overlapping_same_pitch": overlap_count,
                "unmatched_note_off": unmatched_off,
                "dangling_note_on": dangling,
            }
        )

    if len(tracks) != declared_tracks:
        warnings.append(f"header declares {declared_tracks} tracks but parsed {len(tracks)}")
    return {
        "format": fmt,
        "declared_tracks": declared_tracks,
        "ppq": ppq,
        "tracks": tracks,
        "tempos": sorted(tempos, key=lambda item: item["tick"]),
        "time_signatures": sorted(signatures, key=lambda item: item["tick"]),
        "key_signatures": sorted(keys, key=lambda item: item["tick"]),
        "notes": notes,
        "controllers": controllers,
        "program_changes": programs,
        "warnings": warnings,
    }


def meter_segments(parsed: dict[str, Any]) -> tuple[list[dict[str, Any]], list[str]]:
    ppq = parsed["ppq"]
    source = parsed["time_signatures"][:]
    warnings: list[str] = []
    if not source or source[0]["tick"] != 0:
        source.insert(0, {"tick": 0, "numerator": 4, "denominator": 4})
        warnings.append("no time signature at tick 0; assumed 4/4")
    deduped: list[dict[str, Any]] = []
    for item in source:
        if deduped and item["tick"] == deduped[-1]["tick"]:
            deduped[-1] = item
        else:
            deduped.append(item)

    segments: list[dict[str, Any]] = []
    bar = 1
    for index, item in enumerate(deduped):
        tick = item["tick"]
        measure_ticks = Fraction(ppq * 4 * item["numerator"], item["denominator"])
        next_tick = deduped[index + 1]["tick"] if index + 1 < len(deduped) else None
        segment = {
            "tick": tick,
            "bar": bar,
            "numerator": item["numerator"],
            "denominator": item["denominator"],
            "measure_ticks": measure_ticks,
            "next_tick": next_tick,
        }
        segments.append(segment)
        if next_tick is not None:
            span = Fraction(next_tick - tick, 1)
            measures = span / measure_ticks
            if measures.denominator != 1:
                warnings.append(
                    f"time-signature change at tick {next_tick} is not on a complete {item['numerator']}/{item['denominator']} bar boundary"
                )
            bar += int(measures)
    return segments, warnings


def bar_to_tick(bar: int, segments: list[dict[str, Any]]) -> int:
    if bar < 1:
        raise MidiError("bar numbers must be positive")
    for index, segment in enumerate(segments):
        next_bar = segments[index + 1]["bar"] if index + 1 < len(segments) else None
        if next_bar is None or bar < next_bar:
            value = Fraction(segment["tick"], 1) + (bar - segment["bar"]) * segment["measure_ticks"]
            if value.denominator != 1:
                raise MidiError(f"bar {bar} does not resolve to an integer tick")
            return int(value)
    raise AssertionError("unreachable")


def tick_to_bar(tick: int, segments: list[dict[str, Any]]) -> str:
    segment = segments[0]
    for candidate in segments:
        if candidate["tick"] <= tick:
            segment = candidate
        else:
            break
    offset = Fraction(tick - segment["tick"], 1)
    bars = int(offset / segment["measure_ticks"])
    within = offset - bars * segment["measure_ticks"]
    beat_ticks = Fraction(segment["measure_ticks"], segment["numerator"])
    beat = int(within / beat_ticks) + 1
    return f"{segment['bar'] + bars}.{beat}"


def pitch_name(pitch: int) -> str:
    names = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")
    return f"{names[pitch % 12]}{pitch // 12 - 1}"


def build_report(parsed: dict[str, Any], start_bar: int, end_bar: int) -> dict[str, Any]:
    if end_bar < start_bar:
        raise MidiError("end bar must not precede start bar")
    segments, meter_warnings = meter_segments(parsed)
    start_tick = bar_to_tick(start_bar, segments)
    end_tick = bar_to_tick(end_bar + 1, segments)
    report: dict[str, Any] = {
        "format": parsed["format"],
        "ppq": parsed["ppq"],
        "range": {
            "start_bar": start_bar,
            "end_bar_inclusive": end_bar,
            "start_tick": start_tick,
            "end_tick_exclusive": end_tick,
        },
        "time_signatures": [],
        "tempos": [],
        "key_signatures": [],
        "tracks": [],
        "warnings": parsed["warnings"][:] + meter_warnings,
    }
    if parsed["format"] != 1:
        report["warnings"].append("file is not Type 1 multitrack MIDI")
    if not parsed["key_signatures"]:
        report["warnings"].append("no key-signature events found")

    for item in parsed["time_signatures"]:
        if start_tick <= item["tick"] < end_tick or item["tick"] == 0:
            report["time_signatures"].append(
                {**item, "bar_beat": tick_to_bar(item["tick"], segments)}
            )
    for item in parsed["tempos"]:
        if start_tick <= item["tick"] < end_tick or item["tick"] == 0:
            report["tempos"].append({**item, "bar_beat": tick_to_bar(item["tick"], segments)})
    for item in parsed["key_signatures"]:
        if start_tick <= item["tick"] < end_tick or item["tick"] == 0:
            report["key_signatures"].append(
                {**item, "bar_beat": tick_to_bar(item["tick"], segments)}
            )
    in_range_tempos = [item for item in parsed["tempos"] if start_tick <= item["tick"] < end_tick]
    if len(in_range_tempos) > 8:
        report["warnings"].append(
            f"dense tempo map: {len(in_range_tempos)} tempo events in requested range; engrave as musical ramps/anchors"
        )

    notes_by_track: dict[int, list[Note]] = defaultdict(list)
    for note in parsed["notes"]:
        notes_by_track[note.track].append(note)
    controllers_by_track: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for controller in parsed["controllers"]:
        controllers_by_track[controller["track"]].append(controller)

    for track in parsed["tracks"]:
        index0 = track["index"] - 1
        track_notes = notes_by_track[index0]
        in_range = [note for note in track_notes if note.start < end_tick and note.end > start_tick]
        starts_before = sum(note.start < start_tick < note.end for note in track_notes)
        ends_after = sum(note.start < end_tick < note.end for note in track_notes)
        pedal = [
            event
            for event in controllers_by_track[index0]
            if event["controller"] == 64 and start_tick <= event["tick"] < end_tick
        ]
        heuristic_control_notes = [note for note in in_range if note.pitch < 24]
        item = {
            **track,
            "notes_in_range": len(in_range),
            "range": None,
            "first_note": None,
            "last_note_end": None,
            "notes_crossing_start": starts_before,
            "notes_crossing_end": ends_after,
            "cc64_events_in_range": len(pedal),
            "heuristic_control_notes_below_c1": len(heuristic_control_notes),
        }
        if in_range:
            low = min(note.pitch for note in in_range)
            high = max(note.pitch for note in in_range)
            item["range"] = f"{pitch_name(low)}-{pitch_name(high)}"
            item["first_note"] = tick_to_bar(min(note.start for note in in_range), segments)
            item["last_note_end"] = tick_to_bar(max(note.end for note in in_range), segments)
        if not track["name"]:
            report["warnings"].append(f"track {track['index']} has no track name")
        if track["note_count"] and not in_range:
            report["warnings"].append(f"track {track['index']} ({track['name'] or 'unnamed'}) has no notes in requested range")
        if track["overlapping_same_pitch"]:
            report["warnings"].append(
                f"track {track['index']} ({track['name'] or 'unnamed'}) has {track['overlapping_same_pitch']} overlapping same-pitch note-ons"
            )
        if starts_before or ends_after:
            report["warnings"].append(
                f"track {track['index']} ({track['name'] or 'unnamed'}) has notes crossing an excerpt boundary"
            )
        if track["dangling_note_on"] or track["unmatched_note_off"]:
            report["warnings"].append(
                f"track {track['index']} ({track['name'] or 'unnamed'}) has unmatched note events"
            )
        if heuristic_control_notes:
            pitches = sorted({pitch_name(note.pitch) for note in heuristic_control_notes})
            report["warnings"].append(
                f"track {track['index']} ({track['name'] or 'unnamed'}) has {len(heuristic_control_notes)} notes below C1 "
                f"({', '.join(pitches)}); classify likely keyswitch/control notes before scoring"
            )
        report["tracks"].append(item)

    for left_index in range(len(parsed["tracks"])):
        left = {
            (note.start, note.end, note.pitch)
            for note in notes_by_track[left_index]
            if note.start < end_tick and note.end > start_tick
        }
        if len(left) < 20:
            continue
        for right_index in range(left_index + 1, len(parsed["tracks"])):
            right = {
                (note.start, note.end, note.pitch)
                for note in notes_by_track[right_index]
                if note.start < end_tick and note.end > start_tick
            }
            if len(right) < 20:
                continue
            overlap = len(left & right)
            ratio = overlap / min(len(left), len(right))
            if overlap >= 20 and ratio >= 0.5:
                left_name = parsed["tracks"][left_index]["name"] or f"track {left_index + 1}"
                right_name = parsed["tracks"][right_index]["name"] or f"track {right_index + 1}"
                report["warnings"].append(
                    f"possible doubled/guide material: {left_name} and {right_name} share {overlap} exact notes "
                    f"({ratio:.0%} of the smaller set); decide whether to merge, retain, or exclude"
                )

    if parsed["program_changes"]:
        report["warnings"].append(
            f"{len(parsed['program_changes'])} program-change events found; verify them separately because Studio One MIDI export may not preserve all program changes"
        )
    return report


def render_text(report: dict[str, Any]) -> str:
    lines = [
        f"MIDI format {report['format']} | PPQ {report['ppq']}",
        f"Range: bars {report['range']['start_bar']}-{report['range']['end_bar_inclusive']} inclusive "
        f"(ticks {report['range']['start_tick']}..{report['range']['end_tick_exclusive']})",
    ]
    meters = ", ".join(
        f"{item['numerator']}/{item['denominator']}@{item['bar_beat']}" for item in report["time_signatures"]
    ) or "none"
    tempo_items = [f"{item['bpm']:g}@{item['bar_beat']}" for item in report["tempos"]]
    if len(tempo_items) > 12:
        tempos = ", ".join(tempo_items[:5] + [f"... {len(tempo_items) - 10} more ..."] + tempo_items[-5:])
    else:
        tempos = ", ".join(tempo_items) or "none"
    lines.extend([f"Meters: {meters}", f"Tempos: {tempos}", "Tracks:"])
    for track in report["tracks"]:
        name = track["name"] or "unnamed"
        lines.append(
            f"  {track['index']:>2}. {name}: {track['notes_in_range']} notes, "
            f"range {track['range'] or '-'}, channels {track['channels'] or '-'}, "
            f"CC64 {track['cc64_events_in_range']}, control-note heuristic {track['heuristic_control_notes_below_c1']}"
        )
    if report["warnings"]:
        lines.append("Warnings:")
        lines.extend(f"  - {warning}" for warning in report["warnings"])
    else:
        lines.append("Warnings: none")
    return "\n".join(lines)


def make_self_test_midi() -> bytes:
    header = b"MThd" + struct.pack(">IHHH", 6, 1, 2, 480)
    conductor = (
        b"\x00\xff\x03\x09Conductor"
        b"\x00\xff\x58\x04\x04\x02\x18\x08"
        b"\x00\xff\x51\x03\x07\xa1\x20"
        b"\x00\xff\x2f\x00"
    )
    piano = (
        b"\x00\xff\x03\x05Piano"
        b"\x00\x90\x3c\x50"
        + write_vlq(480)
        + b"\x80\x3c\x00"
        + b"\x00\xb0\x40\x7f"
        + b"\x00\xff\x2f\x00"
    )
    return header + b"MTrk" + struct.pack(">I", len(conductor)) + conductor + b"MTrk" + struct.pack(">I", len(piano)) + piano


def self_test() -> None:
    parsed = parse_midi(make_self_test_midi())
    report = build_report(parsed, 1, 1)
    assert report["format"] == 1
    assert report["tracks"][1]["name"] == "Piano"
    assert report["tracks"][1]["notes_in_range"] == 1
    assert report["tracks"][1]["range"] == "C4-C4"
    assert report["tracks"][1]["cc64_events_in_range"] == 1
    print("self-test passed")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("midi", nargs="?", type=Path)
    parser.add_argument("--start-bar", type=int, default=1)
    parser.add_argument("--end-bar", type=int)
    parser.add_argument("--json", action="store_true", dest="as_json")
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
        max_tick = max((track["end_tick"] for track in parsed["tracks"]), default=0)
        if args.end_bar is None:
            end_bar = int(tick_to_bar(max_tick, segments).split(".")[0])
        else:
            end_bar = args.end_bar
        report = build_report(parsed, args.start_bar, end_bar)
    except (OSError, MidiError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    if args.as_json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(render_text(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
