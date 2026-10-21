#!/usr/bin/env python3
"""Forensic comparison of an original, a target render, and a current render.

The analysis separates intended slow gain changes from waveform residue, audits
gain-reduction dynamics, stereo stability, spectral coherence/transfer, and
creates machine-readable evidence plus plots and listening excerpts.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import re
import shutil
import subprocess
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import soundfile as sf
from scipy import ndimage, signal


EPS = 1.0e-30
ROLE_COLORS = {
    "Original": "#d8d8d8",
    "Target": "#a8d36f",
    "Current": "#e58c8c",
}


def db(value: float | np.ndarray) -> float | np.ndarray:
    return 20.0 * np.log10(np.maximum(np.asarray(value), EPS))


def rms(value: np.ndarray, axis=None) -> float | np.ndarray:
    result = np.sqrt(np.mean(np.square(value, dtype=np.float64), axis=axis))
    return float(result) if np.ndim(result) == 0 else result


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    fields: list[str] = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    with path.open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def ffmpeg_metrics(path: Path) -> tuple[dict, list[str]]:
    warnings: list[str] = []
    executable = shutil.which("ffmpeg")
    if executable is None:
        return {
            "integrated_lufs": None,
            "lra_lu": None,
            "ffmpeg_true_peak_dbtp": None,
            "precise_integrated_lufs": None,
            "precise_lra_lu": None,
            "loudnorm_true_peak_dbtp": None,
        }, ["ffmpeg was not found; LUFS/LRA metadata is unavailable"]

    common = [executable, "-hide_banner", "-nostats", "-i", str(path)]
    process = subprocess.run(
        common + ["-filter_complex", "ebur128=peak=true", "-f", "null", "-"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    text = process.stdout + "\n" + process.stderr
    integrated = re.findall(
        r"^\s+I:\s+(-?\d+(?:\.\d+)?)\s+LUFS", text, re.MULTILINE
    )
    lra = re.findall(r"^\s+LRA:\s+(-?\d+(?:\.\d+)?)\s+LU", text, re.MULTILINE)
    peak = re.findall(
        r"^\s+Peak:\s+(-?\d+(?:\.\d+)?)\s+dBFS", text, re.MULTILINE
    )

    process2 = subprocess.run(
        common
        + [
            "-af",
            "loudnorm=I=-23:TP=-1:LRA=7:print_format=json",
            "-f",
            "null",
            "-",
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    text2 = process2.stdout + "\n" + process2.stderr

    def loudnorm_value(key: str) -> float | None:
        match = re.search(rf'"{key}"\s*:\s*"?(-?\d+(?:\.\d+)?)', text2)
        return float(match.group(1)) if match else None

    if not integrated:
        warnings.append(f"ffmpeg ebur128 summary could not be parsed for {path}")
    if loudnorm_value("input_i") is None:
        warnings.append(f"ffmpeg loudnorm summary could not be parsed for {path}")
    return {
        "integrated_lufs": float(integrated[-1]) if integrated else None,
        "lra_lu": float(lra[-1]) if lra else None,
        "ffmpeg_true_peak_dbtp": float(peak[-1]) if peak else None,
        "precise_integrated_lufs": loudnorm_value("input_i"),
        "precise_lra_lu": loudnorm_value("input_lra"),
        "loudnorm_true_peak_dbtp": loudnorm_value("input_tp"),
    }, warnings


def true_peak_chunked(
    data: np.ndarray,
    factor: int = 32,
    chunk_frames: int = 131072,
    overlap_frames: int = 64,
) -> tuple[float, list[float]]:
    peaks = np.zeros(data.shape[1], dtype=np.float64)
    total = data.shape[0]
    for start in range(0, total, chunk_frames):
        stop = min(total, start + chunk_frames)
        left = max(0, start - overlap_frames)
        right = min(total, stop + overlap_frames)
        reconstructed = signal.resample_poly(
            data[left:right], factor, 1, axis=0, window=("kaiser", 12.0)
        )
        keep_start = (start - left) * factor
        keep_stop = keep_start + (stop - start) * factor
        # Reject only the outer reconstruction startup/shutdown support.
        if start == 0:
            keep_start += min(24 * factor, max(0, keep_stop - keep_start - 1))
        if stop == total:
            keep_stop -= min(24 * factor, max(0, keep_stop - keep_start - 1))
        if keep_stop > keep_start:
            peaks = np.maximum(
                peaks, np.max(np.abs(reconstructed[keep_start:keep_stop]), axis=0)
            )
    return float(db(np.max(peaks))), [float(db(value)) for value in peaks]


def normalized_correlation(x: np.ndarray, y: np.ndarray) -> float:
    numerator = float(np.sum(x * y, dtype=np.float64))
    denominator = math.sqrt(
        float(np.sum(x * x, dtype=np.float64))
        * float(np.sum(y * y, dtype=np.float64))
        + EPS
    )
    return numerator / denominator


def estimate_delay(
    x: np.ndarray, y: np.ndarray, sample_rate: int, maximum_lag: int
) -> tuple[dict, dict]:
    decimation = max(1, int(math.ceil(max(x.shape[0], y.shape[0]) / 1_500_000)))
    xm = np.diff(np.mean(x, axis=1))[::decimation]
    ym = np.diff(np.mean(y, axis=1))[::decimation]
    correlation = signal.correlate(ym, xm, mode="full", method="fft")
    lags = signal.correlation_lags(ym.size, xm.size, mode="full")
    bound = math.ceil(maximum_lag / decimation)
    keep = (lags >= -bound) & (lags <= bound)
    coarse_lag = int(lags[keep][np.argmax(np.abs(correlation[keep]))]) * decimation

    span = min(x.shape[0] // 5, max(sample_rate * 10, sample_rate))
    centres = (x.shape[0] // 4, x.shape[0] // 2, 3 * x.shape[0] // 4)
    spans = [
        (max(1, centre - span // 2), min(x.shape[0] - 1, centre + span // 2))
        for centre in centres
    ]
    candidates = np.arange(coarse_lag - 16, coarse_lag + 17, dtype=np.int64)
    scores = np.zeros(candidates.size, dtype=np.float64)
    for index, lag in enumerate(candidates):
        for start, stop in spans:
            if lag >= 0:
                xx = np.diff(np.mean(x[start : stop - lag], axis=1))
                yy = np.diff(np.mean(y[start + lag : stop], axis=1))
            else:
                advance = -int(lag)
                xx = np.diff(np.mean(x[start + advance : stop], axis=1))
                yy = np.diff(np.mean(y[start : stop - advance], axis=1))
            if xx.size:
                scores[index] += float(np.dot(xx, yy))
    best = int(np.argmax(np.abs(scores)))
    lag = int(candidates[best])
    polarity = 1 if scores[best] >= 0.0 else -1
    fractional = float(lag)
    if 0 < best < scores.size - 1:
        left, centre, right = np.abs(scores[best - 1 : best + 2])
        denominator = left - 2.0 * centre + right
        if abs(denominator) > EPS:
            fractional += 0.5 * (left - right) / denominator

    if lag >= 0:
        xa = x[: x.shape[0] - lag or None]
        ya = y[lag:] * polarity
    else:
        advance = -lag
        xa = x[advance:]
        ya = y[: y.shape[0] - advance] * polarity
    trace_scale = max(float(np.max(np.abs(scores))), EPS)
    trace = {
        "lags": candidates.astype(float),
        "scores": scores / trace_scale,
    }
    return {
        "output_delay_samples": lag,
        "fractional_delay_samples": fractional,
        "fractional_remainder_samples": fractional - lag,
        "polarity": polarity,
        "aligned_correlation_integer": normalized_correlation(xa, ya),
        "coarse_decimation": decimation,
    }, trace


def fractional_advance_sinc(data: np.ndarray, advance: float, radius: int = 64):
    # Output[n] = input[n + advance]. The FIR therefore has delay -advance.
    offsets = np.arange(-radius, radius + 1, dtype=np.float64)
    kernel = np.sinc(offsets + advance) * np.kaiser(offsets.size, 12.0)
    kernel /= np.sum(kernel)
    output = np.empty_like(data)
    for channel in range(data.shape[1]):
        output[:, channel] = signal.fftconvolve(
            data[:, channel], kernel, mode="same"
        )
    return output, radius + 2


def align_to_source(
    data: np.ndarray,
    alignment: dict,
    fractional_mode: str,
) -> tuple[np.ndarray, np.ndarray]:
    lag = int(alignment["output_delay_samples"])
    polarity = int(alignment["polarity"])
    aligned = np.zeros_like(data)
    valid = np.zeros(data.shape[0], dtype=bool)
    if lag == 0:
        aligned[:] = data * polarity
        valid[:] = True
    elif lag > 0:
        aligned[:-lag] = data[lag:] * polarity
        valid[:-lag] = True
    else:
        advance = -lag
        aligned[advance:] = data[:-advance] * polarity
        valid[advance:] = True

    remainder = float(alignment["fractional_remainder_samples"])
    if fractional_mode == "sinc" and abs(remainder) >= 1.0e-5:
        aligned, margin = fractional_advance_sinc(aligned, remainder)
        valid[:margin] = False
        valid[-margin:] = False
        alignment["fractional_alignment_applied"] = True
        alignment["fractional_alignment_radius"] = margin - 2
    else:
        alignment["fractional_alignment_applied"] = False
        alignment["fractional_alignment_radius"] = 0
    return aligned, valid


def valid_mask(
    source: np.ndarray,
    sample_rate: int,
    alignment_valid: np.ndarray,
    threshold_dbfs: float,
    edge_ms: float,
) -> np.ndarray:
    window = max(1, round(0.010 * sample_rate))
    power = ndimage.uniform_filter1d(
        np.mean(source * source, axis=1), size=window, mode="nearest"
    )
    mask = power > 10.0 ** (threshold_dbfs / 10.0)
    mask &= alignment_valid
    edge = min(source.shape[0] // 4, round(edge_ms * 0.001 * sample_rate))
    if edge:
        mask[:edge] = False
        mask[-edge:] = False
    if not np.any(mask):
        raise RuntimeError("No valid programme remains after silence/alignment masking")
    return mask


def local_common_gain(x: np.ndarray, y: np.ndarray, window: int) -> np.ndarray:
    product = np.sum(x * y, axis=1, dtype=np.float64)
    power = np.sum(x * x, axis=1, dtype=np.float64)
    numerator = ndimage.uniform_filter1d(product, size=window, mode="nearest")
    denominator = ndimage.uniform_filter1d(power, size=window, mode="nearest")
    return numerator / np.maximum(denominator, EPS)


def local_channel_gain(x: np.ndarray, y: np.ndarray, window: int) -> np.ndarray:
    output = np.empty_like(x, dtype=np.float64)
    for channel in range(x.shape[1]):
        numerator = ndimage.uniform_filter1d(
            x[:, channel] * y[:, channel], size=window, mode="nearest"
        )
        denominator = ndimage.uniform_filter1d(
            x[:, channel] * x[:, channel], size=window, mode="nearest"
        )
        output[:, channel] = numerator / np.maximum(denominator, EPS)
    return output


def residual_metrics(
    x: np.ndarray,
    y: np.ndarray,
    sample_rate: int,
    mask: np.ndarray,
    window_ms: float,
) -> tuple[dict, np.ndarray, np.ndarray]:
    window = max(1, round(window_ms * 0.001 * sample_rate))
    gain = local_common_gain(x, y, window)
    residual = y - gain[:, None] * x
    output_rms = max(float(rms(y[mask])), EPS)
    source_rms = max(float(rms(x[mask])), EPS)
    residual_rms = float(rms(residual[mask]))
    return {
        "window_ms": window_ms,
        "residual_percent_of_output": 100.0 * residual_rms / output_rms,
        "residual_percent_of_source": 100.0 * residual_rms / source_rms,
        "residual_db_below_output": float(db(residual_rms / output_rms)),
        "sdr_db": float(-db(residual_rms / output_rms)),
        "gain_db_p05": float(np.percentile(db(np.abs(gain[mask])), 5)),
        "gain_db_median": float(np.median(db(np.abs(gain[mask])))),
        "gain_db_p95": float(np.percentile(db(np.abs(gain[mask])), 95)),
    }, gain, residual


def longest_true_run(mask: np.ndarray) -> slice:
    padded = np.r_[False, mask, False]
    changes = np.flatnonzero(padded[1:] != padded[:-1])
    starts, stops = changes[::2], changes[1::2]
    if starts.size == 0:
        return slice(0, mask.size)
    index = int(np.argmax(stops - starts))
    return slice(int(starts[index]), int(stops[index]))


def spectral_metrics(
    x: np.ndarray,
    y: np.ndarray,
    residual: np.ndarray,
    sample_rate: int,
    mask: np.ndarray,
    fft_size: int,
) -> tuple[list[dict], dict]:
    region = longest_true_run(mask)
    xx, yy, ee = x[region], y[region], residual[region]
    nperseg = min(fft_size, max(256, xx.shape[0]))
    noverlap = nperseg // 2
    pxx = pyy = pee = pxy = None
    frequencies = None
    for channel in range(x.shape[1]):
        f, source_psd = signal.welch(
            xx[:, channel], sample_rate, nperseg=nperseg,
            noverlap=noverlap, window="hann"
        )
        _, output_psd = signal.welch(
            yy[:, channel], sample_rate, nperseg=nperseg,
            noverlap=noverlap, window="hann"
        )
        _, residual_psd = signal.welch(
            ee[:, channel], sample_rate, nperseg=nperseg,
            noverlap=noverlap, window="hann"
        )
        _, cross_psd = signal.csd(
            xx[:, channel], yy[:, channel], sample_rate, nperseg=nperseg,
            noverlap=noverlap, window="hann"
        )
        frequencies = f
        pxx = source_psd if pxx is None else pxx + source_psd
        pyy = output_psd if pyy is None else pyy + output_psd
        pee = residual_psd if pee is None else pee + residual_psd
        pxy = cross_psd if pxy is None else pxy + cross_psd
    coherence = np.abs(pxy) ** 2 / np.maximum(pxx * pyy, EPS)
    transfer = pxy / np.maximum(pxx, EPS)
    transfer_db = db(np.abs(transfer))
    phase_deg = np.unwrap(np.angle(transfer)) * 180.0 / math.pi
    source_reliable = pxx >= np.max(pxx) * 1.0e-8
    reliable = source_reliable & (coherence >= 0.90)
    nyquist = sample_rate * 0.5
    edges = [20, 60, 200, 500, 2000, 5000, 8000, 12000, 16000, 20000]
    edges = [value for value in edges if value < nyquist * 0.98]
    edges.append(nyquist * 0.98)
    rows: list[dict] = []
    for low, high in zip(edges[:-1], edges[1:]):
        band = (frequencies >= low) & (frequencies < high)
        good = band & reliable
        if not np.any(band):
            continue
        selected = good if np.any(good) else band
        rows.append({
            "band_hz": f"{low:g}-{high:g}",
            "median_coherence": float(np.median(coherence[band])),
            "p10_coherence": float(np.percentile(coherence[band], 10)),
            "reliable_bin_fraction": float(np.mean(good[band])),
            "transfer_median_db": float(np.median(transfer_db[selected])),
            "transfer_p05_db": float(np.percentile(transfer_db[selected], 5)),
            "transfer_p95_db": float(np.percentile(transfer_db[selected], 95)),
            "residual_energy_percent": float(100.0 * math.sqrt(
                float(np.sum(pee[band])) / max(float(np.sum(pyy[band])), EPS)
            )),
        })
    curves = {
        "frequency_hz": frequencies,
        "coherence": coherence,
        "transfer_db": transfer_db,
        "phase_deg": phase_deg,
        "residual_output_psd_db": 10.0 * np.log10(
            np.maximum(pee / np.maximum(pyy, EPS), EPS)
        ),
        "reliable": reliable,
    }
    return rows, curves


def stereo_metrics(
    x: np.ndarray, y: np.ndarray, sample_rate: int, mask: np.ndarray
) -> tuple[dict | None, dict | None]:
    if x.shape[1] < 2:
        return None, None

    def width(data: np.ndarray, selected: np.ndarray) -> float:
        mid = (data[:, 0] + data[:, 1]) * 0.5
        side = (data[:, 0] - data[:, 1]) * 0.5
        return float(db(float(rms(side[selected])) / max(float(rms(mid[selected])), EPS)))

    window = max(1, round(0.050 * sample_rate))
    hop = max(1, round(0.010 * sample_rate))
    times, changes = [], []
    for start in range(0, x.shape[0] - window + 1, hop):
        stop = start + window
        local = mask[start:stop]
        if np.mean(local) < 0.80:
            continue
        changes.append(width(y[start:stop], local) - width(x[start:stop], local))
        times.append((start + window * 0.5) / sample_rate)
    changes_array = np.asarray(changes, dtype=np.float64)
    source_corr = float(np.corrcoef(x[mask, 0], x[mask, 1])[0, 1])
    output_corr = float(np.corrcoef(y[mask, 0], y[mask, 1])[0, 1])
    source_width = width(x, mask)
    output_width = width(y, mask)
    channel_gain = local_channel_gain(x[:, :2], y[:, :2], round(0.010 * sample_rate))
    mismatch = db(np.abs(channel_gain[:, 0])) - db(np.abs(channel_gain[:, 1]))
    if changes_array.size:
        largest = int(np.argmax(np.abs(changes_array)))
        local_stats = {
            "local_width_change_median_db": float(np.median(changes_array)),
            "local_width_change_p95_abs_db": float(np.percentile(np.abs(changes_array), 95)),
            "local_width_change_max_abs_db": float(np.max(np.abs(changes_array))),
            "local_width_change_max_time_s": float(times[largest]),
        }
    else:
        local_stats = {
            "local_width_change_median_db": None,
            "local_width_change_p95_abs_db": None,
            "local_width_change_max_abs_db": None,
            "local_width_change_max_time_s": None,
        }
    return {
        "source_lr_correlation": source_corr,
        "output_lr_correlation": output_corr,
        "source_side_mid_db": source_width,
        "output_side_mid_db": output_width,
        "side_mid_change_db": output_width - source_width,
        "local_lr_gain_mismatch_p95_abs_db": float(np.percentile(np.abs(mismatch[mask]), 95)),
        "local_lr_gain_mismatch_max_abs_db": float(np.max(np.abs(mismatch[mask]))),
        **local_stats,
    }, {"times_s": np.asarray(times), "width_change_db": changes_array}


def contiguous_event_stats(
    reduction: np.ndarray, mask: np.ndarray, sample_rate: int, threshold: float
) -> dict:
    active = (reduction >= threshold) & mask
    padded = np.r_[False, active, False]
    changes = np.flatnonzero(padded[1:] != padded[:-1])
    lengths = changes[1::2] - changes[::2]
    durations = lengths.astype(np.float64) * 1000.0 / sample_rate
    if durations.size == 0:
        return {
            "threshold_db": threshold,
            "event_count": 0,
            "duration_p50_ms": 0.0,
            "duration_p95_ms": 0.0,
            "duration_max_ms": 0.0,
        }
    return {
        "threshold_db": threshold,
        "event_count": int(durations.size),
        "duration_p50_ms": float(np.percentile(durations, 50)),
        "duration_p95_ms": float(np.percentile(durations, 95)),
        "duration_max_ms": float(np.max(durations)),
    }


def gain_dynamics(
    x: np.ndarray,
    y: np.ndarray,
    residual5: np.ndarray,
    gain5: np.ndarray,
    sample_rate: int,
    mask: np.ndarray,
    baseline_percentile: float,
    expected_static_gain_db: float | None,
    below_boundary_dbfs: float | None,
) -> tuple[dict, dict, list[dict]]:
    gain50 = local_common_gain(x, y, round(0.050 * sample_rate))
    gain_db5 = db(np.abs(gain5))
    gain_db50 = db(np.abs(gain50))
    baseline = (
        float(expected_static_gain_db)
        if expected_static_gain_db is not None
        else float(np.percentile(gain_db5[mask], baseline_percentile))
    )
    reduction = np.maximum(baseline - gain_db5, 0.0)
    fast = gain_db5 - gain_db50
    step = max(1, round(0.001 * sample_rate))
    sampled = gain_db5[::step]
    sampled_mask = mask[::step]
    pair_mask = sampled_mask[1:] & sampled_mask[:-1]
    signed_slew = np.diff(sampled)[pair_mask]
    absolute_slew = np.abs(signed_slew)

    output_rms = np.square(y, dtype=np.float64).mean(axis=1)
    residual_rms = np.square(residual5, dtype=np.float64).mean(axis=1)
    bins = [(0.0, 0.1), (0.1, 0.5), (0.5, 1.0), (1.0, 2.0),
            (2.0, 3.0), (3.0, 6.0), (6.0, float("inf"))]
    distortion_rows: list[dict] = []
    for low, high in bins:
        selected = mask & (reduction >= low)
        if math.isfinite(high):
            selected &= reduction < high
        if not np.any(selected):
            continue
        distortion_rows.append({
            "gr_bin_db": f"{low:g}-{high:g}" if math.isfinite(high) else f">={low:g}",
            "sample_fraction": float(np.mean(selected[mask])),
            "samples": int(np.sum(selected)),
            "residual_percent_of_output": float(100.0 * math.sqrt(
                float(np.sum(residual_rms[selected]))
                / max(float(np.sum(output_rms[selected])), EPS)
            )),
        })

    activity = {
        "baseline_method": (
            "explicit" if expected_static_gain_db is not None
            else f"percentile_{baseline_percentile:g}"
        ),
        "inferred_unlimited_gain_db": baseline,
        "fraction_reduced_over_0_1db": float(np.mean(reduction[mask] > 0.1)),
        "fraction_reduced_over_0_5db": float(np.mean(reduction[mask] > 0.5)),
        "fraction_reduced_over_1db": float(np.mean(reduction[mask] > 1.0)),
        "fraction_reduced_over_2db": float(np.mean(reduction[mask] > 2.0)),
        "fraction_reduced_over_3db": float(np.mean(reduction[mask] > 3.0)),
        "gain_reduction_p50_db": float(np.percentile(reduction[mask], 50)),
        "gain_reduction_p95_db": float(np.percentile(reduction[mask], 95)),
        "gain_reduction_p99_db": float(np.percentile(reduction[mask], 99)),
        "gain_reduction_max_db": float(np.max(reduction[mask])),
        "events": [
            contiguous_event_stats(reduction, mask, sample_rate, threshold)
            for threshold in (0.1, 1.0, 3.0)
        ],
    }
    if below_boundary_dbfs is not None:
        source_peak5 = ndimage.maximum_filter1d(
            np.max(np.abs(x), axis=1), size=round(0.005 * sample_rate),
            mode="nearest"
        )
        below = mask & (db(source_peak5) < below_boundary_dbfs)
        activity.update({
            "below_boundary_dbfs": below_boundary_dbfs,
            "below_boundary_sample_fraction": float(np.mean(below[mask])),
            "below_boundary_fraction_reduced_over_0_1db": (
                float(np.mean(reduction[below] > 0.1)) if np.any(below) else None
            ),
            "below_boundary_reduction_p95_db": (
                float(np.percentile(reduction[below], 95)) if np.any(below) else None
            ),
            "below_boundary_reduction_max_db": (
                float(np.max(reduction[below])) if np.any(below) else None
            ),
        })
    modulation = {
        "fast_definition": "5ms fitted gain minus 50ms fitted gain",
        "fast_gain_modulation_rms_db": float(rms(fast[mask])),
        "fast_gain_modulation_p95_abs_db": float(np.percentile(np.abs(fast[mask]), 95)),
        "fast_gain_modulation_p99_abs_db": float(np.percentile(np.abs(fast[mask]), 99)),
        "fast_gain_modulation_max_abs_db": float(np.max(np.abs(fast[mask]))),
        "gain_change_1ms_p95_db": float(np.percentile(absolute_slew, 95)),
        "gain_change_1ms_p99_db": float(np.percentile(absolute_slew, 99)),
        "gain_change_1ms_max_db": float(np.max(absolute_slew)),
        "attack_change_1ms_p95_db": float(np.percentile(-signed_slew[signed_slew < 0], 95))
        if np.any(signed_slew < 0) else 0.0,
        "release_change_1ms_p95_db": float(np.percentile(signed_slew[signed_slew > 0], 95))
        if np.any(signed_slew > 0) else 0.0,
    }
    traces = {
        "gain_db5": gain_db5,
        "gain_db50": gain_db50,
        "reduction_db": reduction,
        "fast_db": fast,
    }
    return {"gain_activity": activity, "modulation": modulation}, traces, distortion_rows


def lobe_metrics(x: np.ndarray, y: np.ndarray, sample_rate: int) -> tuple[dict, list[dict]]:
    residues: list[np.ndarray] = []
    jumps: list[np.ndarray] = []
    rows: list[dict] = []
    for channel in range(x.shape[1]):
        source = x[:, channel].astype(np.float64)
        output = y[:, channel].astype(np.float64)
        boundaries = np.r_[
            0,
            np.flatnonzero(np.signbit(source[1:]) != np.signbit(source[:-1])) + 1,
            source.size,
        ]
        starts, stops = boundaries[:-1], boundaries[1:]
        lengths = stops - starts
        source2 = np.r_[0.0, np.cumsum(source * source)]
        cross = np.r_[0.0, np.cumsum(source * output)]
        output2 = np.r_[0.0, np.cumsum(output * output)]
        power = source2[stops] - source2[starts]
        dot = cross[stops] - cross[starts]
        output_power = output2[stops] - output2[starts]
        source_rms = np.sqrt(np.maximum(power / np.maximum(lengths, 1), 0.0))
        valid = (lengths >= 2) & (source_rms >= 10.0 ** (-55.0 / 20.0))
        gain = np.divide(dot, power, out=np.zeros_like(dot), where=power > EPS)
        residual_power = np.maximum(output_power - gain * dot, 0.0)
        residue = 100.0 * np.sqrt(
            np.divide(residual_power, np.maximum(output_power, EPS))
        )
        gain_db = db(np.abs(gain))
        residues.append(residue[valid])
        adjacent = valid[:-1] & valid[1:]
        jump = np.abs(gain_db[1:] - gain_db[:-1])
        jumps.append(jump[adjacent])
        indices = np.flatnonzero(adjacent)
        if indices.size:
            largest = indices[np.argsort(jump[indices])[-100:]]
            rows.extend({
                "time_s": float(boundaries[index + 1] / sample_rate),
                "channel": channel + 1,
                "gain_jump_db": float(jump[index]),
                "preceding_lobe_samples": int(lengths[index]),
                "following_lobe_samples": int(lengths[index + 1]),
                "following_source_rms_dbfs": float(db(source_rms[index + 1])),
            } for index in largest)
    residue_all = np.concatenate(residues) if residues else np.asarray([0.0])
    jump_all = np.concatenate(jumps) if jumps else np.asarray([0.0])
    rows.sort(key=lambda row: row["gain_jump_db"], reverse=True)
    return {
        "audited_lobes": int(residue_all.size),
        "within_lobe_scalar_residue_median_pct": float(np.percentile(residue_all, 50)),
        "within_lobe_scalar_residue_p95_pct": float(np.percentile(residue_all, 95)),
        "within_lobe_scalar_residue_p99_pct": float(np.percentile(residue_all, 99)),
        "adjacent_lobe_gain_jump_median_db": float(np.percentile(jump_all, 50)),
        "adjacent_lobe_gain_jump_p95_db": float(np.percentile(jump_all, 95)),
        "adjacent_lobe_gain_jump_p99_db": float(np.percentile(jump_all, 99)),
        "adjacent_lobe_gain_jump_max_db": float(np.max(jump_all)),
    }, rows[:200]


def window_metrics(
    x: np.ndarray,
    y: np.ndarray,
    sample_rate: int,
    valid: np.ndarray,
    window_ms: float = 20.0,
    hop_ms: float = 5.0,
) -> list[dict]:
    window = max(1, round(window_ms * 0.001 * sample_rate))
    hop = max(1, round(hop_ms * 0.001 * sample_rate))
    source_power = np.sum(x * x, axis=1, dtype=np.float64)
    output_power = np.sum(y * y, axis=1, dtype=np.float64)
    cross = np.sum(x * y, axis=1, dtype=np.float64)
    mask_prefix = np.r_[0, np.cumsum(valid.astype(np.int64))]
    sx = np.r_[0.0, np.cumsum(source_power)]
    sy = np.r_[0.0, np.cumsum(output_power)]
    sc = np.r_[0.0, np.cumsum(cross)]
    starts = np.arange(0, x.shape[0] - window + 1, hop)
    stops = starts + window
    counts = mask_prefix[stops] - mask_prefix[starts]
    xp, yp, dot = sx[stops] - sx[starts], sy[stops] - sy[starts], sc[stops] - sc[starts]
    gain = dot / np.maximum(xp, EPS)
    residue_power = np.maximum(yp - gain * dot, 0.0)
    residue = 100.0 * np.sqrt(residue_power / np.maximum(yp, EPS))
    good = (counts >= 0.80 * window) & (xp > EPS) & (yp > EPS)
    rows = []
    for index in np.flatnonzero(good):
        rows.append({
            "start_s": float(starts[index] / sample_rate),
            "end_s": float(stops[index] / sample_rate),
            "source_rms_dbfs": float(db(math.sqrt(xp[index] / (window * x.shape[1])))),
            "gain_db": float(db(abs(gain[index]))),
            "local_residual_pct": float(residue[index]),
        })
    return rows


def metadata(path: Path, data: np.ndarray, sample_rate: int, tp_factor: int):
    ffmpeg, warnings = ffmpeg_metrics(path)
    true_peak, channels = true_peak_chunked(data, tp_factor)
    return {
        "path": str(path.resolve()),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
        "sample_rate": sample_rate,
        "channels": data.shape[1],
        "frames": data.shape[0],
        "duration_s": data.shape[0] / sample_rate,
        "subtype": sf.info(path).subtype,
        "sample_peak_dbfs": float(db(np.max(np.abs(data)))),
        "rms_dbfs": float(db(float(rms(data)))),
        f"reconstructed_true_peak_{tp_factor}x_dbtp": true_peak,
        f"reconstructed_true_peak_{tp_factor}x_channels_dbtp": channels,
        **ffmpeg,
    }, warnings


def analyze_render(
    role: str,
    path: Path,
    x: np.ndarray,
    data: np.ndarray,
    sample_rate: int,
    mask: np.ndarray,
    alignment: dict,
    tp_factor: int,
    windows_ms: list[float],
    fft_size: int,
    baseline_percentile: float,
    explicit_gain: float | None,
    below_boundary: float | None,
) -> tuple[dict, dict]:
    meta, warnings = metadata(path, data, sample_rate, tp_factor)
    xy, yy = x[mask], data[mask]
    best_gain = float(np.sum(xy * yy, dtype=np.float64) / max(
        float(np.sum(xy * xy, dtype=np.float64)), EPS
    ))
    global_residual = yy - best_gain * xy
    output_rms = max(float(rms(yy)), EPS)
    local_rows = []
    gains: dict[float, np.ndarray] = {}
    residuals: dict[float, np.ndarray] = {}
    for window_ms in windows_ms:
        row, gain, residual = residual_metrics(
            x, data, sample_rate, mask, window_ms
        )
        local_rows.append(row)
        gains[window_ms] = gain
        residuals[window_ms] = residual
    analysis_window = 5.0 if 5.0 in gains else min(gains, key=lambda value: abs(value - 5.0))
    spectral_rows, spectral_curves = spectral_metrics(
        x, data, residuals[analysis_window], sample_rate, mask, fft_size
    )
    stereo, stereo_trace = stereo_metrics(x, data, sample_rate, mask)
    dynamics, gain_traces, distortion_rows = gain_dynamics(
        x, data, residuals[analysis_window], gains[analysis_window],
        sample_rate, mask, baseline_percentile, explicit_gain, below_boundary
    )
    lobes, lobe_rows = lobe_metrics(x, data, sample_rate)
    source_crest = float(db(np.max(np.abs(x[mask])) / max(float(rms(x[mask])), EPS)))
    output_crest = float(db(np.max(np.abs(data[mask])) / output_rms))
    return {
        "metadata": meta,
        "alignment": alignment,
        "warnings": warnings,
        "best_global_gain_db": float(db(abs(best_gain))),
        "global_correlation": normalized_correlation(xy, yy),
        "global_gain_fitted_residual_percent": 100.0 * float(rms(global_residual)) / output_rms,
        "global_gain_fitted_residual_db_below_output": float(db(float(rms(global_residual)) / output_rms)),
        "local_scalar_residuals": local_rows,
        "spectral_bands_after_local_scalar_fit": spectral_rows,
        "stereo": stereo,
        "crest": {
            "source_crest_db": source_crest,
            "output_crest_db": output_crest,
            "crest_change_db": output_crest - source_crest,
        },
        "lobe_transitions": lobes,
        **dynamics,
        "distortion_conditioned_by_gr": distortion_rows,
    }, {
        "spectral": spectral_curves,
        "gain": gain_traces,
        "stereo": stereo_trace,
        "lobe_rows": lobe_rows,
    }


def pairwise_normalized(
    target: np.ndarray,
    current: np.ndarray,
    mask: np.ndarray,
    target_meta: dict,
    current_meta: dict,
    tp_key: str,
) -> dict:
    target_lufs = target_meta.get("precise_integrated_lufs")
    current_lufs = current_meta.get("precise_integrated_lufs")
    if target_lufs is not None and current_lufs is not None:
        current_loud_scale_db = float(target_lufs - current_lufs)
    else:
        current_loud_scale_db = float(db(
            float(rms(target[mask])) / max(float(rms(current[mask])), EPS)
        ))
    current_loud = current * 10.0 ** (current_loud_scale_db / 20.0)
    current_tp_scale_db = float(target_meta[tp_key] - current_meta[tp_key])
    current_tp = current * 10.0 ** (current_tp_scale_db / 20.0)

    def metrics(left: np.ndarray, right: np.ndarray) -> dict:
        a, b = left[mask], right[mask]
        best = float(np.sum(a * b, dtype=np.float64) / max(
            float(np.sum(a * a, dtype=np.float64)), EPS
        ))
        return {
            "correlation": normalized_correlation(a, b),
            "rms_difference_percent_of_target": 100.0 * float(rms(a - b)) / max(float(rms(a)), EPS),
            "best_current_to_target_scalar_db": float(db(abs(best))),
        }
    return {
        "raw": metrics(target, current),
        "equal_loudness": {
            "current_scale_db": current_loud_scale_db,
            **metrics(target, current_loud),
        },
        "equal_true_peak": {
            "current_scale_db": current_tp_scale_db,
            **metrics(target, current_tp),
        },
    }


def plot_results(
    output_dir: Path,
    x: np.ndarray,
    renders: dict[str, np.ndarray],
    sample_rate: int,
    valid: np.ndarray,
    analyses: dict[str, dict],
    traces: dict[str, dict],
    window_rows: dict[str, list[dict]],
    alignment_traces: dict[str, dict],
    labels: dict[str, str],
) -> None:
    total = x.shape[0]
    step = max(1, math.ceil(total / 120000))
    indices = np.arange(0, total, step)
    times = indices / sample_rate
    env_window = max(1, round(0.010 * sample_rate))
    fig, axes = plt.subplots(3, 1, figsize=(16, 11), sharex=True)
    for role, data in {"Original": x, **renders}.items():
        envelope = np.sqrt(ndimage.uniform_filter1d(
            np.mean(data * data, axis=1), env_window, mode="nearest"
        ))
        axes[0].plot(times, db(envelope[indices]), label=labels[role],
                     color=ROLE_COLORS[role], lw=0.8)
    axes[0].set_ylabel("10 ms RMS (dBFS)")
    axes[0].legend(ncol=3)
    for role in ("Target", "Current"):
        axes[1].plot(times, traces[role]["gain"]["gain_db5"][indices],
                     label=labels[role], color=ROLE_COLORS[role], lw=0.8)
        axes[2].plot(times, traces[role]["gain"]["fast_db"][indices],
                     label=labels[role], color=ROLE_COLORS[role], lw=0.8)
    axes[1].set_ylabel("5 ms fitted gain (dB)")
    axes[2].set_ylabel("5 ms - 50 ms gain (dB)")
    axes[2].set_xlabel("Time (s)")
    for axis in axes:
        axis.grid(alpha=0.2)
    fig.tight_layout()
    fig.savefig(output_dir / "envelope_and_gain_timeline.png", dpi=160)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(16, 5))
    for role in ("Target", "Current"):
        rows = window_rows[role]
        ax.plot(
            [0.5 * (row["start_s"] + row["end_s"]) for row in rows],
            [row["local_residual_pct"] for row in rows],
            label=labels[role], color=ROLE_COLORS[role], lw=0.85,
        )
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("20 ms local-scalar residue (%)")
    ax.grid(alpha=0.2)
    ax.legend()
    fig.tight_layout()
    fig.savefig(output_dir / "local_residue_timeline.png", dpi=160)
    plt.close(fig)

    fig, axes = plt.subplots(2, 1, figsize=(14, 9), sharex=True)
    for role in ("Target", "Current"):
        curve = traces[role]["spectral"]
        frequency = curve["frequency_hz"]
        axes[0].semilogx(frequency[1:], np.clip(curve["coherence"][1:], 0, 1),
                         label=labels[role], color=ROLE_COLORS[role], lw=0.9)
        axes[1].semilogx(frequency[1:], curve["residual_output_psd_db"][1:],
                         label=labels[role], color=ROLE_COLORS[role], lw=0.9)
    axes[0].set_ylabel("Magnitude-squared coherence")
    axes[0].set_ylim(0, 1.02)
    axes[1].set_ylabel("Local residue/output PSD (dB)")
    axes[1].set_xlabel("Frequency (Hz)")
    axes[1].set_xlim(20, sample_rate * 0.49)
    for axis in axes:
        axis.grid(alpha=0.2, which="both")
        axis.legend()
    fig.tight_layout()
    fig.savefig(output_dir / "coherence_and_residue_spectrum.png", dpi=160)
    plt.close(fig)

    fig, axes = plt.subplots(2, 1, figsize=(14, 9), sharex=True)
    for role in ("Target", "Current"):
        curve = traces[role]["spectral"]
        frequency = curve["frequency_hz"]
        reliable = curve["reliable"]
        magnitude = np.where(reliable, curve["transfer_db"], np.nan)
        phase = np.where(reliable, curve["phase_deg"], np.nan)
        axes[0].semilogx(frequency[1:], magnitude[1:], label=labels[role],
                         color=ROLE_COLORS[role], lw=0.9)
        axes[1].semilogx(frequency[1:], phase[1:], label=labels[role],
                         color=ROLE_COLORS[role], lw=0.9)
    axes[0].set_ylabel("Coherence-qualified transfer (dB)")
    axes[1].set_ylabel("Transfer phase (degrees)")
    axes[1].set_xlabel("Frequency (Hz)")
    axes[1].set_xlim(20, sample_rate * 0.49)
    for axis in axes:
        axis.grid(alpha=0.2, which="both")
        axis.legend()
    fig.tight_layout()
    fig.savefig(output_dir / "transfer_frequency_response.png", dpi=160)
    plt.close(fig)

    fig, axes = plt.subplots(3, 1, figsize=(16, 10), sharex=True)
    for role in ("Target", "Current"):
        reduction = traces[role]["gain"]["reduction_db"]
        axes[0].plot(times, reduction[indices], label=labels[role],
                     color=ROLE_COLORS[role], lw=0.8)
        sorted_gr = np.sort(reduction[valid])
        axes[1].plot(sorted_gr, np.linspace(0, 100, sorted_gr.size),
                     label=labels[role], color=ROLE_COLORS[role], lw=0.9)
        fast = np.abs(traces[role]["gain"]["fast_db"][valid])
        axes[2].hist(fast, bins=120, density=True, histtype="step",
                     label=labels[role], color=ROLE_COLORS[role])
    axes[0].set_ylabel("Inferred GR (dB)")
    axes[1].set_ylabel("Cumulative (%)")
    axes[1].set_xlabel("Inferred GR (dB)")
    axes[2].set_xlabel("|5 ms - 50 ms gain| (dB)")
    axes[2].set_ylabel("Density")
    for axis in axes:
        axis.grid(alpha=0.2)
        axis.legend()
    fig.tight_layout()
    fig.savefig(output_dir / "gain_reduction_and_dynamics.png", dpi=160)
    plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    for role in ("Target", "Current"):
        rows = analyses[role]["distortion_conditioned_by_gr"]
        xloc = np.arange(len(rows)) + (-0.18 if role == "Target" else 0.18)
        axes[0].bar(xloc, [100.0 * row["sample_fraction"] for row in rows],
                    width=0.35, label=labels[role], color=ROLE_COLORS[role], alpha=0.8)
        axes[1].bar(xloc, [row["residual_percent_of_output"] for row in rows],
                    width=0.35, label=labels[role], color=ROLE_COLORS[role], alpha=0.8)
        axes[0].set_xticks(np.arange(len(rows)), [row["gr_bin_db"] for row in rows], rotation=35)
        axes[1].set_xticks(np.arange(len(rows)), [row["gr_bin_db"] for row in rows], rotation=35)
    axes[0].set_ylabel("Valid programme in GR bin (%)")
    axes[1].set_ylabel("Local residue/output (%)")
    for axis in axes:
        axis.set_xlabel("Inferred GR bin (dB)")
        axis.grid(alpha=0.2, axis="y")
        axis.legend()
    fig.tight_layout()
    fig.savefig(output_dir / "distortion_conditioned_by_gr.png", dpi=160)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(12, 5))
    for role in ("Target", "Current"):
        trace = alignment_traces[role]
        ax.plot(trace["lags"], trace["scores"], label=labels[role],
                color=ROLE_COLORS[role])
    ax.axvline(0.0, color="#888888", lw=0.7)
    ax.set_xlabel("Candidate output delay (samples)")
    ax.set_ylabel("Normalized pre-whitened correlation")
    ax.grid(alpha=0.2)
    ax.legend()
    fig.tight_layout()
    fig.savefig(output_dir / "alignment_correlation.png", dpi=160)
    plt.close(fig)

    if traces["Target"]["stereo"] is not None and traces["Current"]["stereo"] is not None:
        fig, ax = plt.subplots(figsize=(15, 5))
        for role in ("Target", "Current"):
            trace = traces[role]["stereo"]
            ax.plot(trace["times_s"], trace["width_change_db"],
                    label=labels[role], color=ROLE_COLORS[role], lw=0.9)
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("50 ms S/M width change (dB)")
        ax.grid(alpha=0.2)
        ax.legend()
        fig.tight_layout()
        fig.savefig(output_dir / "stereo_width_change.png", dpi=160)
        plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compare Original, Target, and Current audio renders with aligned forensic metrics."
    )
    parser.add_argument("--original", type=Path, required=True)
    parser.add_argument("--target", type=Path, required=True)
    parser.add_argument("--current", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--target-label", default="Target")
    parser.add_argument("--current-label", default="Current")
    parser.add_argument("--max-lag", type=int, default=8192)
    parser.add_argument("--fractional-align", choices=("report", "sinc"), default="report")
    parser.add_argument("--silence-threshold-dbfs", type=float, default=-65.0)
    parser.add_argument("--edge-ms", type=float, default=100.0)
    parser.add_argument("--true-peak-factor", type=int, default=32)
    parser.add_argument("--fft-size", type=int, default=16384)
    parser.add_argument("--gain-windows-ms", default="100,50,20,5,1")
    parser.add_argument("--baseline-percentile", type=float, default=99.9)
    parser.add_argument("--target-static-gain-db", type=float)
    parser.add_argument("--current-static-gain-db", type=float)
    parser.add_argument("--below-boundary-dbfs", type=float)
    parser.add_argument("--excerpt-count", type=int, default=3)
    parser.add_argument("--excerpt-ms", type=float, default=600.0)
    parser.add_argument("--no-excerpts", action="store_true")
    args = parser.parse_args()

    for path in (args.original, args.target, args.current):
        if not path.is_file():
            raise FileNotFoundError(path)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    windows_ms = [float(value) for value in args.gain_windows_ms.split(",")]
    if not windows_ms:
        raise ValueError("At least one gain window is required")

    paths = {
        "Original": args.original,
        "Target": args.target,
        "Current": args.current,
    }
    labels = {
        "Original": "Original",
        "Target": args.target_label,
        "Current": args.current_label,
    }
    raw: dict[str, np.ndarray] = {}
    rates, channels = set(), set()
    for role, path in paths.items():
        data, rate = sf.read(path, always_2d=True, dtype="float64")
        raw[role] = data
        rates.add(rate)
        channels.add(data.shape[1])
    if len(rates) != 1:
        raise RuntimeError(f"Sample-rate mismatch: {sorted(rates)}")
    if len(channels) != 1:
        raise RuntimeError(f"Channel-count mismatch: {sorted(channels)}")
    sample_rate = int(next(iter(rates)))
    common_frames = min(data.shape[0] for data in raw.values())
    duration_warning = len({data.shape[0] for data in raw.values()}) != 1
    for role in raw:
        raw[role] = raw[role][:common_frames]
    x = raw["Original"]

    aligned: dict[str, np.ndarray] = {}
    alignment: dict[str, dict] = {}
    alignment_traces: dict[str, dict] = {}
    alignment_valid = np.ones(common_frames, dtype=bool)
    warnings: list[str] = []
    if duration_warning:
        warnings.append("Input durations differ; analysis was truncated to the common frame count")
    for role in ("Target", "Current"):
        alignment[role], alignment_traces[role] = estimate_delay(
            x, raw[role], sample_rate, args.max_lag
        )
        aligned[role], valid = align_to_source(
            raw[role], alignment[role], args.fractional_align
        )
        alignment_valid &= valid
        remainder = abs(alignment[role]["fractional_remainder_samples"])
        if args.fractional_align == "report" and remainder > 0.02:
            warnings.append(
                f"{labels[role]} has {remainder:.4f} sample fractional remainder; "
                "high-frequency residue includes sub-sample misalignment. Rerender or use --fractional-align sinc."
            )

    mask = valid_mask(
        x, sample_rate, alignment_valid,
        args.silence_threshold_dbfs, args.edge_ms
    )
    original_meta, original_warnings = metadata(
        args.original, x, sample_rate, args.true_peak_factor
    )
    warnings.extend(original_warnings)
    analyses: dict[str, dict] = {}
    traces: dict[str, dict] = {}
    explicit = {
        "Target": args.target_static_gain_db,
        "Current": args.current_static_gain_db,
    }
    for role in ("Target", "Current"):
        analyses[role], traces[role] = analyze_render(
            role, paths[role], x, aligned[role], sample_rate, mask,
            alignment[role], args.true_peak_factor, windows_ms, args.fft_size,
            args.baseline_percentile, explicit[role], args.below_boundary_dbfs
        )
        warnings.extend(f"{labels[role]}: {warning}" for warning in analyses[role]["warnings"])

    tp_key = f"reconstructed_true_peak_{args.true_peak_factor}x_dbtp"
    pairwise = pairwise_normalized(
        aligned["Target"], aligned["Current"], mask,
        analyses["Target"]["metadata"], analyses["Current"]["metadata"], tp_key
    )
    window_rows = {
        role: window_metrics(x, aligned[role], sample_rate, mask)
        for role in ("Target", "Current")
    }
    count = min(len(window_rows["Target"]), len(window_rows["Current"]))
    combined_rows = []
    for index in range(count):
        target = window_rows["Target"][index]
        current = window_rows["Current"][index]
        combined_rows.append({
            "start_s": current["start_s"],
            "end_s": current["end_s"],
            "source_rms_dbfs": current["source_rms_dbfs"],
            "target_gain_db": target["gain_db"],
            "current_gain_db": current["gain_db"],
            "target_local_residual_pct": target["local_residual_pct"],
            "current_local_residual_pct": current["local_residual_pct"],
            "current_minus_target_residual_pp": (
                current["local_residual_pct"] - target["local_residual_pct"]
            ),
        })
    worst_delta = sorted(
        combined_rows, key=lambda row: row["current_minus_target_residual_pp"],
        reverse=True
    )
    worst_current = sorted(
        combined_rows, key=lambda row: row["current_local_residual_pct"],
        reverse=True
    )

    write_csv(args.output_dir / "window_metrics_20ms.csv", combined_rows)
    write_csv(args.output_dir / "worst_current_vs_target_windows.csv", worst_delta[:200])
    write_csv(args.output_dir / "worst_current_windows.csv", worst_current[:200])
    for role in ("Target", "Current"):
        write_csv(
            args.output_dir / f"{role.lower()}_spectral_bands.csv",
            analyses[role]["spectral_bands_after_local_scalar_fit"],
        )
        write_csv(
            args.output_dir / f"{role.lower()}_distortion_by_gr.csv",
            analyses[role]["distortion_conditioned_by_gr"],
        )
        write_csv(
            args.output_dir / f"{role.lower()}_largest_lobe_gain_jumps.csv",
            traces[role]["lobe_rows"],
        )
    spectral_rows = []
    for role in ("Target", "Current"):
        curve = traces[role]["spectral"]
        for index in range(curve["frequency_hz"].size):
            spectral_rows.append({
                "role": role,
                "frequency_hz": float(curve["frequency_hz"][index]),
                "coherence": float(curve["coherence"][index]),
                "transfer_db": float(curve["transfer_db"][index]),
                "phase_deg": float(curve["phase_deg"][index]),
                "residual_output_psd_db": float(curve["residual_output_psd_db"][index]),
                "reliable": bool(curve["reliable"][index]),
            })
    write_csv(args.output_dir / "spectral_curves.csv", spectral_rows)

    plot_results(
        args.output_dir, x, aligned, sample_rate, mask, analyses, traces,
        window_rows, alignment_traces, labels
    )

    excerpt_rows = []
    if not args.no_excerpts and args.excerpt_count > 0:
        selected: list[float] = []
        for row in worst_delta + worst_current:
            centre = 0.5 * (row["start_s"] + row["end_s"])
            if all(abs(centre - prior) >= max(0.45, args.excerpt_ms * 0.001) for prior in selected):
                selected.append(centre)
            if len(selected) >= args.excerpt_count:
                break
        length = round(args.excerpt_ms * 0.001 * sample_rate)
        for number, centre in enumerate(selected, 1):
            start = max(0, round(centre * sample_rate) - length // 2)
            stop = min(common_frames, start + length)
            start = max(0, stop - length)
            for role in ("Original", "Target", "Current"):
                data = x if role == "Original" else aligned[role]
                path = args.output_dir / (
                    f"excerpt_{number}_{start/sample_rate:.3f}-{stop/sample_rate:.3f}s_{role}.wav"
                )
                sf.write(path, data[start:stop], sample_rate, subtype="PCM_24")
                excerpt_rows.append({
                    "excerpt": number,
                    "role": role,
                    "label": labels[role],
                    "start_s": start / sample_rate,
                    "end_s": stop / sample_rate,
                    "path": str(path.resolve()),
                    "sha256": sha256(path),
                })
        write_csv(args.output_dir / "excerpt_manifest.csv", excerpt_rows)

    results = {
        "format": "audio_render_forensics_v1",
        "analysis_contract": {
            "roles": labels,
            "common_frames": common_frames,
            "sample_rate": sample_rate,
            "channels": x.shape[1],
            "valid_samples": int(np.sum(mask)),
            "valid_fraction": float(np.mean(mask)),
            "silence_threshold_dbfs": args.silence_threshold_dbfs,
            "edge_ms": args.edge_ms,
            "fractional_align": args.fractional_align,
            "true_peak_factor": args.true_peak_factor,
            "local_gain_windows_ms": windows_ms,
            "gain_baseline_percentile": args.baseline_percentile,
            "below_boundary_dbfs": args.below_boundary_dbfs,
        },
        "warnings": warnings,
        "metadata": {"Original": original_meta,
                     "Target": analyses["Target"]["metadata"],
                     "Current": analyses["Current"]["metadata"]},
        "alignment": alignment,
        "comparisons_to_original": analyses,
        "current_vs_target": pairwise,
        "worst_windows": {
            "current_minus_target": worst_delta[:20],
            "current_absolute": worst_current[:20],
        },
        "excerpts": excerpt_rows,
    }
    (args.output_dir / "analysis_metrics.json").write_text(
        json.dumps(results, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    def local_value(role: str, window: float) -> float:
        rows = analyses[role]["local_scalar_residuals"]
        nearest = min(rows, key=lambda row: abs(row["window_ms"] - window))
        return nearest["residual_percent_of_output"]

    lines = [
        "# Audio render forensic comparison",
        "",
        f"Original: `{args.original.resolve()}`  ",
        f"Target: `{args.target.resolve()}` ({labels['Target']})  ",
        f"Current: `{args.current.resolve()}` ({labels['Current']})",
        "",
        "## Integrity and alignment",
        "",
        f"- Common analysis: {sample_rate} Hz, {x.shape[1]} channels, "
        f"{common_frames} frames; {np.mean(mask)*100:.2f}% valid after masking.",
    ]
    for role in ("Target", "Current"):
        item = alignment[role]
        lines.append(
            f"- {labels[role]}: integer delay {item['output_delay_samples']} samples; "
            f"fractional estimate {item['fractional_delay_samples']:.6f}; "
            f"polarity {item['polarity']:+d}; integer-aligned correlation "
            f"{item['aligned_correlation_integer']:.9f}."
        )
    if warnings:
        lines += ["", "Warnings:"] + [f"- {warning}" for warning in warnings]
    lines += [
        "",
        "## Core comparison",
        "",
        "| Metric | Target | Current |",
        "|---|---:|---:|",
    ]
    metrics = [
        ("LUFS-I", lambda role: analyses[role]["metadata"].get("precise_integrated_lufs"), " LUFS"),
        (f"{args.true_peak_factor}x true peak", lambda role: analyses[role]["metadata"][tp_key], " dBTP"),
        ("Global fitted residual", lambda role: analyses[role]["global_gain_fitted_residual_percent"], "%"),
        ("20 ms local residual", lambda role: local_value(role, 20.0), "%"),
        ("5 ms local residual", lambda role: local_value(role, 5.0), "%"),
        ("1 ms local residual", lambda role: local_value(role, 1.0), "%"),
        ("Fast gain modulation RMS", lambda role: analyses[role]["modulation"]["fast_gain_modulation_rms_db"], " dB"),
        ("1 ms gain change p99", lambda role: analyses[role]["modulation"]["gain_change_1ms_p99_db"], " dB"),
        (">1 dB GR time", lambda role: 100.0 * analyses[role]["gain_activity"]["fraction_reduced_over_1db"], "%"),
        ("GR p99", lambda role: analyses[role]["gain_activity"]["gain_reduction_p99_db"], " dB"),
        ("Lobe gain jump p99", lambda role: analyses[role]["lobe_transitions"]["adjacent_lobe_gain_jump_p99_db"], " dB"),
        ("Crest change", lambda role: analyses[role]["crest"]["crest_change_db"], " dB"),
    ]
    for label, getter, suffix in metrics:
        values = [getter(role) for role in ("Target", "Current")]
        formatted = ["n/a" if value is None else f"{value:.5f}{suffix}" for value in values]
        lines.append(f"| {label} | {formatted[0]} | {formatted[1]} |")
    lines += [
        "",
        "## Current versus target",
        "",
        f"- Equal-loudness correlation: {pairwise['equal_loudness']['correlation']:.9f}; "
        f"RMS difference {pairwise['equal_loudness']['rms_difference_percent_of_target']:.4f}% of Target.",
        f"- Equal-true-peak correlation: {pairwise['equal_true_peak']['correlation']:.9f}; "
        f"RMS difference {pairwise['equal_true_peak']['rms_difference_percent_of_target']:.4f}% of Target.",
        "",
        "## Largest current disadvantages",
        "",
    ]
    for row in worst_delta[:10]:
        lines.append(
            f"- {row['start_s']:.3f}-{row['end_s']:.3f} s: Current "
            f"{row['current_local_residual_pct']:.3f}%, Target "
            f"{row['target_local_residual_pct']:.3f}%, delta "
            f"{row['current_minus_target_residual_pp']:+.3f} pp; source RMS "
            f"{row['source_rms_dbfs']:.2f} dBFS."
        )
    lines += [
        "",
        "## Interpretation boundary",
        "",
        "- Global or equal-loudness differences include intended gain and dynamic-range changes.",
        "- Local-scalar residue removes an ideal local common gain trajectory. It is a real-program proxy for waveform nonlinearity, phase/SRC error, fast gain modulation and noise; it is not pure-tone THD.",
        "- Inferred GR is audio-derived. Supply explicit static gain values when the render has no clear uncompressed gain plateau.",
        "- Music-derived transfer response is shown only in coherence-qualified bins. Use dedicated tones/sweeps before calling it an LTI frequency response.",
        "- Judge listening quality with the generated time-matched excerpts; metrics locate and characterize differences but do not replace auditioning.",
    ]
    (args.output_dir / "REPORT.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )
    print(f"AUDIO_RENDER_FORENSICS_OK output={args.output_dir.resolve()}")
    print(f"report={args.output_dir.resolve() / 'REPORT.md'}")
    print(f"metrics={args.output_dir.resolve() / 'analysis_metrics.json'}")


if __name__ == "__main__":
    main()
