import boto3
import uuid
from datetime import datetime

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("tickets")

def create_ticket(question):
    table.put_item(Item={
        "id": str(uuid.uuid4()),
        "question": question,
        "timestamp": str(datetime.now()),
        "status": "pending"
    })