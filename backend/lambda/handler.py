"""AWS Lambda handler for the UPOU Admissions AI Helpdesk.

Responsibilities:
- Accept a JSON payload with a "query" field
- Retrieve context from S3
- Call OpenAI to generate an answer (strictly using the provided context)
- If no relevant context is found, create a ticket in DynamoDB and return a fallback message

This file is written to be easy to include in a lambda deployment package.
"""

import json
import os
import logging
import uuid
from datetime import datetime

from s3_retriever import get_context
from openai_service import ask_openai
import boto3

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
logging.basicConfig()
logger = logging.getLogger("lambda_handler")
logger.setLevel(LOG_LEVEL)


def _response(status, body):
    return {
        "statusCode": status,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Methods": "POST,OPTIONS",
        },
        "body": json.dumps(body),
    }

def _create_ticket(question: str) -> dict:
    """Create a ticket record in DynamoDB and return the created item metadata.

    Table name is read from env var DDB_TICKETS_TABLE (default: 'tickets').
    """
    table_name = os.getenv("DDB_TICKETS_TABLE", "tickets")
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(table_name)

    item = {
        "id": str(uuid.uuid4()),
        "question": question,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "status": "pending",
    }

    table.put_item(Item=item)
    logger.info("Created ticket %s in table %s", item["id"], table_name)
    return item


def _parse_event_body(event: dict) -> dict:
    if not event:
        return {}

    body = event.get("body")

    # Case 1: API Gateway sends string
    if isinstance(body, str):
        if body.strip() == "":
            return {}
        try:
            return json.loads(body)
        except Exception:
            return {}

    # Case 2: already parsed
    if isinstance(body, dict):
        return body

    # Case 3: direct invocation
    if "query" in event:
        return event

    return {}


def lambda_handler(event, context):
    logger.debug("Event received: %s", event)

    # ✅ Handle preflight (CORS)
    if event.get("httpMethod") == "OPTIONS":
        return _response(200, {})

    try:
        body = _parse_event_body(event)
        user_query = (body or {}).get("query")

        if not user_query or not isinstance(user_query, str) or not user_query.strip():
            return _response(400, {"error": "Missing or invalid 'query' in request body"})

        user_query = user_query.strip()

        # 1) Retrieve context from S3
        context_text = get_context(user_query)

        # 2) If no context → fallback + ticket
        if not context_text:
            ticket = _create_ticket(user_query)
            fallback = (
                "I'm sorry — I couldn't find a relevant answer in the knowledge base. "
                "I've created a support ticket and our admissions team will follow up."
            )
            return _response(200, {"response": fallback, "ticket": ticket})

        # 3) Call OpenAI
        answer = ask_openai(user_query, context_text)

        if not answer or not answer.strip():
            ticket = _create_ticket(user_query)
            fallback = (
                "I couldn't produce a confident answer. I've created a support ticket so a human can follow up."
            )
            return _response(200, {"response": fallback, "ticket": ticket})

        # 4) Success
        return _response(200, {"response": answer})

    except Exception as e:
        logger.exception("Unhandled error in lambda_handler")
        return _response(500, {"error": str(e)})