import os
import uuid
from datetime import datetime
import boto3
import logging

sns = boto3.client("sns")
TOPIC_ARN = os.getenv("SNS_TOPIC_ARN") #LAMBDA ENVIRONMENT VARIABLES SNS ARN NUMBER FOR NOTIFICATION

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def categorize(query: str) -> str:
    q = query.lower()
    if "admission" in q:
        return "admission"
    elif "enroll" in q:
        return "enrollment"
    elif "fee" in q or "payment" in q:
        return "finance"
    return "general"


def detect_priority(query: str) -> str:
    q = query.lower()
    if "urgent" in q or "asap" in q:
        return "HIGH"
    elif "help" in q:
        return "MEDIUM"
    return "LOW"

def send_notification(message: str):
    if not TOPIC_ARN:
        logger.info("SNS_TOPIC_ARN not set. Skipping SNS notification.")
        return

    try:
        sns.publish(
            TopicArn=TOPIC_ARN,
            Subject="New Helpdesk Ticket",
            Message=message
        )
        logger.info("SNS notification sent successfully.")
    except Exception as e:
        logger.error(f"Failed to send SNS notification: {e}")

def _create_ticket(question: str) -> dict:
    table_name = os.getenv("DDB_TICKETS_TABLE", "tickets") #key and value in lambda
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(table_name)

    ticket_id = str(uuid.uuid4())
    timestamp = datetime.utcnow().isoformat() + "Z"

    item = {
        "id": ticket_id,  # keep existing schema
        "question": question,
        "answer": "",
        "timestamp": timestamp,
        "status": "pending",
        "category": categorize(question),
        "priority": detect_priority(question),
    }

    table.put_item(Item=item)
   
    message = (
        f"New Ticket Created\n\n"
        f"ID: {ticket_id}\n"
        f"Question: {question}\n"
        f"Category: {item['category']}\n"   
        f"Priority: {item['priority']}\n"
        f"Timestamp: {timestamp}\n"
    )

    send_notification(message)

    logger.info(
        "Created ticket %s with category %s and priority %s",
                ticket_id, 
                item["category"], 
                item["priority"])

    return item
