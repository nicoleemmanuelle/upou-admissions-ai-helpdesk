import boto3

s3 = boto3.client("s3")
BUCKET_NAME = "upou-admissions-kb"

def get_context(query):
    objects = s3.list_objects_v2(Bucket=BUCKET_NAME)

    context = ""
    for obj in objects.get("Contents", []):
        file = s3.get_object(Bucket=BUCKET_NAME, Key=obj["Key"])
        content = file["Body"].read().decode("utf-8")

        # simple keyword filtering
        if any(word in content.lower() for word in query.lower().split()):
            context += content + "\n"

    return context[:5000]  # limit size