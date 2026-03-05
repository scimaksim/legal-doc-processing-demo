"""Extracted key information API routes."""
from fastapi import APIRouter
from server.sql_client import execute_sql_as_dicts
from server.config import CATALOG, SCHEMA

router = APIRouter(prefix="/api/extraction", tags=["extraction"])

KEY_INFO_TABLE = f"{CATALOG}.{SCHEMA}.extracted_key_info"


@router.get("")
async def list_extractions():
    """List extracted key info for all documents."""
    query = f"""
    SELECT
        file_name,
        document_type,
        parties,
        effective_date,
        termination_date,
        governing_law,
        key_dollar_amounts,
        confidentiality_period,
        termination_notice_period,
        non_compete_duration,
        key_obligations,
        risk_flags
    FROM {KEY_INFO_TABLE}
    ORDER BY file_name
    """
    rows = await execute_sql_as_dicts(query)
    import json
    for row in rows:
        for key in ["parties", "key_dollar_amounts", "key_obligations", "risk_flags"]:
            if row.get(key):
                try:
                    row[key] = json.loads(row[key])
                except (json.JSONDecodeError, TypeError):
                    pass
    return {"documents": rows}


@router.get("/{file_name}")
async def get_extraction(file_name: str):
    """Get extracted key info for a specific document."""
    query = f"""
    SELECT *
    FROM {KEY_INFO_TABLE}
    WHERE file_name = '{file_name}'
    """
    rows = await execute_sql_as_dicts(query)
    if not rows:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Extraction not found")
    import json
    row = rows[0]
    for key in ["parties", "key_dollar_amounts", "key_obligations", "risk_flags"]:
        if row.get(key):
            try:
                row[key] = json.loads(row[key])
            except (json.JSONDecodeError, TypeError):
                pass
    return row
