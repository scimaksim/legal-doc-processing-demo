# Databricks notebook source
# MAGIC %md
# MAGIC # Step 5: Extract Key Legal Information with ai_query
# MAGIC Uses Foundation Models to extract structured fields from each document.

# COMMAND ----------

try:
    catalog = spark.conf.get("spark.databricks.bundle.variables.catalog")
except Exception:
    catalog = "classic_stable_tetifz_catalog"
try:
    schema = spark.conf.get("spark.databricks.bundle.variables.schema")
except Exception:
    schema = "legal_docs"

# COMMAND ----------

spark.sql(f"""
CREATE OR REPLACE TABLE {catalog}.{schema}.extracted_fields AS
WITH doc_text AS (
  SELECT
    file_name,
    concat_ws('\n\n', collect_list(
      CASE WHEN element_type = 'title' THEN concat('# ', content)
           WHEN element_type = 'section_header' THEN concat('## ', content)
           ELSE content
      END
    )) as full_text
  FROM {catalog}.{schema}.document_elements
  GROUP BY file_name
)
SELECT
  file_name,
  ai_query(
    'databricks-claude-sonnet-4-6',
    concat(
      'You are a legal document analyst. Extract key information from the following legal document. ',
      'Return a JSON object with these fields (use null if not found): ',
      'document_type, parties (array), effective_date, termination_date, governing_law, ',
      'key_dollar_amounts (array of objects with description and amount), ',
      'confidentiality_period, termination_notice_period, non_compete_duration, ',
      'key_obligations (array of top 3-5 terms), risk_flags (array of risky clauses). ',
      'Document:\\n', full_text
    ),
    responseFormat => 'STRUCT<extraction:STRUCT<document_type:STRING, parties:ARRAY<STRING>, effective_date:STRING, termination_date:STRING, governing_law:STRING, key_dollar_amounts:ARRAY<STRUCT<description:STRING, amount:STRING>>, confidentiality_period:STRING, termination_notice_period:STRING, non_compete_duration:STRING, key_obligations:ARRAY<STRING>, risk_flags:ARRAY<STRING>>>'
  ) as extracted_json
FROM doc_text
""")

# COMMAND ----------

spark.sql(f"""
CREATE OR REPLACE TABLE {catalog}.{schema}.extracted_key_info AS
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
FROM {catalog}.{schema}.extracted_fields
""")

# COMMAND ----------

count = spark.sql(f"SELECT count(*) as cnt FROM {catalog}.{schema}.extracted_key_info").first()["cnt"]
print(f"Extracted key information from {count} documents")

# Show sample
display(spark.sql(f"""
SELECT file_name, document_type, parties, governing_law
FROM {catalog}.{schema}.extracted_key_info
ORDER BY file_name
LIMIT 10
"""))
