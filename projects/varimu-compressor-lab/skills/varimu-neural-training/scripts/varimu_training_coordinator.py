#!/usr/bin/env python3
"""Coordinate immutable Vari-Mu training batches across machines.

GitHub is the production control plane.  A filesystem backend is included for
offline validation and race tests.  The monitor claims work; it never executes
training code from a remote batch.
"""

from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import base64
import fcntl
import hashlib
import json
import math
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
import tempfile
from typing import Any
from urllib.parse import quote


SCHEMA_VERSION = 1
ACTIVE_STATES = {"CLAIMED", "TRAINING", "FINALIZING"}
SAFE_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,95}$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
REPO_RE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
ASSET_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,254}$")
ZERO_SHA256 = "0" * 64


class CoordinationError(RuntimeError):
    pass


class RemoteMissing(CoordinationError):
    pass


class CreateConflict(CoordinationError):
    pass


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace(
        "+00:00", "Z"
    )


def parse_utc(value: Any, label: str) -> None:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise CoordinationError(f"{label} must be an ISO-8601 UTC timestamp ending in Z")
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise CoordinationError(f"invalid {label}: {value!r}") from exc


def canonical_json_bytes(data: dict[str, Any]) -> bytes:
    return (json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode(
        "utf-8"
    )


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(4 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def safe_id(value: Any, label: str) -> str:
    if not isinstance(value, str) or not SAFE_ID_RE.fullmatch(value):
        raise CoordinationError(f"unsafe {label}: {value!r}")
    return value


def safe_control_path(path: str) -> str:
    candidate = PurePosixPath(path)
    if candidate.is_absolute() or not candidate.parts or ".." in candidate.parts:
        raise CoordinationError(f"unsafe control-plane path: {path!r}")
    return candidate.as_posix()


def load_json_file(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CoordinationError(f"cannot read JSON {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise CoordinationError(f"JSON root must be an object: {path}")
    return data


def atomic_write(path: Path, payload: bytes, *, exclusive: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if exclusive:
        try:
            with path.open("xb") as handle:
                handle.write(payload)
                handle.flush()
                os.fsync(handle.fileno())
            return
        except FileExistsError as exc:
            raise CreateConflict(f"refusing to overwrite {path}") from exc
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, path)
    except BaseException:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass
        raise


def atomic_write_json(path: Path, data: dict[str, Any], *, exclusive: bool = False) -> None:
    atomic_write(path, canonical_json_bytes(data), exclusive=exclusive)


def validate_sha(value: Any, label: str, *, allow_placeholder: bool = False) -> str:
    if not isinstance(value, str) or not SHA256_RE.fullmatch(value):
        raise CoordinationError(f"{label} must be a lowercase SHA-256")
    if not allow_placeholder and value == ZERO_SHA256:
        raise CoordinationError(f"{label} is still a placeholder")
    return value


def validate_batch(data: dict[str, Any], *, expected_id: str | None = None) -> None:
    if data.get("schema_version") != SCHEMA_VERSION:
        raise CoordinationError("batch schema_version must be 1")
    if data.get("kind") != "varimu_training_batch":
        raise CoordinationError("batch kind must be varimu_training_batch")
    if data.get("status") != "READY":
        raise CoordinationError("batch status must be READY")
    batch_id = safe_id(data.get("batch_id"), "batch_id")
    if expected_id is not None and batch_id != expected_id:
        raise CoordinationError(
            f"batch_id {batch_id!r} does not match queue directory {expected_id!r}"
        )
    parse_utc(data.get("created_at_utc"), "created_at_utc")
    priority = data.get("priority")
    if not isinstance(priority, int) or isinstance(priority, bool):
        raise CoordinationError("priority must be an integer")
    if data.get("eligibility_authority") != "exact_dataset_allowlist":
        raise CoordinationError("eligibility_authority must be exact_dataset_allowlist")
    safe_id(data.get("training_objective_id"), "training_objective_id")
    if not isinstance(data.get("model_family"), str) or not data["model_family"].strip():
        raise CoordinationError("model_family is required")

    dataset = data.get("dataset")
    if not isinstance(dataset, dict):
        raise CoordinationError("dataset must be an object")
    if not isinstance(dataset.get("release_repository"), str) or not REPO_RE.fullmatch(
        dataset["release_repository"]
    ):
        raise CoordinationError("dataset.release_repository must be owner/repository")
    release_tag = dataset.get("release_tag")
    safe_id(release_tag, "dataset.release_tag")
    expected_release_url = (
        f"https://github.com/{dataset['release_repository']}/releases/tag/{release_tag}"
    )
    if dataset.get("release_url") != expected_release_url:
        raise CoordinationError(
            f"dataset.release_url must be the canonical URL: {expected_release_url}"
        )
    asset_name = dataset.get("archive_manifest_asset_name")
    if not isinstance(asset_name, str) or not ASSET_RE.fullmatch(asset_name):
        raise CoordinationError("dataset.archive_manifest_asset_name is invalid")
    code_commit = dataset.get("metadata_code_commit")
    if not isinstance(code_commit, str) or not re.fullmatch(r"[0-9a-f]{40,64}", code_commit):
        raise CoordinationError("dataset.metadata_code_commit must be a full Git commit SHA")
    if set(code_commit) == {"0"}:
        raise CoordinationError("dataset.metadata_code_commit is still a placeholder")
    for key in ("exact_allowlist_path", "ready_ledger_path", "target_variant",
                "objective_role", "no_mix_group"):
        if not isinstance(dataset.get(key), str) or not dataset[key].strip():
            raise CoordinationError(f"dataset.{key} is required")
    safe_control_path(dataset["exact_allowlist_path"])
    safe_control_path(dataset["ready_ledger_path"])
    validate_sha(dataset.get("archive_manifest_sha256"), "dataset.archive_manifest_sha256")
    validate_sha(dataset.get("exact_allowlist_sha256"), "dataset.exact_allowlist_sha256")
    validate_sha(dataset.get("ready_ledger_sha256"), "dataset.ready_ledger_sha256")
    if dataset["objective_role"] not in {"primary", "comparison_only"}:
        raise CoordinationError("dataset.objective_role must be primary or comparison_only")

    sources = data.get("source_files")
    if not isinstance(sources, list) or len(sources) < 2:
        raise CoordinationError("source_files must contain at least Original and Target")
    roles: set[str] = set()
    paths: set[str] = set()
    for index, record in enumerate(sources):
        if not isinstance(record, dict):
            raise CoordinationError(f"source_files[{index}] must be an object")
        path = record.get("path")
        if not isinstance(path, str):
            raise CoordinationError(f"source_files[{index}].path is required")
        safe_control_path(path)
        if path in paths:
            raise CoordinationError(f"duplicate source path: {path}")
        paths.add(path)
        validate_sha(record.get("sha256"), f"source_files[{index}].sha256")
        role = record.get("role")
        if role not in {"original", "target", "training_input"}:
            raise CoordinationError(f"unsupported source role: {role!r}")
        roles.add(role)
        if record.get("eligible_for_training") is not True:
            raise CoordinationError(f"source is not exact-allowlist eligible: {path}")
    if not {"original", "target"}.issubset(roles):
        raise CoordinationError("source_files require original and target roles")

    split = data.get("split_policy")
    if not isinstance(split, dict):
        raise CoordinationError("split_policy must be an object")
    if not isinstance(split.get("manifest_path"), str):
        raise CoordinationError("split_policy.manifest_path is required")
    safe_control_path(split["manifest_path"])
    validate_sha(split.get("manifest_sha256"), "split_policy.manifest_sha256")
    keys = split.get("whole_group_leakage_keys")
    if not isinstance(keys, list) or not keys or not all(isinstance(v, str) and v for v in keys):
        raise CoordinationError("split_policy.whole_group_leakage_keys must be non-empty")


def validate_claim(data: dict[str, Any], batch_id: str) -> None:
    if data.get("schema_version") != SCHEMA_VERSION:
        raise CoordinationError("claim schema_version must be 1")
    if data.get("kind") != "varimu_training_claim" or data.get("status") != "CLAIMED":
        raise CoordinationError("claim kind/status is invalid")
    if data.get("batch_id") != batch_id:
        raise CoordinationError("claim batch_id mismatch")
    safe_id(data.get("machine_id"), "machine_id")
    if not isinstance(data.get("machine_name"), str) or not data["machine_name"].strip():
        raise CoordinationError("claim machine_name is required")
    parse_utc(data.get("claimed_at_utc"), "claimed_at_utc")
    validate_sha(data.get("batch_manifest_sha256"), "batch_manifest_sha256")


class Backend:
    def list_batch_ids(self) -> list[str]:
        raise NotImplementedError

    def get_bytes(self, path: str) -> bytes:
        raise NotImplementedError

    def create_bytes(self, path: str, payload: bytes, message: str) -> dict[str, Any]:
        raise NotImplementedError

    def completed_batch_exists(self, batch_id: str) -> bool:
        raise NotImplementedError

    def create_completed_bytes(
        self, batch_id: str, run_id: str, payload: bytes, message: str
    ) -> dict[str, Any]:
        raise NotImplementedError

    def exists(self, path: str) -> bool:
        try:
            self.get_bytes(path)
            return True
        except RemoteMissing:
            return False


class FilesystemBackend(Backend):
    def __init__(self, root: Path, completion_index_root: str = "varimu-training/release-index"):
        self.root = root.expanduser().resolve()
        self.completion_index_root = safe_control_path(completion_index_root)

    def _path(self, path: str) -> Path:
        safe = safe_control_path(path)
        resolved = (self.root / safe).resolve()
        try:
            resolved.relative_to(self.root)
        except ValueError as exc:
            raise CoordinationError(f"path escapes control root: {path}") from exc
        return resolved

    def list_batch_ids(self) -> list[str]:
        queue = self._path("queue")
        if not queue.is_dir():
            return []
        return sorted(
            item.name for item in queue.iterdir()
            if item.is_dir() and SAFE_ID_RE.fullmatch(item.name)
        )

    def get_bytes(self, path: str) -> bytes:
        candidate = self._path(path)
        try:
            return candidate.read_bytes()
        except FileNotFoundError as exc:
            raise RemoteMissing(path) from exc

    def create_bytes(self, path: str, payload: bytes, message: str) -> dict[str, Any]:
        del message
        candidate = self._path(path)
        atomic_write(candidate, payload, exclusive=True)
        return {"path": str(candidate), "commit_sha": sha256_bytes(payload)}

    def completed_batch_exists(self, batch_id: str) -> bool:
        path = self._path(f"{self.completion_index_root}/{safe_id(batch_id, 'batch_id')}")
        return path.is_dir() and any(path.iterdir())

    def create_completed_bytes(
        self, batch_id: str, run_id: str, payload: bytes, message: str
    ) -> dict[str, Any]:
        return self.create_bytes(
            f"{self.completion_index_root}/{safe_id(batch_id, 'batch_id')}/"
            f"{safe_id(run_id, 'training_run_id')}/completed-run.json",
            payload,
            message,
        )


class GitHubBackend(Backend):
    def __init__(
        self, *, repo: str, branch: str, control_root: str,
        completion_index_root: str, gh_path: str,
    ):
        if not REPO_RE.fullmatch(repo):
            raise CoordinationError(f"invalid GitHub repo: {repo!r}")
        self.repo = repo
        self.branch = safe_id(branch, "branch")
        self.control_root = safe_control_path(control_root).rstrip("/")
        self.completion_index_root = safe_control_path(completion_index_root).rstrip("/")
        self.gh_path = gh_path

    def _full(self, path: str) -> str:
        return f"{self.control_root}/{safe_control_path(path)}"

    def _api(
        self,
        endpoint: str,
        *,
        method: str = "GET",
        body: dict[str, Any] | None = None,
        missing_ok: bool = False,
    ) -> Any:
        command = [
            self.gh_path,
            "api",
            "--method",
            method,
            "-H",
            "Accept: application/vnd.github+json",
            endpoint,
        ]
        input_text = None
        if body is not None:
            command += ["--input", "-"]
            input_text = json.dumps(body)
        result = subprocess.run(
            command,
            input=input_text,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if result.returncode != 0:
            combined = f"{result.stdout}\n{result.stderr}"
            if missing_ok and ("HTTP 404" in combined or '"status":"404"' in combined):
                raise RemoteMissing(endpoint)
            if "HTTP 409" in combined or "HTTP 422" in combined:
                raise CreateConflict(combined.strip())
            raise CoordinationError(f"GitHub API failed: {combined.strip()}")
        if not result.stdout.strip():
            return None
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError as exc:
            raise CoordinationError("GitHub API returned invalid JSON") from exc

    def list_batch_ids(self) -> list[str]:
        path = quote(self._full("queue"), safe="/")
        try:
            listing = self._api(
                f"repos/{self.repo}/contents/{path}?ref={quote(self.branch, safe='')}",
                missing_ok=True,
            )
        except RemoteMissing:
            return []
        if not isinstance(listing, list):
            raise CoordinationError("GitHub queue path is not a directory")
        return sorted(
            item["name"] for item in listing
            if isinstance(item, dict)
            and item.get("type") == "dir"
            and isinstance(item.get("name"), str)
            and SAFE_ID_RE.fullmatch(item["name"])
        )

    def get_bytes(self, path: str) -> bytes:
        full = quote(self._full(path), safe="/")
        return self.get_repository_bytes(self.repo, full, self.branch, encoded_path=True)

    def get_repository_bytes(
        self, repo: str, path: str, ref: str, *, encoded_path: bool = False
    ) -> bytes:
        full = path if encoded_path else quote(safe_control_path(path), safe="/")
        try:
            item = self._api(
                f"repos/{repo}/contents/{full}?ref={quote(ref, safe='')}",
                missing_ok=True,
            )
        except RemoteMissing:
            raise
        if not isinstance(item, dict) or item.get("type") != "file":
            raise CoordinationError(f"control path is not a file: {path}")
        content = item.get("content")
        if not isinstance(content, str) or item.get("encoding") != "base64":
            raise CoordinationError(f"unsupported GitHub content encoding: {path}")
        try:
            return base64.b64decode(content, validate=False)
        except ValueError as exc:
            raise CoordinationError(f"invalid base64 content: {path}") from exc

    def repository_path_exists(self, repo: str, path: str, ref: str) -> bool:
        full = quote(safe_control_path(path), safe="/")
        try:
            self._api(
                f"repos/{repo}/contents/{full}?ref={quote(ref, safe='')}",
                missing_ok=True,
            )
            return True
        except RemoteMissing:
            return False

    def release_view(self, repo: str, tag: str) -> dict[str, Any]:
        result = subprocess.run(
            [
                self.gh_path, "release", "view", tag, "--repo", repo,
                "--json", "url,tagName,assets",
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if result.returncode != 0:
            raise CoordinationError(
                f"GitHub Release lookup failed for {repo}@{tag}: {result.stderr.strip()}"
            )
        try:
            data = json.loads(result.stdout)
        except json.JSONDecodeError as exc:
            raise CoordinationError("GitHub Release lookup returned invalid JSON") from exc
        if not isinstance(data, dict):
            raise CoordinationError("GitHub Release lookup returned no object")
        return data

    def download_release_asset(self, repo: str, tag: str, asset_name: str) -> bytes:
        if not ASSET_RE.fullmatch(asset_name):
            raise CoordinationError(f"invalid Release asset name: {asset_name!r}")
        with tempfile.TemporaryDirectory(prefix="varimu-release-asset-") as temporary:
            result = subprocess.run(
                [
                    self.gh_path, "release", "download", tag, "--repo", repo,
                    "--pattern", asset_name, "--dir", temporary,
                ],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            if result.returncode != 0:
                raise CoordinationError(
                    f"GitHub Release asset download failed for {asset_name}: "
                    f"{result.stderr.strip()}"
                )
            path = Path(temporary) / asset_name
            if not path.is_file():
                raise CoordinationError(f"Release asset was not downloaded: {asset_name}")
            return path.read_bytes()

    def create_bytes(self, path: str, payload: bytes, message: str) -> dict[str, Any]:
        full = quote(self._full(path), safe="/")
        result = self._api(
            f"repos/{self.repo}/contents/{full}",
            method="PUT",
            body={
                "message": message,
                "content": base64.b64encode(payload).decode("ascii"),
                "branch": self.branch,
            },
        )
        if not isinstance(result, dict):
            raise CoordinationError("GitHub create returned no object")
        return {
            "path": self._full(path),
            "commit_sha": (result.get("commit") or {}).get("sha", ""),
            "html_url": (result.get("content") or {}).get("html_url", ""),
        }

    def completed_batch_exists(self, batch_id: str) -> bool:
        full = quote(
            f"{self.completion_index_root}/{safe_id(batch_id, 'batch_id')}", safe="/"
        )
        try:
            listing = self._api(
                f"repos/{self.repo}/contents/{full}?ref={quote(self.branch, safe='')}",
                missing_ok=True,
            )
        except RemoteMissing:
            return False
        return isinstance(listing, list) and bool(listing)

    def create_completed_bytes(
        self, batch_id: str, run_id: str, payload: bytes, message: str
    ) -> dict[str, Any]:
        relative = (
            f"{self.completion_index_root}/{safe_id(batch_id, 'batch_id')}/"
            f"{safe_id(run_id, 'training_run_id')}/completed-run.json"
        )
        full = quote(relative, safe="/")
        result = self._api(
            f"repos/{self.repo}/contents/{full}",
            method="PUT",
            body={
                "message": message,
                "content": base64.b64encode(payload).decode("ascii"),
                "branch": self.branch,
            },
        )
        if not isinstance(result, dict):
            raise CoordinationError("GitHub completed receipt create returned no object")
        return {
            "path": relative,
            "commit_sha": (result.get("commit") or {}).get("sha", ""),
            "html_url": (result.get("content") or {}).get("html_url", ""),
        }


def decode_json(raw: bytes, label: str) -> dict[str, Any]:
    try:
        data = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CoordinationError(f"invalid JSON in {label}: {exc}") from exc
    if not isinstance(data, dict):
        raise CoordinationError(f"JSON root must be an object: {label}")
    return data


def config_from_args(args: argparse.Namespace) -> dict[str, Any]:
    config: dict[str, Any] = {}
    if getattr(args, "config", None):
        config = load_json_file(args.config.expanduser().resolve())
        if config.get("schema_version") != SCHEMA_VERSION:
            raise CoordinationError("monitor config schema_version must be 1")
        if config.get("poll_interval_seconds") != 600:
            raise CoordinationError("production monitor interval must be exactly 600 seconds")
    for key in (
        "repo", "branch", "control_root", "local_root", "machine_name",
        "machine_id", "gh_path", "control_dir", "completion_index_root",
    ):
        value = getattr(args, key, None)
        if value is not None:
            config[key] = str(value)
    return config


def backend_from_config(config: dict[str, Any]) -> Backend:
    completion_index_root = config.get(
        "completion_index_root", "varimu-training/release-index"
    )
    safe_control_path(completion_index_root)
    if completion_index_root == "trained Data" or completion_index_root.startswith(
        "trained Data/"
    ):
        raise CoordinationError("the removed trained Data namespace must not be recreated")
    if config.get("control_dir"):
        return FilesystemBackend(
            Path(config["control_dir"]),
            completion_index_root,
        )
    required = ("repo", "branch", "control_root", "gh_path")
    missing = [key for key in required if not config.get(key)]
    if missing:
        raise CoordinationError(f"missing backend configuration: {', '.join(missing)}")
    return GitHubBackend(
        repo=config["repo"],
        branch=config["branch"],
        control_root=config["control_root"],
        completion_index_root=completion_index_root,
        gh_path=config["gh_path"],
    )


def local_root_from_config(config: dict[str, Any]) -> Path:
    value = config.get("local_root")
    if not value:
        raise CoordinationError("local_root is required")
    return Path(value).expanduser().resolve()


def machine_from_config(config: dict[str, Any]) -> tuple[str, str]:
    name = config.get("machine_name")
    machine_id = config.get("machine_id")
    if not isinstance(name, str) or not name.strip():
        raise CoordinationError("machine_name is required")
    return name.strip(), safe_id(machine_id, "machine_id")


@contextmanager
def monitor_lock(local_root: Path):
    lock_path = local_root / "state" / "monitor.lock"
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with lock_path.open("a+") as handle:
        try:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise CoordinationError("another local monitor cycle is running") from exc
        yield


def append_event(local_root: Path, event: dict[str, Any]) -> None:
    log_path = local_root / "logs" / "events.ndjson"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")


def local_active_records(local_root: Path) -> list[tuple[Path, dict[str, Any]]]:
    result: list[tuple[Path, dict[str, Any]]] = []
    active_root = local_root / "active"
    if not active_root.is_dir():
        return result
    for path in sorted(active_root.glob("*/active-run.json")):
        data = load_json_file(path)
        if data.get("status") in ACTIVE_STATES:
            result.append((path, data))
    return result


def completed_remote(backend: Backend, batch_id: str) -> bool:
    return backend.completed_batch_exists(batch_id)


def restore_local_claim(
    *, local_root: Path, batch: dict[str, Any], batch_raw: bytes,
    claim: dict[str, Any], claim_raw: bytes,
) -> Path:
    batch_id = batch["batch_id"]
    batch_path = local_root / "batches" / batch_id / "batch.json"
    if not batch_path.exists():
        atomic_write(batch_path, batch_raw, exclusive=True)
    claim_path = local_root / "batches" / batch_id / "claim.json"
    if not claim_path.exists():
        atomic_write(claim_path, claim_raw, exclusive=True)
    active_path = local_root / "active" / batch_id / "active-run.json"
    if not active_path.exists():
        active = {
            "schema_version": SCHEMA_VERSION,
            "kind": "varimu_local_active_run",
            "status": "CLAIMED",
            "batch_id": batch_id,
            "training_objective_id": batch["training_objective_id"],
            "machine_name": claim["machine_name"],
            "machine_id": claim["machine_id"],
            "claimed_at_utc": claim["claimed_at_utc"],
            "batch_manifest_sha256": sha256_bytes(batch_raw),
            "claim_sha256": sha256_bytes(claim_raw),
            "restored_at_utc": utc_now(),
        }
        atomic_write_json(active_path, active, exclusive=True)
    return active_path


def sorted_batches(
    backend: Backend,
) -> tuple[list[tuple[dict[str, Any], bytes]], list[dict[str, str]]]:
    batches: list[tuple[dict[str, Any], bytes]] = []
    invalid: list[dict[str, str]] = []
    for batch_id in backend.list_batch_ids():
        try:
            raw = backend.get_bytes(f"queue/{batch_id}/batch.json")
            data = decode_json(raw, f"queue/{batch_id}/batch.json")
            validate_batch(data, expected_id=batch_id)
            if isinstance(backend, GitHubBackend):
                verify_batch_remote_reference(backend, data)
            batches.append((data, raw))
        except CoordinationError as exc:
            invalid.append({"batch_id": batch_id, "reason": str(exc)})
    # Strict FIFO: priority is retained for audit compatibility but never lets a
    # newer batch jump ahead of the oldest remotely unclaimed batch.
    batches.sort(key=lambda item: (item[0]["created_at_utc"], item[0]["batch_id"]))
    return batches, invalid


def verify_batch_remote_reference(backend: GitHubBackend, batch: dict[str, Any]) -> None:
    dataset = batch["dataset"]
    repo = dataset["release_repository"]
    commit = dataset["metadata_code_commit"]
    if repo != backend.repo:
        raise CoordinationError(
            f"batch data repository must match the configured repository: {repo} != {backend.repo}"
        )
    release = backend.release_view(repo, dataset["release_tag"])
    if release.get("tagName") != dataset["release_tag"]:
        raise CoordinationError(
            f"batch Release tag mismatch: {release.get('tagName')!r}"
        )
    if release.get("url") != dataset["release_url"]:
        raise CoordinationError("batch Release URL does not match the published Release")
    assets = release.get("assets")
    if not isinstance(assets, list) or dataset["archive_manifest_asset_name"] not in {
        item.get("name") for item in assets if isinstance(item, dict)
    }:
        raise CoordinationError("batch archive-manifest asset is absent from the Release")
    archive_manifest = backend.download_release_asset(
        repo, dataset["release_tag"], dataset["archive_manifest_asset_name"]
    )
    if sha256_bytes(archive_manifest) != dataset["archive_manifest_sha256"]:
        raise CoordinationError("batch Release archive-manifest hash mismatch")
    checks = (
        ("exact_allowlist_path", "exact_allowlist_sha256"),
        ("ready_ledger_path", "ready_ledger_sha256"),
    )
    payloads: dict[str, bytes] = {}
    for path_key, sha_key in checks:
        payload = backend.get_repository_bytes(repo, dataset[path_key], commit)
        if sha256_bytes(payload) != dataset[sha_key]:
            raise CoordinationError(
                f"batch metadata hash mismatch for {dataset[path_key]} at {commit}"
            )
        payloads[path_key] = payload
    ledger = decode_json(payloads["ready_ledger_path"], dataset["ready_ledger_path"])
    if ledger.get("status") != "READY":
        raise CoordinationError("referenced training ledger is not READY")
    if ledger.get("training_objective_id") != batch["training_objective_id"]:
        raise CoordinationError("referenced READY ledger objective does not match the batch")


def watch_once(args: argparse.Namespace) -> int:
    config = config_from_args(args)
    backend = backend_from_config(config)
    local_root = local_root_from_config(config)
    machine_name, machine_id = machine_from_config(config)
    local_root.mkdir(parents=True, exist_ok=True)

    with monitor_lock(local_root):
        active = local_active_records(local_root)
        if active:
            result = {
                "status": "BUSY",
                "active_batches": [record[1].get("batch_id") for record in active],
                "checked_at_utc": utc_now(),
            }
            append_event(local_root, result)
            print(json.dumps(result, ensure_ascii=False))
            return 0

        batches, invalid = sorted_batches(backend)
        available: list[tuple[dict[str, Any], bytes]] = []
        own_claims: list[tuple[dict[str, Any], bytes, dict[str, Any], bytes]] = []

        # Scan the complete queue before choosing work.  This makes the result
        # explicitly oldest-first across every batch visible in this cycle.
        for batch, batch_raw in batches:
            batch_id = batch["batch_id"]
            if completed_remote(backend, batch_id):
                continue
            claim_path = f"queue/{batch_id}/claim.json"
            try:
                claim_raw = backend.get_bytes(claim_path)
            except RemoteMissing:
                claim_raw = b""
            if claim_raw:
                try:
                    claim = decode_json(claim_raw, claim_path)
                    validate_claim(claim, batch_id)
                except CoordinationError as exc:
                    invalid.append({"batch_id": batch_id, "reason": str(exc)})
                    continue
                if claim["machine_id"] == machine_id:
                    own_claims.append((batch, batch_raw, claim, claim_raw))
                continue

            if (local_root / "batches" / batch_id).exists():
                invalid.append({
                    "batch_id": batch_id,
                    "reason": "batch already exists locally without a recoverable active claim",
                })
                continue

            available.append((batch, batch_raw))

        if own_claims:
            batch, batch_raw, claim, claim_raw = own_claims[0]
            batch_id = batch["batch_id"]
            active_path = restore_local_claim(
                local_root=local_root,
                batch=batch,
                batch_raw=batch_raw,
                claim=claim,
                claim_raw=claim_raw,
            )
            result = {
                "status": "RECOVERED_CLAIM",
                "batch_id": batch_id,
                "active_record": str(active_path),
                "checked_at_utc": utc_now(),
            }
            append_event(local_root, result)
            print(json.dumps(result, ensure_ascii=False))
            return 0

        for batch, batch_raw in available:
            batch_id = batch["batch_id"]
            claim_path = f"queue/{batch_id}/claim.json"
            claimed_at = utc_now()
            claim = {
                "schema_version": SCHEMA_VERSION,
                "kind": "varimu_training_claim",
                "status": "CLAIMED",
                "batch_id": batch_id,
                "training_objective_id": batch["training_objective_id"],
                "machine_name": machine_name,
                "machine_id": machine_id,
                "claimed_at_utc": claimed_at,
                "batch_manifest_sha256": sha256_bytes(batch_raw),
                "repository": config.get("repo", "filesystem-test-backend"),
                "branch": config.get("branch", "filesystem-test-branch"),
                "poll_interval_seconds": 600,
                "automatic_takeover": False,
            }
            claim_raw = canonical_json_bytes(claim)
            if args.dry_run:
                result = {
                    "status": "WOULD_CLAIM",
                    "batch_id": batch_id,
                    "machine_name": machine_name,
                    "machine_id": machine_id,
                    "checked_at_utc": claimed_at,
                }
                print(json.dumps(result, ensure_ascii=False))
                return 0
            try:
                remote = backend.create_bytes(
                    claim_path,
                    claim_raw,
                    f"Claim Vari-Mu training batch {batch_id} on {machine_name}",
                )
            except CreateConflict:
                # Another worker won the create-only race. Inspect the next batch.
                continue
            active_path = restore_local_claim(
                local_root=local_root,
                batch=batch,
                batch_raw=batch_raw,
                claim=claim,
                claim_raw=claim_raw,
            )
            result = {
                "status": "CLAIMED",
                "batch_id": batch_id,
                "machine_name": machine_name,
                "machine_id": machine_id,
                "claimed_at_utc": claimed_at,
                "active_record": str(active_path),
                "remote": remote,
            }
            append_event(local_root, result)
            print(json.dumps(result, ensure_ascii=False))
            return 0

        result = {
            "status": "NO_AVAILABLE_BATCH",
            "checked_at_utc": utc_now(),
            "invalid_batches": invalid,
        }
        append_event(local_root, result)
        print(json.dumps(result, ensure_ascii=False))
        return 0


def publish_batch(args: argparse.Namespace) -> int:
    config = config_from_args(args)
    backend = backend_from_config(config)
    path = args.manifest.expanduser().resolve()
    raw = path.read_bytes()
    data = decode_json(raw, str(path))
    validate_batch(data)
    if isinstance(backend, GitHubBackend):
        verify_batch_remote_reference(backend, data)
    batch_id = data["batch_id"]
    result = backend.create_bytes(
        f"queue/{batch_id}/batch.json",
        raw,
        f"Publish training-ready Vari-Mu batch {batch_id}",
    )
    print(json.dumps({"status": "PUBLISHED", "batch_id": batch_id, "remote": result}, ensure_ascii=False))
    return 0


def validate_batch_command(args: argparse.Namespace) -> int:
    path = args.manifest.expanduser().resolve()
    data = load_json_file(path)
    validate_batch(data)
    print(json.dumps({"status": "VALID", "batch_id": data["batch_id"], "sha256": sha256_file(path)}))
    return 0


def set_local_status(args: argparse.Namespace) -> int:
    config = config_from_args(args)
    local_root = local_root_from_config(config)
    machine_name, machine_id = machine_from_config(config)
    batch_id = safe_id(args.batch_id, "batch_id")
    path = local_root / "active" / batch_id / "active-run.json"
    data = load_json_file(path)
    if data.get("machine_id") != machine_id or data.get("machine_name") != machine_name:
        raise CoordinationError("local active record belongs to a different machine identity")
    current = data.get("status")
    allowed = {
        "CLAIMED": {"TRAINING", "FINALIZING", "FAILED"},
        "TRAINING": {"FINALIZING", "FAILED"},
        "FINALIZING": {"COMPLETED", "FAILED"},
    }
    target = args.status
    if target not in allowed.get(current, set()):
        raise CoordinationError(f"invalid local transition {current!r} -> {target!r}")
    data["status"] = target
    data[f"{target.lower()}_at_utc"] = utc_now()
    if args.training_run_id:
        data["training_run_id"] = safe_id(args.training_run_id, "training_run_id")
    atomic_write_json(path, data)
    result = {"status": target, "batch_id": batch_id, "active_record": str(path)}
    append_event(local_root, result | {"recorded_at_utc": utc_now()})
    print(json.dumps(result, ensure_ascii=False))
    return 0


def add_backend_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--config", type=Path)
    parser.add_argument("--repo")
    parser.add_argument("--branch")
    parser.add_argument("--control-root")
    parser.add_argument("--completion-index-root")
    parser.add_argument("--control-dir", type=Path)
    parser.add_argument("--local-root", type=Path)
    parser.add_argument("--machine-name")
    parser.add_argument("--machine-id")
    parser.add_argument("--gh-path")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    watch = sub.add_parser("watch-once", help="inspect and atomically claim one batch")
    add_backend_args(watch)
    watch.add_argument("--dry-run", action="store_true")
    watch.set_defaults(func=watch_once)

    publish = sub.add_parser("publish-batch", help="create one immutable READY batch manifest")
    add_backend_args(publish)
    publish.add_argument("--manifest", type=Path, required=True)
    publish.set_defaults(func=publish_batch)

    validate = sub.add_parser("validate-batch", help="validate a local batch manifest")
    validate.add_argument("manifest", type=Path)
    validate.set_defaults(func=validate_batch_command)

    status = sub.add_parser("set-local-status", help="transition the local worker state")
    add_backend_args(status)
    status.add_argument("--batch-id", required=True)
    status.add_argument("--status", choices=("TRAINING", "FINALIZING", "COMPLETED", "FAILED"), required=True)
    status.add_argument("--training-run-id")
    status.set_defaults(func=set_local_status)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        return args.func(args)
    except (CoordinationError, OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
