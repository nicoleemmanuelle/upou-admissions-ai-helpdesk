import json
from s3_retriever import get_context
from openai_service import ask_openai

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Allow-Methods": "POST, OPTIONS",
}

def lambda_handler(event, context):
    # Handle CORS preflight
    if event.get("httpMethod") == "OPTIONS":
        return {"statusCode": 200, "headers": CORS_HEADERS, "body": ""}

    try:
        body = json.loads(event.get("body", "{}"))
        user_query = body.get("query", "").strip()

        if not user_query:
            return {
                "statusCode": 400,
                "headers": CORS_HEADERS,
                "body": json.dumps({"error": "Missing or empty 'query' field"})
            }

        # Get context from S3
        context_data = get_context(user_query)
        print(f"Query: {user_query}")
        print(f"Context length: {len(context_data)} chars")
        print(f"Context preview: {context_data[:200] if context_data else 'EMPTY'}")

        # Ask OpenAI
        response = ask_openai(user_query, context_data)

        return {
            "statusCode": 200,
            "headers": CORS_HEADERS,
            "body": json.dumps({"response": response})
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "headers": CORS_HEADERS,
            "body": json.dumps({"error": str(e)})
        }