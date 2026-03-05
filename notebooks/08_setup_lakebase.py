# Databricks notebook source
# MAGIC %md
# MAGIC # Step 8: Setup Lakebase for Operational Workflows
# MAGIC Creates Lakebase (OLTP) tables for subpoena tracking and invoice review workflows.

# COMMAND ----------

try:
    catalog = spark.conf.get("spark.databricks.bundle.variables.catalog")
except Exception:
    catalog = "classic_stable_tetifz_catalog"

# COMMAND ----------

# MAGIC %md
# MAGIC ## Create Lakebase schema

# COMMAND ----------

spark.sql(f"CREATE SCHEMA IF NOT EXISTS {catalog}.legal_ops WITH DBPROPERTIES ('database_type' = 'LAKEBASE')")
print(f"Lakebase schema {catalog}.legal_ops created")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Create operational tables

# COMMAND ----------

spark.sql(f"""
CREATE TABLE IF NOT EXISTS {catalog}.legal_ops.subpoena_tracking (
  id STRING,
  file_name STRING,
  case_number STRING,
  status STRING,
  assigned_to STRING,
  priority STRING,
  notes STRING,
  created_at STRING,
  updated_at STRING
)
""")

spark.sql(f"""
CREATE TABLE IF NOT EXISTS {catalog}.legal_ops.invoice_reviews (
  id STRING,
  file_name STRING,
  invoice_number STRING,
  review_status STRING,
  reviewer STRING,
  approved_amount STRING,
  disputed_amount STRING,
  reviewer_notes STRING,
  created_at STRING,
  updated_at STRING
)
""")

print("Lakebase operational tables created: subpoena_tracking, invoice_reviews")
