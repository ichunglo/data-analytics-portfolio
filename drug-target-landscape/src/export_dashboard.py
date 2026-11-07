"""Publish a small, clearly scoped aggregate from an analysis run."""
import argparse
import csv
import json
from pathlib import Path


def export(ranking_path, manifest_path, output_path):
    manifest = json.loads(manifest_path.read_text(encoding='utf8'))
    if manifest['scope'] != 'clinical':
        raise ValueError('Dashboard requires the clinical analysis view')
    with ranking_path.open(encoding='utf8', newline='') as source:
        rows = list(csv.DictReader(source))
    targets = []
    for row in rows[:50]:
        targets.append({key: int(row[key]) if key in ('linked_drugs', 'reported_approved') else row[key]
                        for key in ('target_id', 'target_name', 'gene_symbol', 'target_category',
                                    'linked_drugs', 'reported_approved')})
    data = {'manifest': manifest, 'targets': targets}
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text('window.LANDSCAPE_DATA = ' + json.dumps(data, ensure_ascii=True, indent=2) + ';\n', encoding='utf8')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ranking', type=Path, required=True)
    parser.add_argument('--manifest', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    export(args.ranking, args.manifest, args.out)
