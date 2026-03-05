"""Natural language query route - Genie-style Q&A over legal documents."""
from fastapi import APIRouter
from server.sql_client import execute_sql_as_dicts, execute_sql
from server.config import CATALOG, SCHEMA

router = APIRouter(prefix="/api/nlquery", tags=["nlquery"])

TABLE_SCHEMA = f"""
Table: {CATALOG}.{SCHEMA}.extracted_key_info
Columns:
  - file_name (STRING): PDF filename
  - document_type (STRING): NDA, Software License, Employment Agreement, Commercial Lease, Master Services Agreement, Merger Agreement
  - parties (STRING): JSON array of party names
  - effective_date (STRING): when the agreement takes effect
  - termination_date (STRING): when the agreement ends
  - governing_law (STRING): state/jurisdiction
  - key_dollar_amounts (STRING): JSON array of {{description, amount}} objects
  - confidentiality_period (STRING): duration of confidentiality obligations
  - termination_notice_period (STRING): required notice for termination
  - non_compete_duration (STRING): non-compete clause duration
  - key_obligations (STRING): JSON array of key terms
  - risk_flags (STRING): JSON array of flagged risks

Table: {CATALOG}.{SCHEMA}.document_elements
Columns:
  - file_name (STRING): PDF filename
  - doc_id (STRING): document UUID
  - element_id (INT): element order
  - element_type (STRING): title, section_header, text, page_header
  - content (STRING): element text content
"""


@router.post("")
async def natural_language_query(body: dict):
    """Translate a natural language question to SQL, execute it, return results."""
    question = body.get("question", "")
    if not question:
        return {"error": "No question provided"}

    # Step 1: Use ai_query to generate SQL
    gen_sql = f"""
    SELECT ai_query(
        'databricks-claude-sonnet-4-6',
        'You are a SQL expert. Given this schema:

{TABLE_SCHEMA}

Write a Databricks SQL query to answer this question: {question}

Rules:
- Return ONLY the SQL query, no explanation, no markdown code fences
- Use the full table names including catalog and schema
- For JSON array columns (parties, key_dollar_amounts, key_obligations, risk_flags), use get_json_object or from_json as needed
- Limit results to 50 rows max
- Make the output readable with clear column aliases
'
    ) as generated_sql
    """

    try:
        result = await execute_sql_as_dicts(gen_sql)
        generated_sql = result[0]["generated_sql"].strip()

        # Clean up - remove markdown fences if present
        if generated_sql.startswith("```"):
            lines = generated_sql.split("\n")
            generated_sql = "\n".join(
                l for l in lines if not l.startswith("```")
            ).strip()

        # Step 2: Execute the generated SQL
        query_result = await execute_sql(generated_sql)

        return {
            "question": question,
            "sql": generated_sql,
            "columns": query_result["columns"],
            "rows": query_result["rows"],
            "row_count": len(query_result["rows"]),
        }
    except Exception as e:
        return {
            "question": question,
            "error": str(e),
            "sql": generated_sql if "generated_sql" in dir() else None,
        }
