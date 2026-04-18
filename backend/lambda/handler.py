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
    # Support direct invocation (payload is a dict) and API Gateway proxy (body is JSON string)
    if event is None:
        return {}
    if isinstance(event.get("body"), str):
        try:
            return json.loads(event["body"])
        except Exception:
            return {}
    return event.get("body") or event


def lambda_handler(event, context):
    logger.debug("Event received: %s", event)
    try:
        body = _parse_event_body(event)
        user_query = (body or {}).get("query")

        if not user_query or not isinstance(user_query, str) or not user_query.strip():
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Missing or invalid 'query' in request body"}),
            }

        user_query = user_query.strip()

        # 1) Retrieve context from S3
        context_text = get_context(user_query)

        # 2) If there's no relevant context, create a ticket and return fallback
        if not context_text:
            ticket = _create_ticket(user_query)
            fallback = (
                "I'm sorry — I couldn't find a relevant answer in the knowledge base. "
                "I've created a support ticket and our admissions team will follow up."
            )
            return {
                "statusCode": 200,
                "body": json.dumps({"response": fallback, "ticket": ticket}),
            }

        # 3) Call OpenAI with system prompt + context + user question
        answer = ask_openai(user_query, context_text)

        # If the model declined or returned nothing, create a ticket
        if not answer or not answer.strip():
            ticket = _create_ticket(user_query)
            fallback = (
                "I couldn't produce a confident answer. I've created a support ticket so a human can follow up."
            )
            return {
                "statusCode": 200,
                "body": json.dumps({"response": fallback, "ticket": ticket}),
            }

        # 4) Return the model answer
        return {"statusCode": 200, "body": json.dumps({"response": answer})}

    except Exception as e:
        logger.exception("Unhandled error in lambda_handler")
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}