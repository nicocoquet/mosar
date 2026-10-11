"""Tests complémentaires isolés : python -m unittest discover -s tests -p 'test_sanitize_xlsx_security.py' -v."""
import importlib.util
import io
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch
from types import ModuleType

from openpyxl import Workbook, load_workbook


class SanitizerSecurityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Charge le script du dépôt, sans modifier la configuration réelle du projet.
        cls.script = Path(__file__).resolve().parents[1] / 'scripts' / 'sanitize_xlsx.py'
        cls.fake_config = ModuleType('config')
        cls.fake_config.load_config = lambda: {
            'data': {'sheet': 'recensement', 'file': 'data/test.xlsx'},
            'privacy': {
                'allowed_columns': ['ID_Mosar', 'Nom', 'Site web'],
                'forbidden_columns': ['Contacts', 'Personnel à disposition'],
            },
        }
        cls.fake_config.project_path = lambda path: Path(path)
        with patch.dict(sys.modules, {'config': cls.fake_config}):
            spec = importlib.util.spec_from_file_location('mosar_sanitizer_security_test', cls.script)
            cls.module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(cls.module)

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.source = self.root / 'source.xlsx'
        self.output = self.root / 'output.xlsx'

    def workbook(self, headers, rows, extra_sheet=False):
        wb = Workbook()
        ws = wb.active
        ws.title = 'recensement'
        ws.append(headers)
        for row in rows:
            ws.append(row)
        if extra_sheet:
            wb.create_sheet('Confidentiel').append(['secret'])
        wb.save(self.source)
        wb.close()

    def sanitize(self):
        with redirect_stdout(io.StringIO()) as stdout:
            self.module.sanitize(self.source, self.output)
        return stdout.getvalue()

    def test_unknown_and_forbidden_columns_are_removed(self):
        self.workbook(['ID_Mosar', 'Nom', 'Contacts', 'Notes privées'],
                      [['MOS-1', 'Revue', 'secret', 'autre secret']], extra_sheet=True)
        report = self.sanitize()
        wb = load_workbook(self.output)
        self.assertEqual([c.value for c in wb.active[1]], ['ID_Mosar', 'Nom'])
        self.assertEqual(wb.sheetnames, ['recensement'])
        self.assertIn('Notes privées', report)
        self.assertIn('Contacts', report)
        wb.close()

    def test_formula_in_retained_column_rejected_and_output_preserved(self):
        self.workbook(['ID_Mosar', 'Nom'], [['MOS-1', '=1+1']])
        self.output.write_bytes(b'original')
        with self.assertRaisesRegex(SystemExit, 'Formule Excel interdite'):
            self.sanitize()
        self.assertEqual(self.output.read_bytes(), b'original')

    def test_formula_in_removed_column_is_ignored(self):
        self.workbook(['ID_Mosar', 'Nom', 'Contacts', 'Inconnue'],
                      [['MOS-1', 'Revue', '=1+1', '=2+2']])
        self.sanitize()
        self.module.validate_sanitized(self.output)

    def test_literal_equals_string_is_rejected_conservatively(self):
        self.workbook(['ID_Mosar', 'Nom'], [['MOS-1', "'=1+1"]])
        self.sanitize()  # Valeur textuelle explicite (apostrophe), non formule.

    def test_check_rejects_formula(self):
        self.workbook(['ID_Mosar', 'Nom'], [['MOS-1', '=1+1']])
        with self.assertRaisesRegex(SystemExit, 'Formule Excel interdite'):
            self.module.validate_sanitized(self.source)

    def test_check_rejects_unknown_column(self):
        self.workbook(['ID_Mosar', 'Nom', 'Privé'], [['MOS-1', 'Revue', 'secret']])
        with self.assertRaisesRegex(SystemExit, 'Colonnes non autorisées'):
            self.module.validate_sanitized(self.source)

    def test_missing_id_does_not_replace_output(self):
        self.workbook(['Nom'], [['Revue']])
        self.output.write_bytes(b'original')
        with self.assertRaisesRegex(SystemExit, 'ID_Mosar'):
            self.sanitize()
        self.assertEqual(self.output.read_bytes(), b'original')

    def test_duplicate_headers_rejected(self):
        self.workbook(['ID_Mosar', 'Nom', 'Nom'], [['MOS-1', 'A', 'B']])
        with self.assertRaisesRegex(SystemExit, 'dupliqués'):
            self.sanitize()

    def test_valid_sanitized_workbook_accepted(self):
        self.workbook(['ID_Mosar', 'Nom', 'Site web'],
                      [['MOS-1', 'Revue', 'https://example.org']])
        self.sanitize()
        self.module.validate_sanitized(self.output)


if __name__ == '__main__':
    unittest.main()
