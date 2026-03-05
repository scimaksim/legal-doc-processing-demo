# Databricks notebook source
# MAGIC %md
# MAGIC # Step 7: Specialized Extraction Pipelines
# MAGIC Runs targeted ai_query extraction for subpoenas, invoices, and regulatory filings.

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

# MAGIC %md
# MAGIC ## 7a: Parse new documents (incremental)

# COMMAND ----------

spark.sql(f"""
CREATE OR REPLACE TABLE {catalog}.{schema}.parsed_documents AS
SELECT path, ai_parse_document(content, map('version', '2.0',
    'imageOutputPath', '/Volumes/{catalog}/{schema}/parsed_images/')) as parsed
FROM READ_FILES('/Volumes/{catalog}/{schema}/raw_documents/', format => 'binaryFile')
""")

# COMMAND ----------

spark.sql(f"""
CREATE OR REPLACE TABLE {catalog}.{schema}.document_elements AS
SELECT
  replace(path, 'dbfs:/Volumes/{catalog}/{schema}/raw_documents/', '') as file_name,
  parsed:metadata:id::STRING as doc_id,
  elem.id::INT as element_id,
  elem.type::STRING as element_type,
  elem.content::STRING as content
FROM {catalog}.{schema}.parsed_documents
LATERAL VIEW explode(
  from_json(to_json(parsed:document:elements), 'ARRAY<STRUCT<id:INT, type:STRING, content:STRING>>')
) t AS elem
""")

print(f"Parsed and flattened all documents")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 7b: Subpoena Extraction

# COMMAND ----------

spark.sql(f"""
CREATE OR REPLACE TABLE {catalog}.{schema}.extracted_subpoenas AS
WITH doc_text AS (
  SELECT file_name, concat_ws('\n\n', collect_list(content)) as full_text
  FROM {catalog}.{schema}.document_elements
  WHERE file_name LIKE 'subpoena_%'
  GROUP BY file_name
)
SELECT
  file_name,
  get_json_object(extracted, '$.case_number') as case_number,
  get_json_object(extracted, '$.court_jurisdiction') as court_jurisdiction,
  get_json_object(extracted, '$.requesting_party') as requesting_party,
  get_json_object(extracted, '$.responding_party') as responding_party,
  get_json_object(extracted, '$.data_custodians') as data_custodians,
  get_json_object(extracted, '$.date_range_start') as date_range_start,
  get_json_object(extracted, '$.date_range_end') as date_range_end,
  get_json_object(extracted, '$.document_categories_requested') as document_categories_requested,
  get_json_object(extracted, '$.production_deadline') as production_deadline,
  get_json_object(extracted, '$.preservation_required') as preservation_required,
  get_json_object(extracted, '$.special_instructions') as special_instructions
FROM (
  SELECT file_name,
    ai_query(
      'databricks-claude-sonnet-4-6',
      concat(
        'Extract the following fields from this subpoena. Return JSON with these fields (null if not found): ',
        'case_number, court_jurisdiction, requesting_party, responding_party, ',
        'data_custodians (array of names), date_range_start, date_range_end, ',
        'document_categories_requested (array of strings), production_deadline, ',
        'preservation_required (boolean), special_instructions (string). ',
        'Document:\n', full_text
      ),
      responseFormat => 'STRUCT<extraction:STRUCT<case_number:STRING, court_jurisdiction:STRING, requesting_party:STRING, responding_party:STRING, data_custodians:ARRAY<STRING>, date_range_start:STRING, date_range_end:STRING, document_categories_requested:ARRAY<STRING>, production_deadline:STRING, preservation_required:STRING, special_instructions:STRING>>'
    ) as extracted
  FROM doc_text
)
""")

count = spark.sql(f"SELECT count(*) as cnt FROM {catalog}.{schema}.extracted_subpoenas").first()["cnt"]
print(f"Extracted metadata from {count} subpoenas")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 7c: Invoice Extraction & Compliance Checking

# COMMAND ----------

