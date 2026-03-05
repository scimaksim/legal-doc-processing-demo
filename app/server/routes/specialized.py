"""Specialized extraction API routes for subpoenas, invoices, and regulatory filings."""
import json
from fastapi import APIRouter
from server.sql_client import execute_sql_as_dicts
from server.config import CATALOG, SCHEMA

router = APIRouter(prefix="/api/specialized", tags=["specialized"])

JSON_FIELDS_SUBPOENAS = ["data_custodians", "document_categories_requested"]
JSON_FIELDS_INVOICES = ["line_items", "compliance_flags"]
JSON_FIELDS_REGULATORY = ["affected_entities", "compliance_requirements", "penalties"]


def parse_json_fields(rows: list[dict], fields: list[str]) -> list[dict]:
    for row in rows:
        for key in fields:
            if row.get(key):
                try:
                    row[key] = json.loads(row[key])
                except (json.JSONDecodeError, TypeError):
                    pass
    return rows


@router.get("/subpoenas")
async def list_subpoenas():
    query = f"""
    SELECT * FROM {CATALOG}.{SCHEMA}.extracted_subpoenas ORDER BY file_name
    """
    rows = await execute_sql_as_dicts(query)
    return {"documents": parse_json_fields(rows, JSON_FIELDS_SUBPOENAS)}


@router.get("/invoices")
async def list_invoices():
    query = f"""
    SELECT * FROM {CATALOG}.{SCHEMA}.extracted_invoices ORDER BY file_name
    """
    rows = await execute_sql_as_dicts(query)
    return {"documents": parse_json_fields(rows, JSON_FIELDS_INVOICES)}


@router.get("/regulatory")
async def list_regulatory():
    query = f"""
    SELECT * FROM {CATALOG}.{SCHEMA}.extracted_regulatory ORDER BY file_name
    """
    rows = await execute_sql_as_dicts(query)
    return {"documents": parse_json_fields(rows, JSON_FIELDS_REGULATORY)}
