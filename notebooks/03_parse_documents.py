# Databricks notebook source
# MAGIC %md
# MAGIC # Step 3: Parse Documents with ai_document_parse
# MAGIC Processes all PDFs in the volume using Databricks AI Functions.

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
CREATE OR REPLACE TABLE {catalog}.{schema}.parsed_documents AS
SELECT path, ai_parse_document(content, map('version', '2.0',
    'imageOutputPath', '/Volumes/{catalog}/{schema}/parsed_images/')) as parsed
FROM READ_FILES('/Volumes/{catalog}/{schema}/raw_documents/', format => 'binaryFile')
""")

# COMMAND ----------

count = spark.sql(f"SELECT count(*) as cnt FROM {catalog}.{schema}.parsed_documents").first()["cnt"]
print(f"Parsed {count} documents successfully")
