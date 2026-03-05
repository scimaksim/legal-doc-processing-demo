"""Genie Conversation API integration for natural language Q&A."""
import os
import asyncio
import aiohttp
from fastapi import APIRouter
from server.config import get_workspace_host, get_auth_token

router = APIRouter(prefix="/api/genie", tags=["genie"])

GENIE_SPACE_ID = os.environ.get("GENIE_SPACE_ID", "01f118d1043615e68733dc731144bc15")


@router.post("/ask")
async def genie_ask(body: dict):
    """Ask a question via the Genie Conversation API."""
    question = body.get("question", "")
    if not question:
        return {"error": "No question provided"}

    base = get_workspace_host()
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    async with aiohttp.ClientSession() as session:
        # Start conversation
        async with session.post(
            f"{base}/api/2.0/genie/spaces/{GENIE_SPACE_ID}/start-conversation",
            headers=headers,
            json={"content": question},
        ) as resp:
            data = await resp.json()

        if "conversation_id" not in data and "conversation" not in data:
            return {"error": f"Failed to start conversation: {data}"}

        conv_id = data.get("conversation_id") or data.get("conversation", {}).get("id")
        msg_id = data.get("message_id") or data.get("message", {}).get("id")

        if not conv_id or not msg_id:
            return {"error": f"Missing conversation/message ID: {data}"}

        # Poll for result
        for _ in range(30):
            await asyncio.sleep(2)
            async with session.get(
                f"{base}/api/2.0/genie/spaces/{GENIE_SPACE_ID}/conversations/{conv_id}/messages/{msg_id}",
                headers=headers,
            ) as resp:
                msg_data = await resp.json()

            status = msg_data.get("status")
            if status == "COMPLETED":
                break
            elif status in ("FAILED", "CANCELLED"):
                return {"error": f"Genie query {status}", "details": msg_data}
        else:
            return {"error": "Genie query timed out"}

        # Extract results
        attachments = msg_data.get("attachments", [])
        sql = None
        text_response = None
        query_result = None

        for att in attachments:
            if "query" in att:
                sql = att["query"].get("query")
                att_id = att.get("id")
                if att_id:
                    async with session.get(
                        f"{base}/api/2.0/genie/spaces/{GENIE_SPACE_ID}/conversations/{conv_id}/messages/{msg_id}/query-result/{att_id}",
                        headers=headers,
                    ) as resp:
                        query_result = await resp.json()
            elif "text" in att:
                text_response = att["text"].get("content")

        result = {
            "question": question,
            "sql": sql,
            "text_response": text_response,
            "conversation_id": conv_id,
            "source": "genie",
        }

        if query_result:
            columns = query_result.get("statement_response", {}).get("manifest", {}).get("schema", {}).get("columns", [])
            rows = query_result.get("statement_response", {}).get("result", {}).get("data_array", [])
            result["columns"] = [c.get("name", "") for c in columns]
            result["rows"] = rows
            result["row_count"] = len(rows)

        return result
