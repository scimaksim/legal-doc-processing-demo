CREATE OR REPLACE TABLE classic_stable_tetifz_catalog.legal_docs.document_elements AS
SELECT
  replace(path, 'dbfs:/Volumes/classic_stable_tetifz_catalog/legal_docs/raw_documents/', '') as file_name,
  parsed:metadata:id::STRING as doc_id,
  elem.id::INT as element_id,
  elem.type::STRING as element_type,
  elem.content::STRING as content
FROM classic_stable_tetifz_catalog.legal_docs.parsed_documents
LATERAL VIEW explode(
  from_json(
    to_json(parsed:document:elements),
    'ARRAY<STRUCT<id:INT, type:STRING, content:STRING>>'
  )
) t AS elem
