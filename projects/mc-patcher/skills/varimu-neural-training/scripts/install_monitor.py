#!/usr/bin/env python3
"""Install the 600-second Vari-Mu GitHub training monitor for one machine."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import plistlib
import shutil
import socket
import subprocess
import sys
import uuid

import varimu_training_coordinator as coordinator


LABEL = "com.mcpatcher.varimu-training-monitor"
INTERVAL_SECONDS = 600


class InstallError(RuntimeError):
    pass


def default_paths(system: str) -> tuple[Path, Path]:
    if system == "Darwin":
        base = Path.home() / "Library/Application Support/McPatcherVariMuTraining"
        return base / "config.json", base
    config_home = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    data_home = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local/share"))
    return (
        config_home / "mc-patcher/varimu-training.json",
        data_home / "mc-patcher/varimu-training-workspace",
    )


def safe_machine_id(machine_name: str, prior: dict | None) -> str:
    if prior:
        existing = prior.get("machine_id")
        if isinstance(existing, str) and coordinator.SAFE_ID_RE.fullmatch(existing):
            return existing
    slug = "".join(ch if ch.isalnum() or ch in "._-" else "-" for ch in machine_name)
    slug = slug.strip("-.")[:48] or "machine"
    entropy = f"{machine_name}|{uuid.uuid4()}".encode("utf-8")
    return f"{slug}-{hashlib.sha256(entropy).hexdigest()[:16]}"


def run(command: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        command, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        check=False,
    )
    if check and result.returncode != 0:
        raise InstallError(
            f"command failed ({result.returncode}): {' '.join(command)}\n{result.stderr.strip()}"
        )
    return result


def require_repo_access(gh_path: str, repo: str) -> None:
    run([gh_path, "auth", "status"])
    run([gh_path, "repo", "view", repo, "--json", "nameWithOwner,isPrivate"])


def install_launchd(
    *, config_path: Path, coordinator_path: Path, local_root: Path,
    python_path: Path, write_only: bool, scheduler_dir: Path | None,
) -> Path:
    base = scheduler_dir or (Path.home() / "Library/LaunchAgents")
    plist_path = base / f"{LABEL}.plist"
    plist_path.parent.mkdir(parents=True, exist_ok=True)
    logs = local_root / "logs"
    logs.mkdir(parents=True, exist_ok=True)
    payload = {
        "Label": LABEL,
        "ProgramArguments": [
            str(python_path), str(coordinator_path), "watch-once",
            "--config", str(config_path),
        ],
        "RunAtLoad": True,
        "StartInterval": INTERVAL_SECONDS,
        "ProcessType": "Background",
        "StandardOutPath": str(logs / "monitor.stdout.log"),
        "StandardErrorPath": str(logs / "monitor.stderr.log"),
        "EnvironmentVariables": {
            "PATH": "/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin",
        },
    }
    coordinator.atomic_write(plist_path, plistlib.dumps(payload, sort_keys=True))
    if not write_only:
        domain = f"gui/{os.getuid()}"
        run(["launchctl", "bootout", domain, str(plist_path)], check=False)
        run(["launchctl", "bootstrap", domain, str(plist_path)])
        run(["launchctl", "kickstart", f"{domain}/{LABEL}"])
    return plist_path


def quote_systemd(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def install_systemd(
    *, config_path: Path, coordinator_path: Path, local_root: Path,
    python_path: Path, write_only: bool, scheduler_dir: Path | None,
) -> tuple[Path, Path]:
    user_dir = scheduler_dir or (Path.home() / ".config/systemd/user")
    user_dir.mkdir(parents=True, exist_ok=True)
    service_path = user_dir / f"{LABEL}.service"
    timer_path = user_dir / f"{LABEL}.timer"
    logs = local_root / "logs"
    logs.mkdir(parents=True, exist_ok=True)
    command = " ".join(quote_systemd(str(item)) for item in (
        python_path, coordinator_path, "watch-once", "--config", config_path,
    ))
    service = (
        "[Unit]\n"
        "Description=Vari-Mu GitHub training batch monitor\n\n"
        "[Service]\n"
        "Type=oneshot\n"
        f"ExecStart={command}\n"
        f"StandardOutput=append:{logs / 'monitor.stdout.log'}\n"
        f"StandardError=append:{logs / 'monitor.stderr.log'}\n"
    ).encode("utf-8")
    timer = (
        "[Unit]\n"
        "Description=Run Vari-Mu training monitor every ten minutes\n\n"
        "[Timer]\n"
        "OnBootSec=1min\n"
        "OnUnitActiveSec=10min\n"
        "Persistent=true\n"
        "Unit=com.mcpatcher.varimu-training-monitor.service\n\n"
        "[Install]\n"
        "WantedBy=timers.target\n"
    ).encode("utf-8")
    coordinator.atomic_write(service_path, service)
    coordinator.atomic_write(timer_path, timer)
    if not write_only:
        run(["systemctl", "--user", "daemon-reload"])
        run(["systemctl", "--user", "enable", "--now", timer_path.name])
    return service_path, timer_path


def install(args: argparse.Namespace) -> int:
    system = args.platform or platform.system()
    if system not in {"Darwin", "Linux"}:
        raise InstallError(f"unsupported platform: {system}")
    repo_root = args.repo_root.expanduser().resolve()
    coordinator_path = (
        repo_root / ".agents/skills/varimu-neural-training/scripts/varimu_training_coordinator.py"
    )
    if not coordinator_path.is_file():
        raise InstallError(f"coordinator not found: {coordinator_path}")
    default_config, default_local = default_paths(system)
    config_path = (args.config_path or default_config).expanduser().resolve()
    local_root = (args.local_root or default_local).expanduser().resolve()
    gh_path = args.gh_path or shutil.which("gh")
    if not gh_path:
        raise InstallError("gh is required")
    gh_path = str(Path(gh_path).expanduser().resolve())
    require_repo_access(gh_path, args.repo)

    prior = None
    if config_path.is_file():
        prior = coordinator.load_json_file(config_path)
    machine_name = args.machine_name or socket.gethostname()
    machine_id = args.machine_id or safe_machine_id(machine_name, prior)
    coordinator.safe_id(machine_id, "machine_id")
    config = {
        "schema_version": 1,
        "repo": args.repo,
        "branch": args.branch,
        "control_root": args.control_root,
        "completion_index_root": args.completion_index_root,
        "local_root": str(local_root),
        "machine_name": machine_name,
        "machine_id": machine_id,
        "gh_path": gh_path,
        "poll_interval_seconds": INTERVAL_SECONDS,
    }
    for directory in ("batches", "active", "completed", "logs", "state", "packages"):
        (local_root / directory).mkdir(parents=True, exist_ok=True)
    coordinator.atomic_write_json(config_path, config)
    config_path.chmod(0o600)
    python_path = Path(sys.executable).resolve()

    if system == "Darwin":
        scheduler_files = [str(install_launchd(
            config_path=config_path,
            coordinator_path=coordinator_path,
            local_root=local_root,
            python_path=python_path,
            write_only=args.write_only,
            scheduler_dir=args.scheduler_dir,
        ))]
        scheduler = "launchd"
    else:
        scheduler_files = [str(path) for path in install_systemd(
            config_path=config_path,
            coordinator_path=coordinator_path,
            local_root=local_root,
            python_path=python_path,
            write_only=args.write_only,
            scheduler_dir=args.scheduler_dir,
        )]
        scheduler = "systemd-user-timer"

    result = {
        "status": "INSTALLED" if not args.write_only else "WRITTEN_NOT_LOADED",
        "scheduler": scheduler,
        "interval_seconds": INTERVAL_SECONDS,
        "machine_name": machine_name,
        "machine_id": machine_id,
        "config": str(config_path),
        "local_root": str(local_root),
        "scheduler_files": scheduler_files,
    }
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


def status(args: argparse.Namespace) -> int:
    system = args.platform or platform.system()
    default_config, _ = default_paths(system)
    config_path = (args.config_path or default_config).expanduser().resolve()
    data = coordinator.load_json_file(config_path)
    result = {"config": str(config_path), "configuration": data}
    if system == "Darwin":
        domain = f"gui/{os.getuid()}"
        probe = run(["launchctl", "print", f"{domain}/{LABEL}"], check=False)
        result["scheduler"] = "launchd"
        result["loaded"] = probe.returncode == 0
        result["scheduler_output"] = probe.stdout[-4000:]
    else:
        probe = run(["systemctl", "--user", "status", f"{LABEL}.timer"], check=False)
        result["scheduler"] = "systemd-user-timer"
        result["loaded"] = probe.returncode == 0
        result["scheduler_output"] = probe.stdout[-4000:]
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    create = sub.add_parser("install", help="write config and load the 600-second scheduler")
    create.add_argument("--repo-root", type=Path, required=True)
    create.add_argument("--repo", default="shawnxxxqazwsx/mc-patcher")
    create.add_argument("--branch", default="main")
    create.add_argument("--control-root", default="varimu-training")
    create.add_argument(
        "--completion-index-root", default="varimu-training/release-index"
    )
    create.add_argument("--local-root", type=Path)
    create.add_argument("--config-path", type=Path)
    create.add_argument("--gh-path")
    create.add_argument("--machine-name")
    create.add_argument("--machine-id")
    create.add_argument("--scheduler-dir", type=Path, help=argparse.SUPPRESS)
    create.add_argument("--platform", choices=("Darwin", "Linux"), help=argparse.SUPPRESS)
    create.add_argument("--write-only", action="store_true")
    create.set_defaults(func=install)
    inspect = sub.add_parser("status", help="show installed monitor status")
    inspect.add_argument("--config-path", type=Path)
    inspect.add_argument("--platform", choices=("Darwin", "Linux"), help=argparse.SUPPRESS)
    inspect.set_defaults(func=status)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        return args.func(args)
    except (InstallError, coordinator.CoordinationError, OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
