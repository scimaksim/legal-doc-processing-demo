"""Document browsing and viewing API routes."""
from fastapi import APIRouter, HTTPException
from server.sql_client import execute_sql_as_dicts, execute_sql
from server.config import ELEMENTS_TABLE

router = APIRouter(prefix="/api/documents", tags=["documents"])


@router.get("")
async def list_documents():
    """List all processed documents with element breakdown."""
    query = f"""
    SELECT
        file_name,
        doc_id,
        COUNT(*) as total_elements,
        SUM(CASE WHEN element_type = 'title' THEN 1 ELSE 0 END) as titles,
        SUM(CASE WHEN element_type = 'section_header' THEN 1 ELSE 0 END) as section_headers,
        SUM(CASE WHEN element_type = 'text' THEN 1 ELSE 0 END) as text_blocks,
        SUM(CASE WHEN element_type = 'page_header' THEN 1 ELSE 0 END) as page_headers
    FROM {ELEMENTS_TABLE}
    GROUP BY file_name, doc_id
    ORDER BY file_name
    """
    docs = await execute_sql_as_dicts(query)
    # Convert numeric strings to ints
    for doc in docs:
        for key in ["total_elements", "titles", "section_headers", "text_blocks", "page_headers"]:
            doc[key] = int(doc.get(key, 0) or 0)
    return {"documents": docs}


@router.get("/{doc_id}")
async def get_document(doc_id: str):
    """Get all elements for a specific document, organized by type."""
    query = f"""
    SELECT file_name, doc_id, element_id, element_type, content
    FROM {ELEMENTS_TABLE}
    WHERE doc_id = '{doc_id}'
    ORDER BY CAST(element_id AS INT)
    """
    elements = await execute_sql_as_dicts(query)
    if not elements:
        raise HTTPException(status_code=404, detail="Document not found")

    file_name = elements[0]["file_name"]

    # Group by element type
    by_type: dict[str, list] = {}
    for el in elements:
        t = el["element_type"]
        if t not in by_type:
            by_type[t] = []
        by_type[t].append({
            "element_id": int(el["element_id"]),
            "content": el["content"],
        })

    return {
        "file_name": file_name,
        "doc_id": doc_id,
        "total_elements": len(elements),
        "elements_by_type": by_type,
        "elements_ordered": [
            {
                "element_id": int(el["element_id"]),
                "element_type": el["element_type"],
                "content": el["content"],
            }
            for el in elements
        ],
    }


@router.get("/search/{query}")
async def search_documents(query: str):
    """Full-text search across all document content."""
    sql = f"""
    SELECT file_name, doc_id, element_id, element_type, content
    FROM {ELEMENTS_TABLE}
    WHERE LOWER(content) LIKE LOWER('%' || '{query}' || '%')
    ORDER BY file_name, CAST(element_id AS INT)
    LIMIT 100
    """
    results = await execute_sql_as_dicts(sql)
    return {"query": query, "total_results": len(results), "results": results}
