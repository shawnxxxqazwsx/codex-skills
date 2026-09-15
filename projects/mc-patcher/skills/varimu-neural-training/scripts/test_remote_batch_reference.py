#!/usr/bin/env python3
"""Offline Release plus pinned-metadata batch-reference regression."""

from __future__ import annotations

import json

import varimu_training_coordinator as coordinator


class FakeBackend(coordinator.GitHubBackend):
    def __init__(self, payloads: dict[str, bytes]):
        self.repo = "owner/repo"
        self.branch = "main"
        self.gh_path = "/not-used"
        self.payloads = payloads

    def release_view(self, repo: str, tag: str):
        return {
            "tagName": tag,
            "url": f"https://github.com/{repo}/releases/tag/{tag}",
            "assets": [{"name": "archive-manifest-v1.json"}],
        }

    def download_release_asset(self, repo: str, tag: str, asset_name: str) -> bytes:
        del repo, tag
        return self.payloads[asset_name]

    def get_repository_bytes(
        self, repo: str, path: str, ref: str, *, encoded_path: bool = False
    ) -> bytes:
        del repo, ref, encoded_path
        return self.payloads[path]


def main() -> int:
    objective = "objective-test"
    archive = b'{"kind":"capture-package"}\n'
    allowlist = b'{"kind":"exact-allowlist"}\n'
    ledger = coordinator.canonical_json_bytes({
        "status": "READY",
        "training_objective_id": objective,
    })
    payloads = {
        "archive-manifest-v1.json": archive,
        "capture/allowlist.json": allowlist,
        "training/ready/receipt.json": ledger,
    }
    batch = {
        "schema_version": 1,
        "kind": "varimu_training_batch",
        "status": "READY",
        "batch_id": "batch-test",
        "created_at_utc": "2026-08-31T00:00:00Z",
        "priority": 100,
        "eligibility_authority": "exact_dataset_allowlist",
        "training_objective_id": objective,
        "model_family": "test-causal-model",
        "dataset": {
            "release_repository": "owner/repo",
            "release_tag": "capture-test",
            "release_url": "https://github.com/owner/repo/releases/tag/capture-test",
            "archive_manifest_asset_name": "archive-manifest-v1.json",
            "archive_manifest_sha256": coordinator.sha256_bytes(archive),
            "metadata_code_commit": "a" * 40,
            "exact_allowlist_path": "capture/allowlist.json",
            "exact_allowlist_sha256": coordinator.sha256_bytes(allowlist),
            "ready_ledger_path": "training/ready/receipt.json",
            "ready_ledger_sha256": coordinator.sha256_bytes(ledger),
            "target_variant": "raw-v1",
            "objective_role": "primary",
            "no_mix_group": "test-primary",
        },
        "source_files": [
            {
                "path": "capture/original.wav", "sha256": "1" * 64,
                "role": "original", "eligible_for_training": True,
            },
            {
                "path": "capture/target.wav", "sha256": "2" * 64,
                "role": "target", "eligible_for_training": True,
            },
        ],
        "split_policy": {
            "manifest_path": "capture/split.json",
            "manifest_sha256": "3" * 64,
            "whole_group_leakage_keys": ["capture_id"],
        },
    }
    coordinator.validate_batch(batch)
    backend = FakeBackend(payloads)
    coordinator.verify_batch_remote_reference(backend, batch)
    backend.payloads["archive-manifest-v1.json"] = b"tampered\n"
    try:
        coordinator.verify_batch_remote_reference(backend, batch)
    except coordinator.CoordinationError:
        tamper_rejected = True
    else:
        tamper_rejected = False
    if not tamper_rejected:
        raise RuntimeError("tampered capture Release manifest was accepted")
    print(json.dumps({
        "status": "PASS",
        "release_manifest_bound": True,
        "metadata_commit_bound": True,
        "tamper_rejected": True,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
