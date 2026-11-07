import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

PROJECT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(PROJECT/'src'),str(PROJECT/'examples')]
from analyze import analyze
from create_demo import create


class AnalysisTest(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.db_path=Path(self.temp.name)/'demo.sqlite';create(self.db_path)
        self.db=sqlite3.connect(self.db_path)

    def tearDown(self):self.db.close();self.temp.cleanup()

    def test_clinical_and_broad_populations(self):
        clinical=analyze(self.db,'clinical');broad=analyze(self.db,'broad')
        a={r['target_id']:r for r in clinical['ranking']}['T1'];b={r['target_id']:r for r in broad['ranking']}['T1']
        self.assertEqual((a['linked_drugs'],a['reported_approved']),(3,2))
        self.assertEqual((b['linked_drugs'],b['reported_approved']),(4,2))
        self.assertEqual(len(clinical['links']),5)

    def test_selected_dates_count_distinct_drugs_per_target_per_year(self):
        data=analyze(self.db,'clinical')
        self.assertEqual(data['annual'][('T1',2016)],{'D1','D2'})
        self.assertEqual(data['annual'][('T1',2017)],{'D1'})
        self.assertEqual(data['annual'][('T2',2020)],{'D5'})
        self.assertEqual(len(data['modalities'][('T1','Biologic')]),1)

    def test_invalid_scope_rejected(self):
        with self.assertRaises(ValueError):analyze(self.db,'unverified')


if __name__=='__main__':unittest.main()
