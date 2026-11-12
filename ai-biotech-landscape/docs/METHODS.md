# Methods and provenance

## Scope

The selected universe comprises US- or Europe-headquartered AI-native therapeutic developers and specialist computational providers. Large pharmaceutical companies, general-purpose technology vendors, and manufacturing- or commercialization-only providers were excluded. Some companies span multiple locations or modalities. The source material was reviewed through November 11–12, 2026; this is a historical, curated selection, not an exhaustive census.

The application catalog paraphrases and reorganizes Table 3 of Bender et al., [*Artificial intelligence in drug discovery — what it is, where we stand and the path forward*](https://www.nature.com/articles/s41573-026-01496-2), *Nature Reviews Drug Discovery* (2026), doi:10.1038/s41573-026-01496-2. Target identification, virtual screening, oligonucleotide design, repurposing and physics-based simulation were added to suit the project scope. Tags are mapped to specific links, not inferred from marketing language alone; missing tags are not evidence that a capability does not exist. Physics-based modeling is not necessarily AI.

## Collection and curation

Company websites, investor presentations, financial filings, regulatory announcements and selected specialist sources support the company and rights summaries. The study snapshot combines selected known studies and exact normalized lead-sponsor searches across the selected company set using the [ClinicalTrials.gov API v2](https://clinicaltrials.gov/data-api/api). The query and count log is included in `dashboard/sponsor-search-audit.csv`.

Registry records include completed, withdrawn, terminated, recruiting, and selected partner-sponsored studies; some studies are observational or diagnostic. Registry phase, recruitment status, sponsor and last-posted date have different meanings. A sponsor search can miss aliases, affiliates, collaborator-sponsored studies, non-US registries and undisclosed trials. No match does not prove absence. Trial sponsor does not establish who owns the asset.

Corporate status, historical financing participation, beneficial ownership, legal control and asset-level rights are separate fields. Dates in sources matter: a historic stake, grant of options, in-licensing, and a clinical trial's sponsorship are not interchangeable. Unestablished rights and stage details are explicitly retained. Articles and company statements are linked for drill-down; ownership percentages are not necessarily current.

## Processing and reproducibility

The dashboard data are the curated `window.landscapeCompanies` data scripts plus the structured registry and asset snapshots. `node ai-biotech-landscape/scripts/build_audits.js` loads these in order, applies explicit company and asset overrides, regenerates four audit CSVs, and checks company names, assets and studies for missing references. `python -m unittest discover -s ai-biotech-landscape/tests -v` runs offline integrity checks. No API credential is required.

The checked-in study data and sponsor-search log are fixed inputs. The build does not reconstruct source searches, fetch the latest trial registry, establish all agreements, or independently reproduce qualitative review. The publicly displayed outcomes are consequently a dated research snapshot. Raw third-party web pages are not republished here; CSVs contain short curated descriptions, registry titles and direct source links. Third-party rights and reuse terms should be checked for any reuse.

## Interpretation

Asset and clinical-trial rows are not independent company counts or a matched cohort; an asset can appear for multiple indications and a study can include multiple interventions. Clinical trial progress is not proof of efficacy, regulatory approval, or the causal contribution of AI. Findings and claims remain source-specific and are not medical or investment guidance.
