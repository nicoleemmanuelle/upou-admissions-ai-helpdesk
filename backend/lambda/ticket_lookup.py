"""Lambda to lookup a ticket by id from DynamoDB and return selected fields.

Returns JSON with: id, question, timestamp, status, answer
"""
import json
import os
import logging

import boto3

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
logging.basicConfig()
logger = logging.getLogger("ticket_lookup")
logger.setLevel(LOG_LEVEL)


def _response(status: int, body: dict):
    return {
        "statusCode": status,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Methods": "GET,OPTIONS",
        },
        "body": json.dumps(body),
    }


def _extract_ticket_id(event: dict) -> str:
    if event.get("pathParameters"):
        p = event["pathParameters"]
        return p.get("ticket_id") or p.get("id")
    if event.get("ticket_id"):
        return event.get("ticket_id")
    path = event.get("path") or event.get("rawPath")
    if path:
        parts = [p for p in path.split("/") if p]
        for i, seg in enumerate(parts):
            if seg == "id" and i + 1 < len(parts):
                return parts[i + 1]
    return None


def lambda_handler(event, context):
    logger.debug("Event: %s", event)

    if event.get("httpMethod") == "OPTIONS":
        return _response(200, {})

    ticket_id = _extract_ticket_id(event)
    if not ticket_id:
        return _response(400, {"error": "Missing ticket id in path or parameters"})

    table_name = os.getenv("DDB_TICKETS_TABLE", "tickets")
    try:
        ddb = boto3.resource("dynamodb")
        table = ddb.Table(table_name)
        resp = table.get_item(Key={"id": ticket_id})
    except Exception:
        logger.exception("Error fetching ticket %s", ticket_id)
        return _response(500, {"error": "Internal server error"})

    item = resp.get("Item")
    if not item:
        return _response(404, {"error": "Ticket not found"})

    out = {
        "id": item.get("id"),
        "question": item.get("question"),
        "answer": item.get("answer", ""),
        "timestamp": item.get("timestamp"),
        "status": item.get("status"),
    }

    return _response(200, out)
