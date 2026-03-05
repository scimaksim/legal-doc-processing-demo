CREATE OR REPLACE TABLE classic_stable_tetifz_catalog.legal_docs.parsed_documents AS
SELECT path, ai_parse_document(content, map('version', '2.0', 'imageOutputPath', '/Volumes/classic_stable_tetifz_catalog/legal_docs/parsed_images/')) as parsed
FROM READ_FILES('/Volumes/classic_stable_tetifz_catalog/legal_docs/raw_documents/', format => 'binaryFile')
