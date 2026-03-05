"""SQL statement execution client using Databricks SQL Statements API."""
import aiohttp
from typing import Any
from server.config import get_workspace_host, get_auth_token, get_warehouse_id


async def execute_sql(statement: str, parameters: list[dict] | None = None) -> dict[str, Any]:
    """Execute a SQL statement and return results.

    Returns dict with keys: columns (list of names), rows (list of lists).
    """
    host = get_workspace_host()
    token = get_auth_token()
    warehouse_id = get_warehouse_id()

    url = f"{host}/api/2.0/sql/statements"
    payload = {
        "warehouse_id": warehouse_id,
        "statement": statement,
        "wait_timeout": "50s",
    }
    if parameters:
        payload["parameters"] = parameters

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as response:
            if response.status != 200:
                error_text = await response.text()
                raise RuntimeError(f"SQL API error ({response.status}): {error_text}")
            data = await response.json()

    status = data.get("status", {}).get("state", "UNKNOWN")
    if status == "FAILED":
        error_msg = data.get("status", {}).get("error", {}).get("message", "Unknown SQL error")
        raise RuntimeError(f"SQL execution failed: {error_msg}")

    if status != "SUCCEEDED":
        raise RuntimeError(f"SQL statement in unexpected state: {status}")

    columns = [
        col["name"]
        for col in data.get("manifest", {}).get("schema", {}).get("columns", [])
    ]
    rows = data.get("result", {}).get("data_array", [])

    return {"columns": columns, "rows": rows}


async def execute_sql_as_dicts(statement: str, parameters: list[dict] | None = None) -> list[dict]:
    """Execute SQL and return results as list of dicts."""
    result = await execute_sql(statement, parameters)
    columns = result["columns"]
    return [dict(zip(columns, row)) for row in result["rows"]]
