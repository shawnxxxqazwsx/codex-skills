#!/usr/bin/env python3
"""Offline FIFO and atomic-claim regression for the Vari-Mu coordinator."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile


NONZERO_SHA = "1" * 64


def batch(batch_id: str, created: str) -> dict:
    return {
        "schema_version": 1,
        "kind": "varimu_training_batch",
        "status": "READY",
        "batch_id": batch_id,
        "created_at_utc": created,
        "priority": 100,
        "eligibility_authority": "exact_dataset_allowlist",
        "training_objective_id": f"objective-{batch_id}",
        "model_family": "test-causal-model",
        "dataset": {
            "release_repository": "o/r",
            "release_tag": "capture-test-batch",
            "release_url": "https://github.com/o/r/releases/tag/capture-test-batch",
            "archive_manifest_asset_name": "archive.json",
            "archive_manifest_sha256": "6" * 64,
            "metadata_code_commit": "a" * 40,
            "exact_allowlist_path": "capture-data/allowlist.json",
            "exact_allowlist_sha256": NONZERO_SHA,
            "ready_ledger_path": "training/ready/d/training-consumption-v1.json",
            "ready_ledger_sha256": "2" * 64,
            "target_variant": "raw-v1",
            "objective_role": "primary",
            "no_mix_group": "primary",
        },
        "source_files": [
            {
                "path": "capture-data/original.wav",
                "sha256": "3" * 64,
                "role": "original",
                "eligible_for_training": True,
            },
            {
                "path": "capture-data/target.wav",
                "sha256": "4" * 64,
                "role": "target",
                "eligible_for_training": True,
            },
        ],
        "split_policy": {
            "manifest_path": "capture-data/split.json",
            "manifest_sha256": "5" * 64,
            "whole_group_leakage_keys": ["capture_id"],
        },
        "notes": "test",
    }


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def run_worker(script: Path, control: Path, local: Path, machine_id: str) -> subprocess.Popen[str]:
    return subprocess.Popen(
        [
            sys.executable, str(script), "watch-once",
            "--control-dir", str(control),
            "--completion-index-root", "varimu-training/release-index",
            "--local-root", str(local),
            "--machine-name", machine_id,
            "--machine-id", machine_id,
        ],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def main() -> int:
    coordinator = Path(__file__).with_name("varimu_training_coordinator.py")
    with tempfile.TemporaryDirectory(prefix="varimu-coordination-") as temporary:
        root = Path(temporary)

        # One available batch: exactly one of two racing machines may win.
        race = root / "race"
        write_json(race / "queue/oldest/batch.json", batch("oldest", "2026-01-01T00:00:00Z"))
        workers = [
            run_worker(coordinator, race, root / "race-worker-a", "worker-a"),
            run_worker(coordinator, race, root / "race-worker-b", "worker-b"),
        ]
        results = []
        for process in workers:
            stdout, stderr = process.communicate(timeout=20)
            if process.returncode != 0:
                raise RuntimeError(stderr)
            results.append(json.loads(stdout))
        statuses = sorted(item["status"] for item in results)
        if statuses != ["CLAIMED", "NO_AVAILABLE_BATCH"]:
            raise RuntimeError(f"atomic race failed: {results}")
        claim = json.loads((race / "queue/oldest/claim.json").read_text(encoding="utf-8"))
        if claim["machine_id"] not in {"worker-a", "worker-b"}:
            raise RuntimeError("unexpected race winner")

        # Scan all entries, skip a foreign-marked oldest batch, and allocate the
        # two remaining batches in strict created_at order across two workers.
        fifo = root / "fifo"
        write_json(fifo / "queue/a/batch.json", batch("a", "2026-01-01T00:00:00Z"))
        write_json(fifo / "queue/b/batch.json", batch("b", "2026-01-02T00:00:00Z"))
        newest = batch("c", "2026-01-03T00:00:00Z")
        newest["priority"] = 999999
        write_json(fifo / "queue/c/batch.json", newest)
        raw_a = (fifo / "queue/a/batch.json").read_bytes()
        write_json(fifo / "queue/a/claim.json", {
            "schema_version": 1,
            "kind": "varimu_training_claim",
            "status": "CLAIMED",
            "batch_id": "a",
            "training_objective_id": "objective-a",
            "machine_name": "foreign",
            "machine_id": "foreign",
            "claimed_at_utc": "2026-01-01T00:01:00Z",
            "batch_manifest_sha256": __import__("hashlib").sha256(raw_a).hexdigest(),
        })
        first = run_worker(coordinator, fifo, root / "fifo-worker-a", "fifo-a")
        first_out, first_err = first.communicate(timeout=20)
        if first.returncode != 0:
            raise RuntimeError(first_err)
        first_result = json.loads(first_out)
        if first_result.get("batch_id") != "b":
            raise RuntimeError(f"oldest-unclaimed selection failed: {first_result}")
        second = run_worker(coordinator, fifo, root / "fifo-worker-b", "fifo-b")
        second_out, second_err = second.communicate(timeout=20)
        if second.returncode != 0:
            raise RuntimeError(second_err)
        second_result = json.loads(second_out)
        if second_result.get("batch_id") != "c":
            raise RuntimeError(f"next-oldest selection failed: {second_result}")

        print(json.dumps({
            "status": "PASS",
            "atomic_single_winner": True,
            "scan_all_oldest_unclaimed_first": ["b", "c"],
            "foreign_claim_preserved": True,
        }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
