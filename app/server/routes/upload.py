"""Document upload and processing routes."""
import base64
from fastapi import APIRouter, UploadFile, File, HTTPException
from server.config import (
    get_workspace_host,
    get_auth_token,
    RAW_VOLUME,
    CATALOG,
    SCHEMA,
    ELEMENTS_TABLE,
    PARSED_TABLE,
)
from server.sql_client import execute_sql, execute_sql_as_dicts
import aiohttp

router = APIRouter(prefix="/api/upload", tags=["upload"])


@router.post("")
async def upload_document(file: UploadFile = File(...)):
    """Upload a PDF document to the volume, parse it, and flatten elements."""
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    contents = await file.read()
    file_name = file.filename

    # 1. Upload to volume via Files API
    host = get_workspace_host()
    token = get_auth_token()
    volume_path = f"{RAW_VOLUME}/{file_name}"
    upload_url = f"{host}/api/2.0/fs/files{volume_path}"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/octet-stream",
    }

    async with aiohttp.ClientSession() as session:
        async with session.put(upload_url, data=contents, headers=headers) as resp:
            if resp.status not in (200, 201, 204):
                error = await resp.text()
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to upload file: {error}",
                )

    # 2. Run ai_document_parse on the uploaded file and insert into parsed_documents
    parse_sql = f"""
    INSERT INTO {PARSED_TABLE} (path, parsed)
    SELECT
        '{volume_path}' as path,
        ai_document_parse('{volume_path}') as parsed
    """
    try:
        await execute_sql(parse_sql)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Document parsing failed: {str(e)}",
        )

    # 3. Flatten parsed output into document_elements
    flatten_sql = f"""
    INSERT INTO {ELEMENTS_TABLE} (file_name, doc_id, element_id, element_type, content)
    SELECT
        '{file_name}' as file_name,
        uuid() as doc_id,
        posexplode.pos as element_id,
        posexplode.col.elementType as element_type,
        posexplode.col.content as content
    FROM (
        SELECT parsed
        FROM {PARSED_TABLE}
        WHERE path = '{volume_path}'
        ORDER BY path DESC
        LIMIT 1
    ),
    LATERAL posexplode(parsed:elements) as posexplode(pos, col)
    """
    try:
        await execute_sql(flatten_sql)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Element flattening failed: {str(e)}",
        )

    return {
        "status": "success",
        "file_name": file_name,
        "message": f"Document '{file_name}' uploaded, parsed, and indexed successfully.",
    }
