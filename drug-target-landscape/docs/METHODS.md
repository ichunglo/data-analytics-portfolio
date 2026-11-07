# Methods and reproducibility

## Snapshot and unit of analysis

The input is the local `unified-historical-v6/unified-drug-targets.sqlite` snapshot, audited on 6 November 2026. TTD's target and drug source files are 2024 snapshots; the mapping workbook version was not stated. The database also incorporates a paper-derived catalog and later source annotations. A source record is not necessarily a unique chemical entity; 43 same-name groups remain separate.

The `drug_target_landscape` view has one retained row per drug–target pair. Analyses count **distinct drug IDs per target**. A drug may appear under multiple targets. Target groupings can combine mutant, RNA, and protein forms; the original source forms remain in the underlying database. Grouping does not prove a drug binds all forms.

## Evidence views

- `clinical` (default): Include a relationship when `default_developed_count_eligible=1` **or** the linked drug has `approval_reported=1`. The original eligibility rule can suppress a combination when a qualifying mapped component is counted against the same target. The drug-level approval clause also includes some links with no phase reported for that specific association.
- `broad`: Include all retained relationships. These can include investigative records without a trial phase, research chemicals and radiolabeled ligands. Do not call this a clinical-trial cohort.

An approval count includes source-reported approvals that may be outside the U.S. It does not mean each target was validated as the mechanism of the approved indication. No recorded approval does not establish that none exists.

## Study-date heatmap

For eligible pairs, parse the source-linked `candidate_study_date_proxy` in relationship evidence, select 2015–2024, and count distinct drug IDs per target and year. A drug may appear in several years. These study links can be name-matched candidates; a date is not necessarily first clinical entry. Coverage is incomplete, so empty cells do not mean no studies occurred.

## Reproduce

The committed figures were produced with `src/analyze.py` from the input hash in [analysis-manifest.json](../results/analysis-manifest.json). The program opens the database read-only, checks SQLite integrity, queries with [SQL](../sql/target_rankings.sql), and saves a full local ranking, a manifest, and PNG/SVG figures. The complete input SQLite and upstream source snapshots are not bundled, so independent reproduction of the real figures requires access to that same audited snapshot. The fictional example and tests run without it.

```bash
python drug-target-landscape/src/analyze.py --db /path/to/unified-drug-targets.sqlite --out analysis-output/actual --scope clinical
```

The analysis does not produce clinical success probabilities: the sources are not a matched cohort, approval coverage is incomplete, and follow-up time differs.
