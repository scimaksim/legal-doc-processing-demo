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

Table: {CATALOG}.{SCHEMA}.extracted_subpoenas
Columns:
  - file_name (STRING): PDF filename (subpoena_XXX.pdf)
  - case_number (STRING): court case number
  - court_jurisdiction (STRING): court and jurisdiction
  - requesting_party (STRING): who issued the subpoena
  - responding_party (STRING): who must respond
  - data_custodians (STRING): JSON array of custodian names
  - date_range_start (STRING): start of document production date range
  - date_range_end (STRING): end of document production date range
  - document_categories_requested (STRING): JSON array of requested document types
  - production_deadline (STRING): when documents must be produced
  - preservation_required (STRING): whether preservation is required
  - special_instructions (STRING): any special handling instructions

Table: {CATALOG}.{SCHEMA}.extracted_invoices
Columns:
  - file_name (STRING): PDF filename (invoice_XXX.pdf)
  - invoice_number (STRING): invoice ID
  - law_firm (STRING): billing law firm name
  - client (STRING): client being billed
  - matter_number (STRING): matter/case reference
  - billing_period (STRING): period covered
  - professional_services_total (STRING): total for professional services
  - expenses_total (STRING): total expenses
  - invoice_total (STRING): grand total
  - line_items (STRING): JSON array of line items with timekeeper_role, hours, rate, amount, description
  - compliance_flags (STRING): JSON array of compliance issues with flag_type and description
  - highest_hourly_rate (STRING): highest rate billed
  - total_hours (STRING): total hours billed

Table: {CATALOG}.{SCHEMA}.extracted_regulatory
Columns:
  - file_name (STRING): PDF filename (regulatory_XXX.pdf)
  - regulation_id (STRING): regulation identifier
  - issuing_agency (STRING): regulatory agency name
  - document_type (STRING): Final Rule, Proposed Rule, Enforcement Action, etc.
  - effective_date (STRING): when regulation takes effect
  - affected_entities (STRING): JSON array of affected entity types
  - compliance_requirements (STRING): JSON array of compliance requirements
  - penalties (STRING): JSON array of penalty descriptions
  - comment_period_deadline (STRING): deadline for public comments (null if not applicable)
  - summary (STRING): 2-3 sentence summary
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
