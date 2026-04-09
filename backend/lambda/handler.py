import json
from s3_retriever import get_context
from openai_service import ask_openai

def lambda_handler(event, context):
    try:
        body = json.loads(event["body"])
        user_query = body.get("query")

        # Get context from S3
        context_data = get_context(user_query)

        # Ask OpenAI
        response = ask_openai(user_query, context_data)

        return {
            "statusCode": 200,
            "body": json.dumps({"response": response})
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }