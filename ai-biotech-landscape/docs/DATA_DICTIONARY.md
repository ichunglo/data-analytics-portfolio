# Dataset guide

All files are UTF-8 CSV with a header. They are kept beside the browser data in `dashboard/` so they are also available as downloads in the rendered dashboard.

| File | Unit | Key fields |
|---|---|---|
| `company-audit.csv` | Company | `company`, `region`, `location`, `business_model`, `corporate_status`, `disclosed_portfolio`, `rights_and_collaborations`, linked sources, `audit_as_of` |
| `ownership-audit.csv` | Company | `listing_and_control`, dated `investor_evidence`, `source`, `evidence_status`, `review_date` |
| `pipeline-coverage.csv` | Company | `portfolio_summary`, source, number and names of selected asset records, rights summary and source |
| `asset-audit.csv` | Asset–indication or asset record | `company`, `asset`, `indication`, `stage`, `rights`, separate stage and rights source links, `source_date` |
| `trial-audit.csv` | Registry study | `company_or_affiliate`, `asset`, `study_id`, registry phase and status, last posted, lead sponsor, title, source, retrieval date |
| `sponsor-search-audit.csv` | Company search | sponsor query, broad-hit and matching lead-sponsor counts, interpretation note, retrieval date |

Company records are also stored in `landscape-data.js` and ordered expansion and dossier scripts; `asset-audit.js`, `trial-audit.js`, `asset-registry-links.js` and `asset-rights-review.js` are used by the browser and build script. Some company names in the trial CSV denote affiliates or retain alternate spellings; the browser snapshot explicitly maps those labels to the current company profile. Dates can denote publication, registry update, source review or retrieval as named by the field; they should not be interpreted interchangeably.

An asset may be repeated for distinct indications; trial records are uniquely keyed by ClinicalTrials.gov NCT identifier in this snapshot. `pipeline-coverage.csv` counts selected asset rows, not unique molecules or the full portfolio. `Not established` describes the reviewed evidence, not necessarily the underlying fact.
