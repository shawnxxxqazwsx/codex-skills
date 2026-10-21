#!/usr/bin/env python3
"""Package and publish one validated Vari-Mu completed training folder."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import tempfile
import threading
from typing import Any
from urllib.parse import quote

import validate_completed_run as completed_validator
import varimu_training_coordinator as coordinator


DEFAULT_MAX_PART_MIB = 1900
MAX_RELEASE_PART_MIB = 1900
MAX_CODE_METADATA_BYTES = 10 * 1024 * 1024


class PublishError(RuntimeError):
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


def write_json(path: Path, data: dict[str, Any], *, exclusive: bool = False) -> None:
    coordinator.atomic_write_json(path, data, exclusive=exclusive)


class SplitSink:
    def __init__(self, output_dir: Path, base_name: str, max_part_bytes: int):
        self.output_dir = output_dir
        self.base_name = base_name
        self.max_part_bytes = max_part_bytes
        self.handle = None
        self.digest = None
        self.size = 0
        self.index = 0
        self.parts: list[dict[str, Any]] = []

    def _open(self) -> None:
        self.index += 1
        path = self.output_dir / f"{self.base_name}.tar.zst.part-{self.index:04d}"
        self.handle = path.open("xb")
        self.digest = hashlib.sha256()
        self.size = 0

    def _close(self) -> None:
        if self.handle is None:
            return
        self.handle.flush()
        os.fsync(self.handle.fileno())
        path = Path(self.handle.name)
        self.handle.close()
        self.parts.append({
            "name": path.name,
            "path": str(path),
            "size": self.size,
            "sha256": self.digest.hexdigest(),
        })
        self.handle = None
        self.digest = None
        self.size = 0

    def write(self, data: bytes) -> None:
        view = memoryview(data)
        while view:
            if self.handle is None:
                self._open()
            remaining = self.max_part_bytes - self.size
            chunk = view[:remaining]
            self.handle.write(chunk)
            self.digest.update(chunk)
            self.size += len(chunk)
            view = view[len(chunk):]
            if self.size == self.max_part_bytes:
                self._close()

    def close(self) -> None:
        self._close()


def tarinfo_for(archive: tarfile.TarFile, path: Path, arcname: str) -> tarfile.TarInfo:
    info = archive.gettarinfo(str(path), arcname=arcname)
    info.uid = 0
    info.gid = 0
    info.uname = "root"
    info.gname = "root"
    info.mtime = 0
    return info


def package_run(
    run_root: Path, output_dir: Path, max_part_bytes: int, batch_id: str
) -> list[dict[str, Any]]:
    zstd = shutil.which("zstd")
    if not zstd:
        raise PublishError("zstd is required to package completed runs")
    output_dir.mkdir(parents=True, exist_ok=False)
    sink = SplitSink(output_dir, f"varimu-completed-{run_root.name}", max_part_bytes)
    process = subprocess.Popen(
        [zstd, "-19", "-T0", "-c"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if process.stdin is None or process.stdout is None or process.stderr is None:
        raise PublishError("failed to create zstd packaging pipeline")
    drain_errors: list[BaseException] = []

    def drain() -> None:
        try:
            for chunk in iter(lambda: process.stdout.read(4 * 1024 * 1024), b""):
                sink.write(chunk)
        except BaseException as exc:
            drain_errors.append(exc)
        finally:
            sink.close()

    thread = threading.Thread(target=drain, name="varimu-package-split", daemon=True)
    thread.start()
    try:
        with tarfile.open(fileobj=process.stdin, mode="w|", format=tarfile.PAX_FORMAT) as archive:
            for path in sorted(run_root.rglob("*"), key=lambda p: p.relative_to(run_root).as_posix()):
                if path.is_symlink():
                    raise PublishError(f"symlink is not permitted: {path}")
                if not path.is_file():
                    continue
                relative = path.relative_to(run_root).as_posix()
                arcname = (
                    f"varimu-training-completed/{batch_id}/{run_root.name}/{relative}"
                )
                info = tarinfo_for(archive, path, arcname)
                with path.open("rb") as handle:
                    archive.addfile(info, handle)
        process.stdin.close()
        thread.join()
        stderr = process.stderr.read().decode("utf-8", errors="replace")
        return_code = process.wait()
        process.stdout.close()
        process.stderr.close()
    except BaseException:
        process.kill()
        thread.join(timeout=5)
        raise
    if drain_errors:
        raise PublishError(f"package output failed: {drain_errors[0]}")
    if return_code != 0:
        raise PublishError(f"zstd failed ({return_code}): {stderr.strip()}")
    if not sink.parts:
        raise PublishError("packaging produced no parts")
    return sink.parts


def run_gh(gh_path: str, args: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        [gh_path, *args], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        check=False,
    )
    if check and result.returncode != 0:
        raise PublishError(f"gh {' '.join(args[:3])} failed: {result.stderr.strip()}")
    return result


def run_git(
    repo: Path, args: list[str], *, check: bool = True
) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        ["git", "-C", str(repo), *args], text=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
    )
    if check and result.returncode != 0:
        raise PublishError(f"git {' '.join(args[:3])} failed: {result.stderr.strip()}")
    return result


def verify_local_claim(
    config: dict[str, Any], backend: coordinator.Backend,
    manifest: dict[str, Any], run_root: Path,
) -> tuple[bytes, Path, dict[str, Any]]:
    batch_id = manifest["batch_id"]
    claim_raw = backend.get_bytes(f"queue/{batch_id}/claim.json")
    claim = coordinator.decode_json(claim_raw, f"queue/{batch_id}/claim.json")
    coordinator.validate_claim(claim, batch_id)
    expected = manifest["claim"]
    for key in ("machine_name", "machine_id", "claimed_at_utc"):
        if claim.get(key) != expected.get(key):
            raise PublishError(f"remote claim {key} does not match completed manifest")
    if coordinator.sha256_bytes(claim_raw) != expected.get("claim_sha256"):
        raise PublishError("remote claim SHA-256 does not match completed manifest")
    if claim.get("training_objective_id") != manifest.get("training_objective_id"):
        raise PublishError("remote claim objective does not match completed manifest")

    local_root = coordinator.local_root_from_config(config)
    active_path = local_root / "active" / batch_id / "active-run.json"
    active = coordinator.load_json_file(active_path)
    if active.get("status") != "FINALIZING":
        raise PublishError("local active state must be FINALIZING before publication")
    if active.get("machine_id") != claim.get("machine_id"):
        raise PublishError("local active record belongs to another machine")
    if active.get("training_run_id") != manifest.get("training_run_id"):
        raise PublishError("local active training_run_id does not match completed manifest")
    expected_root = local_root / "completed" / manifest["training_run_id"]
    if run_root != expected_root.resolve():
        raise PublishError(f"run directory must be the unified completed path: {expected_root}")
    return claim_raw, active_path, active


def load_existing_package(
    package_dir: Path, batch_id: str, training_run_id: str
) -> tuple[list[dict[str, Any]], Path, dict[str, Any]]:
    manifest_path = package_dir / "package-manifest-v1.json"
    if not manifest_path.is_file():
        raise PublishError(
            f"package directory exists without a sealed manifest; preserve and review it: {package_dir}"
        )
    data = coordinator.load_json_file(manifest_path)
    if data.get("batch_id") != batch_id or data.get("training_run_id") != training_run_id:
        raise PublishError("existing local package identity does not match this run")
    if data.get("transport") != "immutable_github_release_assets":
        raise PublishError(
            "existing local package uses a superseded transport; preserve and review it"
        )
    records = data.get("parts")
    if not isinstance(records, list) or not records:
        raise PublishError("existing local package has no part inventory")
    parts: list[dict[str, Any]] = []
    for record in records:
        path = package_dir / record["name"]
        if not path.is_file():
            raise PublishError(f"local backup part is missing: {path}")
        if path.stat().st_size != record["size"] or sha256_file(path) != record["sha256"]:
            raise PublishError(f"local backup part failed verification: {path}")
        parts.append({**record, "path": str(path)})
    return parts, manifest_path, data


def release_view(
    gh_path: str, repo_name: str, tag: str, *, missing_ok: bool = False
) -> dict[str, Any] | None:
    result = run_gh(
        gh_path,
        [
            "release", "view", tag, "--repo", repo_name,
            "--json", "url,tagName,name,body,isDraft,isPrerelease,assets",
        ],
        check=False,
    )
    if result.returncode != 0:
        combined = f"{result.stdout}\n{result.stderr}".lower()
        if missing_ok and ("release not found" in combined or "http 404" in combined):
            return None
        raise PublishError(f"GitHub Release lookup failed: {result.stderr.strip()}")
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise PublishError("GitHub Release lookup returned invalid JSON") from exc
    if not isinstance(data, dict):
        raise PublishError("GitHub Release lookup returned no object")
    return data


def release_assets(data: dict[str, Any]) -> dict[str, dict[str, Any]]:
    records = data.get("assets")
    if not isinstance(records, list):
        raise PublishError("GitHub Release asset listing is invalid")
    result: dict[str, dict[str, Any]] = {}
    for record in records:
        if not isinstance(record, dict) or not isinstance(record.get("name"), str):
            raise PublishError("GitHub Release contains an invalid asset record")
        name = record["name"]
        if name in result:
            raise PublishError(f"GitHub Release contains a duplicate asset: {name}")
        result[name] = record
    return result


def download_release_asset(
    gh_path: str, repo_name: str, tag: str, name: str
) -> bytes:
    with tempfile.TemporaryDirectory(prefix="varimu-release-download-") as temporary:
        run_gh(
            gh_path,
            [
                "release", "download", tag, "--repo", repo_name,
                "--pattern", name, "--dir", temporary,
            ],
        )
        path = Path(temporary) / name
        if not path.is_file():
            raise PublishError(f"GitHub Release asset was not downloaded: {name}")
        return path.read_bytes()


def verify_remote_asset(
    *, gh_path: str, repo_name: str, tag: str, remote: dict[str, Any],
    expected_path: Path, expected_size: int, expected_sha256: str,
) -> None:
    if remote.get("size") != expected_size:
        raise PublishError(f"GitHub Release asset size differs: {expected_path.name}")
    digest = remote.get("digest")
    if isinstance(digest, str) and digest:
        if digest != f"sha256:{expected_sha256}":
            raise PublishError(f"GitHub Release asset digest differs: {expected_path.name}")
        return
    payload = download_release_asset(
        gh_path, repo_name, tag, expected_path.name
    )
    if len(payload) != expected_size or coordinator.sha256_bytes(payload) != expected_sha256:
        raise PublishError(f"GitHub Release asset bytes differ: {expected_path.name}")


def publish_or_recover_release(
    *, gh_path: str, repo_name: str, batch_id: str, training_run_id: str,
    parts: list[dict[str, Any]], package_manifest: Path,
) -> dict[str, Any]:
    tag = f"varimu-training-{training_run_id}"
    if len(tag) > 255:
        raise PublishError("generated GitHub Release tag is too long")
    title = f"Vari-Mu completed training {training_run_id}"
    manifest_sha = sha256_file(package_manifest)
    body = (
        "Immutable Vari-Mu completed training archive.\n\n"
        f"Batch: `{batch_id}`\n"
        f"Run: `{training_run_id}`\n"
        f"Package manifest SHA-256: `{manifest_sha}`\n"
        "Local complete data and verified package parts are retained permanently."
    )
    release = release_view(gh_path, repo_name, tag, missing_ok=True)
    if release is None:
        created = run_gh(
            gh_path,
            [
                "release", "create", tag, "--repo", repo_name,
                "--title", title, "--notes", body,
            ],
            check=False,
        )
        if created.returncode != 0:
            release = release_view(gh_path, repo_name, tag, missing_ok=True)
            if release is None:
                raise PublishError(
                    f"GitHub Release creation failed: {created.stderr.strip()}"
                )
        else:
            release = release_view(gh_path, repo_name, tag)
    assert release is not None
    expected_url = f"https://github.com/{repo_name}/releases/tag/{tag}"
    if (
        release.get("tagName") != tag
        or release.get("url") != expected_url
        or release.get("name") != title
        or release.get("body") != body
        or release.get("isDraft") is not False
        or release.get("isPrerelease") is not False
    ):
        raise PublishError(f"existing GitHub Release identity differs: {tag}")

    expected: dict[str, tuple[Path, int, str]] = {
        package_manifest.name: (
            package_manifest, package_manifest.stat().st_size, manifest_sha
        )
    }
    for part in parts:
        path = Path(part["path"])
        if path.name in expected:
            raise PublishError(f"duplicate package asset name: {path.name}")
        expected[path.name] = (path, part["size"], part["sha256"])

    assets = release_assets(release)
    unexpected = sorted(set(assets) - set(expected))
    if unexpected:
        raise PublishError(
            f"existing GitHub Release has unexpected assets: {', '.join(unexpected)}"
        )
    for name, (path, size, digest) in expected.items():
        if name in assets:
            verify_remote_asset(
                gh_path=gh_path, repo_name=repo_name, tag=tag,
                remote=assets[name], expected_path=path,
                expected_size=size, expected_sha256=digest,
            )
            continue
        run_gh(
            gh_path,
            ["release", "upload", tag, str(path), "--repo", repo_name],
        )

    release = release_view(gh_path, repo_name, tag)
    assert release is not None
    assets = release_assets(release)
    if set(assets) != set(expected):
        raise PublishError("GitHub Release asset set is incomplete after upload")
    for name, (path, size, digest) in expected.items():
        verify_remote_asset(
            gh_path=gh_path, repo_name=repo_name, tag=tag,
            remote=assets[name], expected_path=path,
            expected_size=size, expected_sha256=digest,
        )
    return {"tag": tag, "url": expected_url, "assets": assets}


def publish_code_folder(
    *, gh_path: str, repo_name: str, branch: str, completion_index_root: str,
    batch_id: str, training_run_id: str, metadata_files: dict[str, Path],
) -> dict[str, str]:
    with tempfile.TemporaryDirectory(prefix="varimu-code-publish-") as temporary:
        clone = Path(temporary) / "repo"
        run_gh(
            gh_path,
            [
                "repo", "clone", repo_name, str(clone), "--",
                "--filter=blob:none", "--single-branch", "--branch", branch,
            ],
        )
        relative = Path(completion_index_root) / batch_id / training_run_id
        destination = clone / relative
        if destination.exists():
            raise PublishError(f"Code-page completion index already exists: {relative}")
        destination.mkdir(parents=True, exist_ok=False)

        total_size = sum(source.stat().st_size for source in metadata_files.values())
        if total_size > MAX_CODE_METADATA_BYTES:
            raise PublishError("Code-page completion metadata exceeds the 10 MiB limit")
        for name, source in metadata_files.items():
            if Path(name).name != name or not source.is_file():
                raise PublishError(f"invalid Code-page metadata file: {name}")
            target = destination / name
            shutil.copy2(source, target)
            if sha256_file(source) != sha256_file(target):
                raise PublishError(f"copied Code-page metadata failed hash verification: {target}")

        run_git(clone, ["config", "user.name", "Vari-Mu Training Worker"])
        run_git(clone, ["config", "user.email", "varimu-training@users.noreply.github.com"])
        run_git(clone, ["add", "--", relative.as_posix()])
        run_git(
            clone,
            ["commit", "-m", f"Publish completed Vari-Mu training {training_run_id}"],
        )
        for attempt in range(3):
            pushed = run_git(clone, ["push", "origin", f"HEAD:{branch}"], check=False)
            if pushed.returncode == 0:
                commit = run_git(clone, ["rev-parse", "HEAD"]).stdout.strip()
                return {"commit_sha": commit, "code_path": relative.as_posix()}
            run_git(clone, ["fetch", "origin", branch])
            exists = run_git(
                clone,
                ["cat-file", "-e", f"origin/{branch}:{relative.as_posix()}/completed-run.json"],
                check=False,
            )
            if exists.returncode == 0:
                raise PublishError(f"another publisher created the completed folder: {relative}")
            if attempt == 2:
                raise PublishError(f"Code-page push failed after retries: {pushed.stderr.strip()}")
            run_git(clone, ["rebase", f"origin/{branch}"])
    raise PublishError("unreachable Code-page publication state")


def recover_code_publication(
    *, backend: coordinator.GitHubBackend, branch: str,
    completion_index_root: str, batch_id: str, training_run_id: str,
    metadata_files: dict[str, Path],
) -> dict[str, str] | None:
    relative = f"{completion_index_root}/{batch_id}/{training_run_id}"
    receipt_path = f"{relative}/completed-run.json"
    try:
        remote_receipt = backend.get_repository_bytes(
            backend.repo, receipt_path, branch
        )
    except coordinator.RemoteMissing:
        return None
    if remote_receipt != metadata_files["completed-run.json"].read_bytes():
        raise PublishError(f"existing Code-page receipt differs: {receipt_path}")
    for name, local_path in metadata_files.items():
        remote_payload = backend.get_repository_bytes(
            backend.repo, f"{relative}/{name}", branch
        )
        if remote_payload != local_path.read_bytes():
            raise PublishError(f"existing Code-page metadata differs: {relative}/{name}")
    commits = backend._api(
        f"repos/{backend.repo}/commits?sha={branch}&path="
        f"{quote(receipt_path, safe='')}&per_page=1"
    )
    if not isinstance(commits, list) or not commits or not isinstance(commits[0], dict):
        raise PublishError(f"cannot resolve existing Code-page publication commit: {relative}")
    return {
        "commit_sha": str(commits[0].get("sha", "")),
        "code_path": relative,
        "recovered": "true",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_directory", type=Path)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--max-part-mib", type=int, default=DEFAULT_MAX_PART_MIB)
    args = parser.parse_args()
    try:
        config = coordinator.load_json_file(args.config.expanduser().resolve())
        if config.get("poll_interval_seconds") != 600:
            raise PublishError("monitor config is not the frozen 600-second protocol")
        backend = coordinator.backend_from_config(config)
        if not isinstance(backend, coordinator.GitHubBackend):
            raise PublishError("completed publication requires the GitHub backend")
        run_root = args.run_directory.expanduser().resolve()
        manifest_path = run_root / "completed-run-v1.json"
        manifest = completed_validator.load_json(manifest_path)
        completed_validator.validate_manifest(run_root, manifest, check_files=True)
        claim_raw, active_path, active = verify_local_claim(config, backend, manifest, run_root)

        training_run_id = manifest["training_run_id"]
        batch_id = manifest["batch_id"]
        completion_index_root = config.get(
            "completion_index_root", "varimu-training/release-index"
        )
        completion_index_root = coordinator.safe_control_path(completion_index_root)
        if completion_index_root == "trained Data" or completion_index_root.startswith(
            "trained Data/"
        ):
            raise PublishError("the removed trained Data namespace must not be recreated")
        max_part_bytes = args.max_part_mib * 1024 * 1024
        if max_part_bytes <= 0 or args.max_part_mib > MAX_RELEASE_PART_MIB:
            raise PublishError(
                f"max-part-mib must be in 1..{MAX_RELEASE_PART_MIB} for Release assets"
            )
        local_root = coordinator.local_root_from_config(config)
        package_dir = local_root / "packages" / training_run_id
        if package_dir.exists():
            parts, package_manifest, package_manifest_data = load_existing_package(
                package_dir, batch_id, training_run_id
            )
        else:
            parts = package_run(run_root, package_dir, max_part_bytes, batch_id)
            # Prove no file changed while it was being packaged.
            completed_validator.validate_manifest(run_root, manifest, check_files=True)
            package_manifest_data = {
                "schema_version": 1,
                "kind": "varimu_completed_training_package",
                "created_at_utc": utc_now(),
                "batch_id": batch_id,
                "training_run_id": training_run_id,
                "machine_name": manifest["claim"]["machine_name"],
                "machine_id": manifest["claim"]["machine_id"],
                "completed_run_manifest_sha256": sha256_file(manifest_path),
                "claim_sha256": coordinator.sha256_bytes(claim_raw),
                "compression": "zstd-19",
                "part_limit_mib": args.max_part_mib,
                "transport": "immutable_github_release_assets",
                "release_repository": config["repo"],
                "release_tag": f"varimu-training-{training_run_id}",
                "release_url": (
                    f"https://github.com/{config['repo']}/releases/tag/"
                    f"varimu-training-{training_run_id}"
                ),
                "archive_root": (
                    f"varimu-training-completed/{batch_id}/{training_run_id}"
                ),
                "local_backup_policy": "retain_complete_run_and_verified_parts_never_move_or_delete_unique_copy",
                "parts": [
                    {key: value for key, value in part.items() if key != "path"}
                    for part in parts
                ],
            }
            package_manifest = package_dir / "package-manifest-v1.json"
            write_json(package_manifest, package_manifest_data, exclusive=True)

        expected_package_identity = {
            "completed_run_manifest_sha256": sha256_file(manifest_path),
            "claim_sha256": coordinator.sha256_bytes(claim_raw),
            "release_repository": config["repo"],
            "release_tag": f"varimu-training-{training_run_id}",
            "release_url": (
                f"https://github.com/{config['repo']}/releases/tag/"
                f"varimu-training-{training_run_id}"
            ),
        }
        for key, value in expected_package_identity.items():
            if package_manifest_data.get(key) != value:
                raise PublishError(f"local package manifest {key} differs from this run")

        release = publish_or_recover_release(
            gh_path=config["gh_path"],
            repo_name=config["repo"],
            batch_id=batch_id,
            training_run_id=training_run_id,
            parts=parts,
            package_manifest=package_manifest,
        )
        asset_records = [{**part} for part in package_manifest_data["parts"]]
        asset_records.append({
            "name": package_manifest.name,
            "size": package_manifest.stat().st_size,
            "sha256": sha256_file(package_manifest),
        })
        annotation_path = run_root / "ANNOTATION.md"
        ledger_artifacts = [
            record for record in manifest["artifacts"]
            if record.get("role") == "training_ledger_receipt"
        ]
        if len(ledger_artifacts) != 1:
            raise PublishError("completed run must contain exactly one training ledger receipt")
        ledger_path = run_root / ledger_artifacts[0]["path"]
        code_path = f"{completion_index_root}/{batch_id}/{training_run_id}"
        receipt = {
            "schema_version": 1,
            "kind": "varimu_completed_training_receipt",
            "status": "COMPLETED",
            "batch_id": batch_id,
            "training_run_id": training_run_id,
            "training_objective_id": manifest["training_objective_id"],
            "machine_name": manifest["claim"]["machine_name"],
            "machine_id": manifest["claim"]["machine_id"],
            "claimed_at_utc": manifest["claim"]["claimed_at_utc"],
            "completed_at_utc": manifest["completed_at_utc"],
            "published_at_utc": utc_now(),
            "claim_sha256": coordinator.sha256_bytes(claim_raw),
            "completed_run_manifest_sha256": sha256_file(manifest_path),
            "annotation_sha256": sha256_file(annotation_path),
            "implementation": manifest["implementation"],
            "acceptance": manifest["acceptance"],
            "known_limits": manifest["known_limits"],
            "storage": "github_release_with_lightweight_code_index",
            "repository": config["repo"],
            "branch": config["branch"],
            "release_tag": release["tag"],
            "release_url": release["url"],
            "code_index_path": code_path,
            "package_manifest_sha256": sha256_file(package_manifest),
            "training_ledger_receipt_sha256": sha256_file(ledger_path),
            "local_complete_run_retained": True,
            "local_verified_package_retained": True,
            "local_backup_policy": (
                "Local complete run and verified package parts are retained. "
                "Publication copies them and never moves or deletes the unique source."
            ),
            "assets": asset_records,
        }
        local_receipt = package_dir / "completion-receipt.json"
        if local_receipt.exists():
            prior_receipt = coordinator.load_json_file(local_receipt)
            receipt["published_at_utc"] = prior_receipt.get("published_at_utc")
            if prior_receipt != receipt:
                raise PublishError(
                    f"existing local completion receipt identity differs; preserve and review: {local_receipt}"
                )
            receipt = prior_receipt
            receipt_raw = local_receipt.read_bytes()
        else:
            receipt_raw = coordinator.canonical_json_bytes(receipt)
            coordinator.atomic_write(local_receipt, receipt_raw, exclusive=True)
        metadata_files = {
            "completed-run.json": local_receipt,
            "completed-run-v1.json": manifest_path,
            "ANNOTATION.md": annotation_path,
            "package-manifest-v1.json": package_manifest,
            "training-ledger-receipt.json": ledger_path,
        }
        remote = recover_code_publication(
            backend=backend,
            branch=config["branch"],
            completion_index_root=completion_index_root,
            batch_id=batch_id,
            training_run_id=training_run_id,
            metadata_files=metadata_files,
        )
        if remote is None:
            remote = publish_code_folder(
                gh_path=config["gh_path"],
                repo_name=config["repo"],
                branch=config["branch"],
                completion_index_root=completion_index_root,
                batch_id=batch_id,
                training_run_id=training_run_id,
                metadata_files=metadata_files,
            )
        active["status"] = "COMPLETED"
        active["completed_at_utc"] = receipt["published_at_utc"]
        active["code_commit"] = remote["commit_sha"]
        active["code_path"] = remote["code_path"]
        active["release_tag"] = release["tag"]
        active["release_url"] = release["url"]
        active["completed_receipt_sha256"] = coordinator.sha256_bytes(receipt_raw)
        coordinator.atomic_write_json(active_path, active)
        result = {
            "status": "COMPLETED",
            "batch_id": batch_id,
            "training_run_id": training_run_id,
            "code_commit": remote["commit_sha"],
            "code_path": remote["code_path"],
            "release_tag": release["tag"],
            "release_url": release["url"],
            "package_manifest": str(package_manifest),
            "local_backup_retained": True,
        }
        coordinator.append_event(local_root, result | {"recorded_at_utc": utc_now()})
        print(json.dumps(result, ensure_ascii=False))
        return 0
    except (
        PublishError, completed_validator.ValidationError,
        coordinator.CoordinationError, OSError, UnicodeError, json.JSONDecodeError,
    ) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
