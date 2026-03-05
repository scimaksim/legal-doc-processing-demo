-- Step 1: Create the extracted legal fields table using ai_query
-- This extracts structured key information from each parsed legal document

CREATE OR REPLACE TABLE classic_stable_tetifz_catalog.legal_docs.extracted_fields AS
WITH doc_text AS (
  -- Concatenate all text elements per document into a single text block
  SELECT
    file_name,
    concat_ws('\n\n', collect_list(
      CASE WHEN element_type = 'title' THEN concat('# ', content)
           WHEN element_type = 'section_header' THEN concat('## ', content)
           ELSE content
      END
    )) as full_text
  FROM classic_stable_tetifz_catalog.legal_docs.document_elements
  GROUP BY file_name
)
SELECT
  file_name,
  ai_query(
    'databricks-claude-sonnet-4-6',
    concat(
      'You are a legal document analyst. Extract key information from the following legal document. ',
      'Return a JSON object with ONLY these fields (use null if not found):\n',
      '- document_type: the type of legal document (e.g., "NDA", "Software License", "Employment Agreement", "Commercial Lease", "Merger Agreement")\n',
      '- parties: array of party names involved\n',
      '- effective_date: the effective or execution date\n',
      '- termination_date: when the agreement expires or can be terminated\n',
      '- governing_law: the state/jurisdiction governing the agreement\n',
      '- key_dollar_amounts: array of objects with {description, amount} for any monetary values mentioned\n',
      '- confidentiality_period: duration of any confidentiality obligations\n',
      '- termination_notice_period: required notice period for termination\n',
      '- non_compete_duration: duration of any non-compete clause\n',
      '- key_obligations: array of the top 3-5 most important obligations or terms\n',
      '- risk_flags: array of any unusual or potentially risky clauses\n\n',
      'Document:\n', full_text
    ),
    responseFormat => 'STRUCT<extraction:STRUCT<document_type:STRING, parties:ARRAY<STRING>, effective_date:STRING, termination_date:STRING, governing_law:STRING, key_dollar_amounts:ARRAY<STRUCT<description:STRING, amount:STRING>>, confidentiality_period:STRING, termination_notice_period:STRING, non_compete_duration:STRING, key_obligations:ARRAY<STRING>, risk_flags:ARRAY<STRING>>>'
  ) as extracted_json
FROM doc_text
