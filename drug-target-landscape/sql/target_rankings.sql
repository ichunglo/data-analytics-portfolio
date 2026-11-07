-- Count distinct source records; approval is a drug-level source claim.
WITH eligible AS (
  SELECT * FROM drug_target_landscape
  WHERE :scope = 'broad'
     OR default_developed_count_eligible = 1
     OR approval_reported = 1
)
SELECT target_id, target_name, gene_symbol, target_category,
       COUNT(DISTINCT drug_id) AS linked_drugs,
       COUNT(DISTINCT CASE WHEN approval_reported = 1 THEN drug_id END) AS reported_approved
FROM eligible
GROUP BY target_id, target_name, gene_symbol, target_category
ORDER BY linked_drugs DESC, COALESCE(NULLIF(gene_symbol,''), target_name), target_id;
