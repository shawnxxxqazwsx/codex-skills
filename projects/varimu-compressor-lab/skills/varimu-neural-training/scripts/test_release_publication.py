#!/usr/bin/env python3
"""Offline create/recover/tamper regression for Release publication."""

from __future__ import annotations

import json
import os
from pathlib import Path
import stat
import subprocess
import tempfile

import publish_completed_run as publisher


FAKE_GH = r'''#!/usr/bin/env python3
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

root = Path(os.environ["VARIMU_FAKE_GH_ROOT"])
args = sys.argv[1:]

def option(name):
    return args[args.index(name) + 1]

def release_dir(tag):
    return root / "releases" / tag

if args[:2] == ["repo", "clone"]:
    subprocess.run(
        ["git", "clone", os.environ["VARIMU_FAKE_GIT_REMOTE"], args[3]],
        check=True,
    )
elif args[:2] == ["release", "view"]:
    tag = args[2]
    directory = release_dir(tag)
    metadata = directory / "metadata.json"
    if not metadata.is_file():
        print("release not found", file=sys.stderr)
        raise SystemExit(1)
    data = json.loads(metadata.read_text())
    assets = []
    for path in sorted((directory / "assets").glob("*")):
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        assets.append({
            "name": path.name,
            "size": path.stat().st_size,
            "digest": "sha256:" + digest,
            "url": "https://example.invalid/" + path.name,
        })
    data["assets"] = assets
    print(json.dumps(data))
elif args[:2] == ["release", "create"]:
    tag = args[2]
    directory = release_dir(tag)
    if directory.exists():
        print("already exists", file=sys.stderr)
        raise SystemExit(1)
    (directory / "assets").mkdir(parents=True)
    repo = option("--repo")
    data = {
        "tagName": tag,
        "url": f"https://github.com/{repo}/releases/tag/{tag}",
        "name": option("--title"),
        "body": option("--notes"),
        "isDraft": False,
        "isPrerelease": False,
    }
    (directory / "metadata.json").write_text(json.dumps(data))
    print(data["url"])
elif args[:2] == ["release", "upload"]:
    tag = args[2]
    source = Path(args[3])
    target = release_dir(tag) / "assets" / source.name
    if target.exists():
        print("asset already exists", file=sys.stderr)
        raise SystemExit(1)
    shutil.copy2(source, target)
elif args[:2] == ["release", "download"]:
    tag = args[2]
    source = release_dir(tag) / "assets" / option("--pattern")
    if not source.is_file():
        print("asset not found", file=sys.stderr)
        raise SystemExit(1)
    destination = Path(option("--dir")) / source.name
    shutil.copy2(source, destination)
else:
    print("unsupported fake gh command: " + repr(args), file=sys.stderr)
    raise SystemExit(2)
'''


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="varimu-release-test-") as temporary:
        root = Path(temporary)
        fake_root = root / "remote"
        fake_gh = root / "gh"
        fake_gh.write_text(FAKE_GH, encoding="utf-8")
        fake_gh.chmod(fake_gh.stat().st_mode | stat.S_IXUSR)
        os.environ["VARIMU_FAKE_GH_ROOT"] = str(fake_root)

        seed = root / "seed"
        bare = root / "repo.git"
        subprocess.run(
            ["git", "init", "-b", "main", str(seed)],
            check=True, stdout=subprocess.DEVNULL,
        )
        subprocess.run(
            ["git", "-C", str(seed), "config", "user.name", "Test"], check=True
        )
        subprocess.run(
            ["git", "-C", str(seed), "config", "user.email", "test@example.invalid"],
            check=True,
        )
        (seed / "README.md").write_text("test\n", encoding="utf-8")
        subprocess.run(
            ["git", "-C", str(seed), "add", "README.md"], check=True
        )
        subprocess.run(
            ["git", "-C", str(seed), "commit", "-m", "initial"],
            check=True, stdout=subprocess.DEVNULL,
        )
        subprocess.run(
            ["git", "clone", "--bare", str(seed), str(bare)],
            check=True, stdout=subprocess.DEVNULL,
        )
        os.environ["VARIMU_FAKE_GIT_REMOTE"] = str(bare)

        package = root / "package-manifest-v1.json"
        package.write_text('{"kind":"test-package"}\n', encoding="utf-8")
        part = root / "varimu-completed-run-test.tar.zst.part-0001"
        part.write_bytes(b"verified package bytes")
        parts = [{
            "name": part.name,
            "path": str(part),
            "size": part.stat().st_size,
            "sha256": publisher.sha256_file(part),
        }]
        arguments = {
            "gh_path": str(fake_gh),
            "repo_name": "owner/repo",
            "batch_id": "batch-test",
            "training_run_id": "run-test",
            "parts": parts,
            "package_manifest": package,
        }
        first = publisher.publish_or_recover_release(**arguments)
        second = publisher.publish_or_recover_release(**arguments)
        if first["url"] != second["url"] or first["tag"] != second["tag"]:
            raise RuntimeError("Release recovery changed immutable identity")

        remote_part = (
            fake_root / "releases" / first["tag"] / "assets" / part.name
        )
        remote_part.write_bytes(b"tampered")
        try:
            publisher.publish_or_recover_release(**arguments)
        except publisher.PublishError:
            tamper_rejected = True
        else:
            tamper_rejected = False
        if not tamper_rejected:
            raise RuntimeError("tampered Release asset was accepted")

        metadata_root = root / "metadata"
        metadata_root.mkdir()
        metadata_files = {}
        for name in (
            "completed-run.json", "completed-run-v1.json", "ANNOTATION.md",
            "package-manifest-v1.json", "training-ledger-receipt.json",
        ):
            path = metadata_root / name
            path.write_text(f"lightweight {name}\n", encoding="utf-8")
            metadata_files[name] = path
        publisher.publish_code_folder(
            gh_path=str(fake_gh),
            repo_name="owner/repo",
            branch="main",
            completion_index_root="varimu-training/release-index",
            batch_id="batch-test",
            training_run_id="run-test",
            metadata_files=metadata_files,
        )
        checkout = root / "verify"
        subprocess.run(
            ["git", "clone", str(bare), str(checkout)],
            check=True, stdout=subprocess.DEVNULL,
        )
        index = checkout / "varimu-training/release-index/batch-test/run-test"
        published_names = sorted(path.name for path in index.iterdir())
        if published_names != sorted(metadata_files):
            raise RuntimeError(f"Code index is not lightweight-only: {published_names}")

        print(json.dumps({
            "status": "PASS",
            "create_only_release": True,
            "idempotent_recovery": True,
            "tampered_asset_rejected": True,
            "lightweight_code_index_only": True,
            "local_sources_retained": package.is_file() and part.is_file(),
        }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
