#!/usr/bin/env python3
"""Export user-maintained skills to this repository; preview unless --write."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
EXTENSIONS = {'.md', '.py', '.yaml', '.yml', '.json', '.txt',
              '.html', '.js', '.mjs', '.sh'}
MEDIA_SCOPES = {
    'personal/skills/lieflat-charts': ('docs/assets/',),
    'personal/skills/motion-web': ('assets/', 'cases/toy-flipbook/img/'),
    'personal/skills/threejs': ('assets/',),
}


def export_bytes(path, key):
    """Allow reviewed bundled media only; keep binary bytes unchanged."""
    data = path.read_bytes()
    if len(data) > 50 * 1024 * 1024:
        raise ValueError(f'Oversized skill resource: {key}')
    if path.suffix in EXTENSIONS or path.name == 'LICENSE':
        return public_text(data.decode('utf-8').replace('\r\n', '\n').replace('\r', '\n')).encode('utf-8')
    parts = key.split('/', 3)
    scope, rel = '/'.join(parts[:3]), parts[3]
    if not any(rel.startswith(prefix) for prefix in MEDIA_SCOPES.get(scope, ())):
        raise ValueError(f'Unreviewed file type or media scope: {key}')
    signatures = {
        '.png': data.startswith(b'\x89PNG\r\n\x1a\n'),
        '.jpg': data.startswith(b'\xff\xd8\xff'),
        '.gif': data.startswith((b'GIF87a', b'GIF89a')),
        '.webp': data[:4] == b'RIFF' and data[8:12] == b'WEBP',
        '.mp4': data[4:8] == b'ftyp',
    }
    if not signatures.get(path.suffix, False):
        raise ValueError(f'Invalid or unreviewed media format: {key}')
    # Scan embedded text/metadata without transforming binary content.
    embedded = data.decode('latin-1')
    if public_text(embedded) != embedded:
        raise ValueError(f'Private path in media metadata: {key}')
    return data


def public_text(text):
    # Public copies must not reveal a workstation username or source library.
    text = re.sub(r'/Users/[^/\n]+/Desktop/CREATING/My Works/MIXING & MASTERING/',
                  '<PROGRAM_STEMS_SOURCE>/', text)
    text = re.sub(r'/Users/[^/\n]+/Desktop/CREATING/Reaper/Mixing/',
                  '<PROGRAM_MIX_SOURCE>/', text)
    text = re.sub(r'/Users/[^/\n]+/Documents/Codex/2026-09-26/w/outputs/crypto-research/',
                  '<CRYPTO_RESEARCH_OUTPUT>/', text)
    if re.search(r'/Users/[^/\s]+/|/home/[^/\s]+/', text):
        raise ValueError('Unreviewed personal home path: configure a public replacement first')
    patterns = [r'gh[pousr]_[A-Za-z0-9]{30,}', r'github_pat_[A-Za-z0-9_]{30,}',
                r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',
                r'AKIA[0-9A-Z]{16}', r'sk-(?:proj-)?[A-Za-z0-9_-]{32,}']
    if any(re.search(pattern, text) for pattern in patterns):
        raise ValueError('Potential credential in source; refusing export')
    return text


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--personal-root', type=Path, required=True)
    parser.add_argument('--project-root', type=Path, required=True,
                        help='mc-patcher checkout containing .agents/skills')
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    sources = [(args.personal_root, 'personal/skills'),
               (args.project_root / '.agents/skills', 'projects/mc-patcher/skills')]
    exports = {}
    modes = {}
    skills = []
    for source, prefix in sources:
        if not source.is_dir() or source.is_symlink():
            raise ValueError(f'Invalid source directory: {source}')
        for skill in sorted(source.iterdir()):
            if skill.name.startswith('.') or not skill.is_dir():
                continue
            if skill.is_symlink():
                raise ValueError(f'Symlink skill directory: {skill.name}')
            if not (skill / 'SKILL.md').is_file():
                continue
            skills.append(f'{prefix}/{skill.name}')
            for path in sorted(skill.rglob('*')):
                rel = path.relative_to(skill)
                if any(p.startswith('.') or p == '__pycache__' for p in rel.parts):
                    continue
                if path.is_symlink():
                    raise ValueError(f'Symlink in skill: {skill.name}/{rel}')
                if not path.is_file():
                    continue
                key = f'{prefix}/{skill.name}/{rel.as_posix()}'
                try:
                    exports[key] = export_bytes(path, key)
                except ValueError as error:
                    raise ValueError(f'{key}: {error}') from error
                modes[key] = 0o755 if path.stat().st_mode & 0o111 else 0o644
    if not exports:
        raise ValueError('No skill files found')
    manifest = {'schema_version': 1, 'skills': skills,
                'files': {key: hashlib.sha256(value).hexdigest()
                          for key, value in sorted(exports.items())}}
    existing = ROOT / 'sync-manifest.json'
    old = json.loads(existing.read_text()).get('files', {}) if existing.exists() else {}
    stale = sorted(set(old) - set(exports))
    # Never remove a file based on an unchecked manifest path.
    for key in stale:
        parts = Path(key).parts
        if '..' in parts or Path(key).is_absolute() or not any(
                key.startswith(prefix + '/') for _, prefix in sources):
            raise ValueError('Unsafe stale manifest entry')
    # Refuse redirected destinations before making any changes.
    for key in set(exports) | set(stale):
        destination = ROOT / key
        if any(p.is_symlink() for p in [destination, *destination.parents] if p != ROOT.parent):
            raise ValueError('Symlink destination')
    changed = [key for key, data in exports.items()
               if not (ROOT / key).exists() or (ROOT / key).read_bytes() != data]
    print(json.dumps({'skills': len(skills), 'files': len(exports),
                      'changed': len(changed), 'stale': stale, 'write': args.write}))
    if not args.write:
        return
    for key in changed:
        path = ROOT / key
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(exports[key])
    for key, mode in modes.items():
        os.chmod(ROOT / key, mode)
    for key in stale:
        (ROOT / key).unlink(missing_ok=True)
    existing.write_text(json.dumps(manifest, indent=2) + '\n')


if __name__ == '__main__':
    main()
