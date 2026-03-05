"""Analytics dashboard API routes."""
from fastapi import APIRouter
from server.sql_client import execute_sql_as_dicts
from server.config import ELEMENTS_TABLE

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/overview")
async def get_overview():
    """Get overall statistics."""
    query = f"""
    SELECT
        COUNT(DISTINCT file_name) as total_documents,
        COUNT(DISTINCT doc_id) as total_doc_ids,
        COUNT(*) as total_elements,
        COUNT(DISTINCT element_type) as unique_element_types
    FROM {ELEMENTS_TABLE}
    """
    rows = await execute_sql_as_dicts(query)
    stats = rows[0] if rows else {}
    for k in stats:
        stats[k] = int(stats[k] or 0)
    return stats


@router.get("/element-distribution")
async def get_element_distribution():
    """Get element type distribution across all documents."""
    query = f"""
    SELECT element_type, COUNT(*) as count
    FROM {ELEMENTS_TABLE}
    GROUP BY element_type
    ORDER BY count DESC
    """
    rows = await execute_sql_as_dicts(query)
    for r in rows:
        r["count"] = int(r["count"])
    return {"distribution": rows}


@router.get("/document-comparison")
async def get_document_comparison():
    """Get per-document element breakdown for comparison."""
    query = f"""
    SELECT
        file_name,
        element_type,
        COUNT(*) as count
    FROM {ELEMENTS_TABLE}
    GROUP BY file_name, element_type
    ORDER BY file_name, element_type
    """
    rows = await execute_sql_as_dicts(query)
    for r in rows:
        r["count"] = int(r["count"])

    # Pivot into per-document structure
    docs: dict[str, dict] = {}
    for r in rows:
        fn = r["file_name"]
        if fn not in docs:
            docs[fn] = {"file_name": fn, "elements": {}}
        docs[fn]["elements"][r["element_type"]] = r["count"]

    return {"documents": list(docs.values())}


@router.get("/content-stats")
async def get_content_stats():
    """Get content length statistics per document."""
    query = f"""
    SELECT
        file_name,
        COUNT(*) as element_count,
        SUM(LENGTH(content)) as total_chars,
        AVG(LENGTH(content)) as avg_element_length,
        MAX(LENGTH(content)) as max_element_length
    FROM {ELEMENTS_TABLE}
    GROUP BY file_name
    ORDER BY total_chars DESC
    """
    rows = await execute_sql_as_dicts(query)
    for r in rows:
        r["element_count"] = int(r["element_count"] or 0)
        r["total_chars"] = int(r["total_chars"] or 0)
        r["avg_element_length"] = round(float(r["avg_element_length"] or 0), 1)
        r["max_element_length"] = int(r["max_element_length"] or 0)
    return {"stats": rows}
