# Databricks notebook source
# MAGIC %md
# MAGIC # Step 4: Extract Document Elements
# MAGIC Flattens parsed document elements into a queryable table.

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
CREATE OR REPLACE TABLE {catalog}.{schema}.document_elements AS
SELECT
  replace(path, 'dbfs:/Volumes/{catalog}/{schema}/raw_documents/', '') as file_name,
  parsed:metadata:id::STRING as doc_id,
  elem.id::INT as element_id,
  elem.type::STRING as element_type,
  elem.content::STRING as content
FROM {catalog}.{schema}.parsed_documents
LATERAL VIEW explode(
  from_json(
    to_json(parsed:document:elements),
    'ARRAY<STRUCT<id:INT, type:STRING, content:STRING>>'
  )
) t AS elem
""")

# COMMAND ----------

count = spark.sql(f"SELECT count(*) as cnt FROM {catalog}.{schema}.document_elements").first()["cnt"]
docs = spark.sql(f"SELECT count(distinct file_name) as cnt FROM {catalog}.{schema}.document_elements").first()["cnt"]
print(f"Extracted {count} elements from {docs} documents")
