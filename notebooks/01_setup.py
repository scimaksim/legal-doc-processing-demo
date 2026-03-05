# Databricks notebook source
# MAGIC %md
# MAGIC # Step 1: Setup Schema and Volumes
# MAGIC Creates the Unity Catalog schema and volumes for the legal document processing demo.

# COMMAND ----------

catalog = spark.conf.get("spark.databricks.bundle.variables.catalog", "classic_stable_tetifz_catalog")
schema = spark.conf.get("spark.databricks.bundle.variables.schema", "legal_docs")

# COMMAND ----------

spark.sql(f"CREATE SCHEMA IF NOT EXISTS {catalog}.{schema} COMMENT 'Legal document processing demo'")
spark.sql(f"CREATE VOLUME IF NOT EXISTS {catalog}.{schema}.raw_documents COMMENT 'Raw legal documents for parsing'")
spark.sql(f"CREATE VOLUME IF NOT EXISTS {catalog}.{schema}.parsed_images COMMENT 'Parsed document page images'")

print(f"Schema {catalog}.{schema} and volumes created successfully")
