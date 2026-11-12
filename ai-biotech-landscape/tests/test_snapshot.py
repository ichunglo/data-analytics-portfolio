import csv
import json
import subprocess
import unittest
from pathlib import Path
from urllib.parse import urlparse

PROJECT = Path(__file__).resolve().parents[1]
DATA = PROJECT / 'dashboard'
SCRIPTS = ['landscape-data.js', 'landscape-expansion.js', 'landscape-expansion-2.js',
           'landscape-expansion-3.js', 'landscape-dossiers.js', 'landscape-expansion-4.js',
           'ownership-disclosures.js', 'landscape-expansion-5.js', 'asset-audit.js',
           'trial-audit.js', 'asset-registry-links.js', 'asset-rights-review.js']


def rows(filename):
    with (DATA / filename).open(encoding='utf-8-sig', newline='') as handle:
        return list(csv.DictReader(handle))


class SnapshotTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        script = "global.window={};for(const f of JSON.parse(process.argv[1]))require(require('path').join(process.argv[2],f));console.log(JSON.stringify({companies:window.landscapeCompanies,assets:window.assetAudit,trials:window.clinicalTrialAudit,groups:window.applicationGroups}))"
        completed = subprocess.run(['node', '-e', script, json.dumps(SCRIPTS), str(DATA)],
                                   check=True, capture_output=True, text=True, encoding='utf-8')
        cls.snapshot = json.loads(completed.stdout)

    def test_company_coverage_and_dossiers(self):
        companies = self.snapshot['companies']
        names = [c['name'] for c in companies]
        self.assertEqual(len(names), 55)
        self.assertEqual(len(set(names)), len(names))
        for filename in ('company-audit.csv', 'ownership-audit.csv', 'pipeline-coverage.csv', 'sponsor-search-audit.csv'):
            entries = rows(filename)
            self.assertEqual(len(entries), len(names), filename)
            self.assertEqual({r['company'] for r in entries}, set(names), filename)
        company_rows = {r['company']: r for r in rows('company-audit.csv')}
        ownership_rows = {r['company']: r for r in rows('ownership-audit.csv')}
        coverage_rows = {r['company']: r for r in rows('pipeline-coverage.csv')}
        for company in companies:
            name = company['name']
            self.assertEqual(company_rows[name]['disclosed_portfolio'], company['dossier']['portfolio'])
            self.assertEqual(company_rows[name]['rights_and_collaborations'], company['dossier']['rights'])
            self.assertEqual(ownership_rows[name]['investor_evidence'], company['ownershipDisclosure']['note'])
            self.assertEqual(coverage_rows[name]['portfolio_summary'], company['dossier']['portfolio'])
            self.assertTrue(company['dossier']['url'], company['name'])
            self.assertTrue(company['dossier']['rightsUrl'], company['name'])
            self.assertTrue(company['ownershipDisclosure']['url'], company['name'])
            self.assertTrue(company['applicationEvidence'], company['name'])

    def test_asset_csv_matches_browser_snapshot(self):
        assets = self.snapshot['assets']
        csv_assets = rows('asset-audit.csv')
        self.assertEqual(len(assets), 81)
        self.assertEqual(len(csv_assets), len(assets))
        fields = ('company', 'asset', 'indication', 'stage', 'rights', 'rights_source', 'source_date', 'source')
        self.assertEqual([{k: a[k] for k in fields} for a in assets], csv_assets)
        company_names = {c['name'] for c in self.snapshot['companies']}
        for asset in assets:
            self.assertIn(asset['company'], company_names)
            self.assertEqual(urlparse(asset['source']).scheme, 'https')
            self.assertEqual(urlparse(asset['rights_source']).scheme, 'https')

    def test_trial_snapshot_has_unique_studies_and_known_company(self):
        trial_csv = rows('trial-audit.csv')
        studies = self.snapshot['trials']
        self.assertEqual(len(studies), 90)
        self.assertEqual(len(trial_csv), len(studies))
        self.assertEqual({x['study_id'] for x in studies}, {x['study_id'] for x in trial_csv})
        self.assertEqual(len({x['study_id'] for x in studies}), len(studies))
        company_names = {c['name'] for c in self.snapshot['companies']}
        for study in studies:
            self.assertIn(study['company_or_affiliate'], company_names)
            self.assertEqual(study['source'], 'https://clinicaltrials.gov/study/' + study['study_id'])

    def test_application_labels_and_audit_links(self):
        labels = {item[0] for group in self.snapshot['groups'] for item in group['items']}
        for company in self.snapshot['companies']:
            for label, url in company['applicationEvidence']:
                self.assertIn(label, labels, company['name'])
                self.assertEqual(urlparse(url).scheme, 'https', company['name'])
        html_source = (DATA / 'index.qmd').read_text(encoding='utf-8-sig')
        for filename in ('company-audit.csv', 'ownership-audit.csv', 'pipeline-coverage.csv', 'asset-audit.csv', 'trial-audit.csv', 'sponsor-search-audit.csv'):
            self.assertIn(filename, html_source)


if __name__ == '__main__':
    unittest.main()
