#!/usr/bin/env python3
"""Run a disclosed Original/Target-only forensic baseline before training."""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any


class BaselineError(RuntimeError):
    pass


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace(
        "+00:00", "Z"
    )


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(4 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def local_residual(analysis: dict[str, Any], window_ms: float) -> float:
    rows = analysis["local_scalar_residuals"]
    row = min(rows, key=lambda item: abs(float(item["window_ms"]) - window_ms))
    return float(row["residual_percent_of_output"])


def filter_sentinel_excerpts(output_dir: Path) -> None:
    path = output_dir / "excerpt_manifest.csv"
    if not path.is_file():
        return
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    kept = [row for row in rows if row.get("role") != "Current"]
    for row in rows:
        if row.get("role") != "Current":
            continue
        candidate = Path(row.get("path", ""))
        try:
            candidate.relative_to(output_dir.resolve())
        except (ValueError, OSError):
            continue
        if candidate.is_file():
            candidate.unlink()
    if kept:
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(kept[0]))
            writer.writeheader()
            writer.writerows(kept)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--original", type=Path, required=True)
    parser.add_argument("--target", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--target-label", default="Captured Hardware Target")
    parser.add_argument("--max-lag", type=int, default=8192)
    parser.add_argument("--fractional-align", choices=("report", "sinc"), default="report")
    parser.add_argument("--silence-threshold-dbfs", type=float, default=-65.0)
    parser.add_argument("--edge-ms", type=float, default=100.0)
    parser.add_argument("--true-peak-factor", type=int, default=32)
    parser.add_argument("--fft-size", type=int, default=16384)
    parser.add_argument("--target-static-gain-db", type=float)
    parser.add_argument("--below-boundary-dbfs", type=float)
    parser.add_argument("--excerpt-count", type=int, default=3)
    args = parser.parse_args()
    try:
        original = args.original.expanduser().resolve()
        target = args.target.expanduser().resolve()
        output_dir = args.output_dir.expanduser().resolve()
        if not original.is_file() or not target.is_file():
            raise BaselineError("Original and Target must both exist")
        if output_dir.exists() and any(output_dir.iterdir()):
            raise BaselineError(f"output directory must be absent or empty: {output_dir}")
        output_dir.mkdir(parents=True, exist_ok=True)
        repo_root = Path(__file__).resolve().parents[4]
        analyzer = (
            repo_root / ".agents/skills/audio-render-forensics/scripts/compare_audio_renders.py"
        )
        if not analyzer.is_file():
            raise BaselineError(f"audio-render-forensics analyzer not found: {analyzer}")
        command = [
            sys.executable,
            str(analyzer),
            "--original", str(original),
            "--target", str(target),
            "--current", str(target),
            "--target-label", args.target_label,
            "--current-label", "Target identity sentinel; no algorithm exists",
            "--output-dir", str(output_dir),
            "--max-lag", str(args.max_lag),
            "--fractional-align", args.fractional_align,
            "--silence-threshold-dbfs", str(args.silence_threshold_dbfs),
            "--edge-ms", str(args.edge_ms),
            "--true-peak-factor", str(args.true_peak_factor),
            "--fft-size", str(args.fft_size),
            "--excerpt-count", str(args.excerpt_count),
        ]
        if args.target_static_gain_db is not None:
            command += [
                "--target-static-gain-db", str(args.target_static_gain_db),
                "--current-static-gain-db", str(args.target_static_gain_db),
            ]
        if args.below_boundary_dbfs is not None:
            command += ["--below-boundary-dbfs", str(args.below_boundary_dbfs)]
        result = subprocess.run(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode != 0:
            raise BaselineError(f"forensic analyzer failed: {result.stderr.strip()}")

        analyzer_metrics_path = output_dir / "analysis_metrics.json"
        all_metrics = json.loads(analyzer_metrics_path.read_text(encoding="utf-8"))
        target_meta = all_metrics["metadata"]["Target"]
        sentinel_meta = all_metrics["metadata"]["Current"]
        if target_meta["sha256"] != sentinel_meta["sha256"]:
            raise BaselineError("identity sentinel does not match Target hash")
        pair = all_metrics["current_vs_target"]
        if abs(pair["raw"]["correlation"] - 1.0) > 1e-10:
            raise BaselineError("identity sentinel correlation is not unity")
        if abs(pair["raw"]["rms_difference_percent_of_target"]) > 1e-10:
            raise BaselineError("identity sentinel residual is not zero")

        filter_sentinel_excerpts(output_dir)
        adapter_report = output_dir / "ANALYZER_ADAPTER_REPORT.md"
        os.replace(output_dir / "REPORT.md", adapter_report)
        target_analysis = all_metrics["comparisons_to_original"]["Target"]
        baseline = {
            "format": "varimu_original_target_baseline_v1",
            "analysis_mode": "ORIGINAL_TARGET_ONLY",
            "created_at_utc": utc_now(),
            "adapter_disclosure": (
                "The three-role analyzer received Target as a duplicate identity sentinel. "
                "No algorithm existed or was evaluated. baseline_metrics.json contains only "
                "Original and Target evidence."
            ),
            "analysis_contract": all_metrics["analysis_contract"],
            "warnings": sorted(set(
                warning for warning in all_metrics.get("warnings", [])
                if "Target identity sentinel" not in warning
            )),
            "metadata": {
                "Original": all_metrics["metadata"]["Original"],
                "Target": target_meta,
            },
            "alignment": all_metrics["alignment"]["Target"],
            "comparison_to_original": target_analysis,
            "adapter_metrics_sha256": sha256_file(analyzer_metrics_path),
        }
        baseline_path = output_dir / "baseline_metrics.json"
        baseline_path.write_text(
            json.dumps(baseline, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        meta = baseline["metadata"]
        tp_key = f"reconstructed_true_peak_{args.true_peak_factor}x_dbtp"
        lines = [
            "# Original / captured Target forensic baseline",
            "",
            "No algorithm exists in this stage. The complete analyzer ran with a disclosed "
            "Target identity sentinel solely to reuse its Target-side residual, dynamics, "
            "nonlinearity, spectral, stereo, loudness, true-peak, plot, and excerpt methods.",
            "",
            f"- Original: `{original}`",
            f"- Target: `{target}` ({args.target_label})",
            f"- Original SHA-256: `{meta['Original']['sha256']}`",
            f"- Target SHA-256: `{meta['Target']['sha256']}`",
            f"- Integer delay: {baseline['alignment']['output_delay_samples']} samples",
            f"- Fractional estimate: {baseline['alignment']['fractional_delay_samples']:.6f} samples",
            f"- Polarity: {baseline['alignment']['polarity']:+d}",
            f"- Aligned correlation: {baseline['alignment']['aligned_correlation_integer']:.9f}",
            "",
            "## Target behavior relative to Original",
            "",
            f"- LUFS-I: {meta['Target'].get('precise_integrated_lufs')}",
            f"- {args.true_peak_factor}x true peak: {meta['Target'][tp_key]:.5f} dBTP",
            f"- Global fitted residue: {target_analysis['global_gain_fitted_residual_percent']:.5f}%",
            f"- 20 ms local residue: {local_residual(target_analysis, 20.0):.5f}%",
            f"- 5 ms local residue: {local_residual(target_analysis, 5.0):.5f}%",
            f"- 1 ms local residue: {local_residual(target_analysis, 1.0):.5f}%",
            f"- Fast gain modulation RMS: {target_analysis['modulation']['fast_gain_modulation_rms_db']:.5f} dB",
            f"- GR p99: {target_analysis['gain_activity']['gain_reduction_p99_db']:.5f} dB",
            f"- Lobe gain jump p99: {target_analysis['lobe_transitions']['adjacent_lobe_gain_jump_p99_db']:.5f} dB",
            "",
            "See `baseline_metrics.json` for all numeric Target statistics, CSV files for "
            "window/band/GR/lobe detail, PNG files for the complete plot set, and the paired "
            "Original/Target excerpt manifest for listening.",
            "",
            "Programme residue is not literal THD, inferred GR is not hardware telemetry, "
            "and low-coherence music bins are not a frequency-response claim.",
        ]
        report_path = output_dir / "BASELINE_REPORT.md"
        report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(json.dumps({
            "status": "BASELINE_COMPLETE",
            "mode": "ORIGINAL_TARGET_ONLY",
            "report": str(report_path),
            "metrics": str(baseline_path),
            "adapter_report": str(adapter_report),
        }, ensure_ascii=False))
        return 0
    except (BaselineError, OSError, KeyError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