spark.sql(f"""
CREATE OR REPLACE TABLE {catalog}.{schema}.extracted_invoices AS
WITH doc_text AS (
  SELECT file_name, concat_ws('\n\n', collect_list(content)) as full_text
  FROM {catalog}.{schema}.document_elements
  WHERE file_name LIKE 'invoice_%'
  GROUP BY file_name
)
SELECT
  file_name,
  get_json_object(extracted, '$.invoice_number') as invoice_number,
  get_json_object(extracted, '$.law_firm') as law_firm,
  get_json_object(extracted, '$.client') as client,
  get_json_object(extracted, '$.matter_number') as matter_number,
  get_json_object(extracted, '$.billing_period') as billing_period,
  get_json_object(extracted, '$.professional_services_total') as professional_services_total,
  get_json_object(extracted, '$.expenses_total') as expenses_total,
  get_json_object(extracted, '$.invoice_total') as invoice_total,
  get_json_object(extracted, '$.line_items') as line_items,
  get_json_object(extracted, '$.compliance_flags') as compliance_flags,
  get_json_object(extracted, '$.highest_hourly_rate') as highest_hourly_rate,
  get_json_object(extracted, '$.total_hours') as total_hours
FROM (
  SELECT file_name,
    ai_query(
      'databricks-claude-sonnet-4-6',
      concat(
        'You are a legal billing auditor. Extract invoice data AND flag billing compliance issues. ',
        'Return JSON with: invoice_number, law_firm, client, matter_number, billing_period, ',
        'professional_services_total, expenses_total, invoice_total, ',
        'highest_hourly_rate (string), total_hours (string), ',
        'line_items (array of objects with: timekeeper_role, hours, rate, amount, description), ',
        'compliance_flags (array of objects with: flag_type and description, where flag_type is one of: ',
        'BLOCK_BILLING, EXCESSIVE_HOURS, RATE_EXCEEDS_CAP, VAGUE_DESCRIPTION, DUPLICATE_CHARGE). ',
        'Flag any entries where: multiple tasks are combined in one entry (block billing), ',
        'single entries exceed 6 hours, rates exceed $900/hr, ',
        'descriptions are fewer than 8 words, or entries appear duplicated. ',
        'Document:\n', full_text
      ),
      responseFormat => 'STRUCT<extraction:STRUCT<invoice_number:STRING, law_firm:STRING, client:STRING, matter_number:STRING, billing_period:STRING, professional_services_total:STRING, expenses_total:STRING, invoice_total:STRING, highest_hourly_rate:STRING, total_hours:STRING, line_items:ARRAY<STRUCT<timekeeper_role:STRING, hours:STRING, rate:STRING, amount:STRING, description:STRING>>, compliance_flags:ARRAY<STRUCT<flag_type:STRING, description:STRING>>>>'
    ) as extracted
  FROM doc_text
)
""")

count = spark.sql(f"SELECT count(*) as cnt FROM {catalog}.{schema}.extracted_invoices").first()["cnt"]
print(f"Extracted and audited {count} invoices")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 7d: Regulatory Filing Extraction

# COMMAND ----------

spark.sql(f"""
CREATE OR REPLACE TABLE {catalog}.{schema}.extracted_regulatory AS
WITH doc_text AS (
  SELECT file_name, concat_ws('\n\n', collect_list(content)) as full_text
  FROM {catalog}.{schema}.document_elements
  WHERE file_name LIKE 'regulatory_%'
  GROUP BY file_name
)
SELECT
  file_name,
  get_json_object(extracted, '$.regulation_id') as regulation_id,
  get_json_object(extracted, '$.issuing_agency') as issuing_agency,
  get_json_object(extracted, '$.document_type') as document_type,
  get_json_object(extracted, '$.effective_date') as effective_date,
  get_json_object(extracted, '$.affected_entities') as affected_entities,
  get_json_object(extracted, '$.compliance_requirements') as compliance_requirements,
  get_json_object(extracted, '$.penalties') as penalties,
  get_json_object(extracted, '$.comment_period_deadline') as comment_period_deadline,
  get_json_object(extracted, '$.summary') as summary
FROM (
  SELECT file_name,
    ai_query(
      'databricks-claude-sonnet-4-6',
      concat(
        'Extract structured data from this regulatory filing. Return JSON with: ',
        'regulation_id, issuing_agency, document_type (Final Rule/Proposed Rule/Enforcement Action/etc), ',
        'effective_date, affected_entities (array of strings), ',
        'compliance_requirements (array of strings), penalties (array of strings), ',
        'comment_period_deadline (null if not applicable), ',
        'summary (2-3 sentence summary of the regulation). ',
        'Document:\n', full_text
      ),
      responseFormat => 'STRUCT<extraction:STRUCT<regulation_id:STRING, issuing_agency:STRING, document_type:STRING, effective_date:STRING, affected_entities:ARRAY<STRING>, compliance_requirements:ARRAY<STRING>, penalties:ARRAY<STRING>, comment_period_deadline:STRING, summary:STRING>>'
    ) as extracted
  FROM doc_text
)
""")

count = spark.sql(f"SELECT count(*) as cnt FROM {catalog}.{schema}.extracted_regulatory").first()["cnt"]
print(f"Extracted metadata from {count} regulatory filings")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 7e: Re-run general contract extraction for any new contracts

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
  WHERE file_name NOT LIKE 'subpoena_%'
    AND file_name NOT LIKE 'invoice_%'
    AND file_name NOT LIKE 'regulatory_%'
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
      'Document:\n', full_text
    ),
    responseFormat => 'STRUCT<extraction:STRUCT<document_type:STRING, parties:ARRAY<STRING>, effective_date:STRING, termination_date:STRING, governing_law:STRING, key_dollar_amounts:ARRAY<STRUCT<description:STRING, amount:STRING>>, confidentiality_period:STRING, termination_notice_period:STRING, non_compete_duration:STRING, key_obligations:ARRAY<STRING>, risk_flags:ARRAY<STRING>>>'
  ) as extracted_json
FROM doc_text
""")

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

print("All extraction pipelines complete!")

# COMMAND ----------

# Summary
for tbl in ["parsed_documents", "document_elements", "extracted_key_info", "extracted_subpoenas", "extracted_invoices", "extracted_regulatory"]:
    cnt = spark.sql(f"SELECT count(*) FROM {catalog}.{schema}.{tbl}").first()[0]
    print(f"  {tbl}: {cnt} rows")
