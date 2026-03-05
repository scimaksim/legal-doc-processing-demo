"""Operational workflow routes backed by Lakebase (OLTP)."""
import uuid
from datetime import datetime
from fastapi import APIRouter
from server.sql_client import execute_sql_as_dicts, execute_sql
from server.config import CATALOG

router = APIRouter(prefix="/api/ops", tags=["operations"])

LAKEBASE_SCHEMA = f"{CATALOG}.legal_ops"


@router.get("/subpoena-tracking")
async def list_subpoena_tracking():
    query = f"SELECT * FROM {LAKEBASE_SCHEMA}.subpoena_tracking ORDER BY created_at DESC"
    rows = await execute_sql_as_dicts(query)
    return {"items": rows}


@router.post("/subpoena-tracking")
async def create_subpoena_tracking(body: dict):
    row_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()
    query = f"""
    INSERT INTO {LAKEBASE_SCHEMA}.subpoena_tracking
    (id, file_name, case_number, status, assigned_to, priority, notes, created_at, updated_at)
    VALUES (
        '{row_id}',
        '{body.get("file_name", "")}',
        '{body.get("case_number", "")}',
        '{body.get("status", "New")}',
        '{body.get("assigned_to", "")}',
        '{body.get("priority", "Normal")}',
        '{body.get("notes", "")}',
        '{now}',
        '{now}'
    )
    """
    await execute_sql(query)
    return {"id": row_id, "status": "created"}


@router.put("/subpoena-tracking/{item_id}")
async def update_subpoena_tracking(item_id: str, body: dict):
    now = datetime.utcnow().isoformat()
    sets = []
    for field in ["status", "assigned_to", "priority", "notes"]:
        if field in body:
            sets.append(f"{field} = '{body[field]}'")
    sets.append(f"updated_at = '{now}'")
    query = f"UPDATE {LAKEBASE_SCHEMA}.subpoena_tracking SET {', '.join(sets)} WHERE id = '{item_id}'"
    await execute_sql(query)
    return {"id": item_id, "status": "updated"}


@router.get("/invoice-reviews")
async def list_invoice_reviews():
    query = f"SELECT * FROM {LAKEBASE_SCHEMA}.invoice_reviews ORDER BY created_at DESC"
    rows = await execute_sql_as_dicts(query)
    return {"items": rows}


@router.post("/invoice-reviews")
async def create_invoice_review(body: dict):
    row_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()
    query = f"""
    INSERT INTO {LAKEBASE_SCHEMA}.invoice_reviews
    (id, file_name, invoice_number, review_status, reviewer, approved_amount, disputed_amount, reviewer_notes, created_at, updated_at)
    VALUES (
        '{row_id}',
        '{body.get("file_name", "")}',
        '{body.get("invoice_number", "")}',
        '{body.get("review_status", "Pending")}',
        '{body.get("reviewer", "")}',
        '{body.get("approved_amount", "")}',
        '{body.get("disputed_amount", "")}',
        '{body.get("reviewer_notes", "")}',
        '{now}',
        '{now}'
    )
    """
    await execute_sql(query)
    return {"id": row_id, "status": "created"}


@router.put("/invoice-reviews/{item_id}")
async def update_invoice_review(item_id: str, body: dict):
    now = datetime.utcnow().isoformat()
    sets = []
    for field in ["review_status", "reviewer", "approved_amount", "disputed_amount", "reviewer_notes"]:
        if field in body:
            sets.append(f"{field} = '{body[field]}'")
    sets.append(f"updated_at = '{now}'")
    query = f"UPDATE {LAKEBASE_SCHEMA}.invoice_reviews SET {', '.join(sets)} WHERE id = '{item_id}'"
    await execute_sql(query)
    return {"id": item_id, "status": "updated"}
