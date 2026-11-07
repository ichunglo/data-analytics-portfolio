# Data dictionary

| Field | Meaning | Interpretation |
|---|---|---|
| `drug_id` | Canonical record identifier in the integrated snapshot | Some generic product names remain unresolved. |
| `target_id` | Canonical target record identifier | Can represent a protein, family, complex, RNA grouping, or non-protein target. |
| `gene_symbol`, `target_name` | Display identifiers for the target | Some source names or accessions need review. |
| `target_category` | Source-derived target class | `Unclear` is retained. |
| `drug_category` | Source-derived modality | `Small molecule`, `Biologic`, `Other`, or `Unknown`. |
| `approval_reported` | A source reports drug-level approval | Not necessarily FDA approval or approval mediated by every linked target. |
| `default_developed_count_eligible` | Relationship satisfies the database's phase/approval and combination rule | The project also includes links involving an approved drug. |
| `source_detail` | Source evidence metadata, sometimes JSON | May include `candidate_study_date_proxy`; it is not verified first entry. |

The script uses the view and evidence table read-only. For an independently runnable example with these fields, see [the synthetic data generator](../examples/create_demo.py).
