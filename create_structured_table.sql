CREATE OR REPLACE TABLE classic_stable_tetifz_catalog.legal_docs.extracted_key_info AS
SELECT
  file_name,
  get_json_object(extracted_json, '$.document_type') as document_type,
  get_json_object(extracted_json, '$.parties') as parties,
  get_json_object(extracted_json, '$.effective_date') as effective_date,
  get_json_object(extracted_json, '$.termination_date') as termination_date,
  get_json_object(extracted_json, '$.governing_law') as governing_law,
  get_json_object(extracted_json, '$.key_dollar_amounts') as key_dollar_amounts,
  get_json_object(extracted_json, '$.confidentiality_period') as confidentiality_period,
  get_json_object(extracted_json, '$.termination_notice_period') as termination_notice_period,
  get_json_object(extracted_json, '$.non_compete_duration') as non_compete_duration,
  get_json_object(extracted_json, '$.key_obligations') as key_obligations,
  get_json_object(extracted_json, '$.risk_flags') as risk_flags
FROM classic_stable_tetifz_catalog.legal_docs.extracted_fields
