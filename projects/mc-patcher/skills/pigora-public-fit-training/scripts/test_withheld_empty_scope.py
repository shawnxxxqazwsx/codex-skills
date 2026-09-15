"""An inference exclusion is not automatically a public withheld decision."""

import contextlib
import csv
import io
import json
import tempfile
import unittest
from pathlib import Path

import validate_withheld_points as gate


class EmptyPolicyTests(unittest.TestCase):
    def test_empty_policy_accepts_only_empty_withheld_ledger(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            catalog = root / 'catalog.jsonl'
            policy = root / 'policy.csv'
            ledger = root / 'withheld.csv'
            catalog.write_text(json.dumps(dict(module_type=1, model_name='Example',
                point_kind='bell', selector=0, fixed_frequency_hz=1000,
                claim_status='source-constrained')) + '\n')
            fields = sorted(gate.EVIDENCE_REQUIRED | {'evidence_policy_decision'})
            with policy.open('w', newline='') as stream:
                writer = csv.DictWriter(stream, fieldnames=fields)
                writer.writeheader()
                writer.writerow(dict(identity_key='1:bell:0',
                    public_fit_state='not publicly specified',
                    evidence_policy_decision='not publicly specified',
                    evidence_policy_reason='No eligible public rows',
                    source_claim_id='none'))
            with ledger.open('w', newline='') as stream:
                writer = csv.DictWriter(stream, fieldnames=gate.LEDGER_COLUMNS)
                writer.writeheader()
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(gate.validate(catalog, policy, ledger), 0)
            with ledger.open('a', newline='') as stream:
                writer = csv.DictWriter(stream, fieldnames=gate.LEDGER_COLUMNS)
                row = {key: 'not-empty' for key in gate.LEDGER_COLUMNS}
                row['identity_key'] = '1:bell:0'
                writer.writerow(row)
            with self.assertRaisesRegex(gate.ValidationError, 'not evidence-policy withheld'):
                gate.validate(catalog, policy, ledger)

    def test_withheld_policy_still_requires_its_row(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            catalog = root / 'catalog.jsonl'
            policy = root / 'policy.csv'
            ledger = root / 'withheld.csv'
            catalog.write_text(json.dumps(dict(module_type=1, model_name='Example',
                point_kind='bell', selector=0, fixed_frequency_hz=1000,
                claim_status='source-constrained')) + '\n')
            with policy.open('w', newline='') as stream:
                fields = sorted(gate.EVIDENCE_REQUIRED | {'evidence_policy_decision'})
                writer = csv.DictWriter(stream, fieldnames=fields)
                writer.writeheader()
                writer.writerow(dict(identity_key='1:bell:0',
                    public_fit_state='public-fit failed/withheld',
                    evidence_policy_decision='withheld',
                    evidence_policy_reason='Frozen response gate failed',
                    source_claim_id='example'))
            with ledger.open('w', newline='') as stream:
                csv.writer(stream).writerow(gate.LEDGER_COLUMNS)
            with self.assertRaisesRegex(gate.ValidationError, 'omits 1'):
                gate.validate(catalog, policy, ledger)


if __name__ == '__main__':
    unittest.main()
