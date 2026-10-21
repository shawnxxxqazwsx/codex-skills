"""Regression checks for public export boundaries; no source skills are edited."""
from pathlib import Path
import tempfile
import unittest

from sync_skills import export_bytes, public_text, source_roots


class ExportBoundaryTests(unittest.TestCase):
    def export(self, name, data, key):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / name
            path.write_bytes(data)
            return export_bytes(path, key)

    def test_known_private_reference_is_redacted(self):
        self.assertEqual(public_text('/Users/example/Documents/Codex/2026-09-26/w/outputs/crypto-research/decade-study/REPORT.md'),
                         '<CRYPTO_RESEARCH_OUTPUT>/decade-study/REPORT.md')

    def test_unknown_home_path_is_rejected(self):
        with self.assertRaises(ValueError):
            public_text('/Users/example/private/report.md')

    def test_extra_project_scopes_are_explicit_and_unique(self):
        roots = source_roots(Path('/personal'), Path('/mc'), ['pigora-eq=/pigora'])
        self.assertEqual(roots[-1], (Path('/pigora/.agents/skills'), 'projects/pigora-eq/skills'))
        for spec in ['../private=/tmp', 'mc-patcher=/other', 'missing-path=', 'no-separator']:
            with self.subTest(spec=spec), self.assertRaises(ValueError):
                source_roots(Path('/personal'), Path('/mc'), [spec])

    def test_credentials_are_rejected(self):
        with self.assertRaises(ValueError):
            public_text('ghp_' + 'x' * 40)

    def test_media_bytes_are_preserved(self):
        data = b'\x89PNG\r\n\x1a\n' + bytes(range(256))
        self.assertEqual(self.export('preview.png', data,
                                    'personal/skills/threejs/assets/preview.png'), data)

    def test_media_outside_reviewed_scope_is_rejected(self):
        with self.assertRaises(ValueError):
            self.export('preview.png', b'\x89PNG\r\n\x1a\n',
                        'personal/skills/other/assets/preview.png')

    def test_invalid_media_signature_is_rejected(self):
        with self.assertRaises(ValueError):
            self.export('preview.png', b'plain text',
                        'personal/skills/threejs/assets/preview.png')

    def test_embedded_private_path_is_rejected(self):
        with self.assertRaises(ValueError):
            self.export('preview.png', b'\x89PNG\r\n\x1a\n/Users/example/private/file',
                        'personal/skills/threejs/assets/preview.png')


if __name__ == '__main__':
    unittest.main()
