import boto3
import csv
import json
import os

# =========================
# AWS CONFIG (MANUAL)
# =========================
#REPLACE WITH YOUR SESSION AWS ACCESS KEY ID
AWS_ACCESS_KEY_ID=""
#REPLACE WITH YOUR SESSION AWS SECRET KEY
AWS_SECRET_ACCESS_KEY=""
#REPLACE WITH YOUR SESSION AWS TOKEN
AWS_SESSION_TOKEN=""
AWS_REGION = "us-east-1"

#REPLACE WITH YOUR BUCKET NAME
BUCKET_NAME = ""
#YOUR FILES AND DOCUMENTS MUST BE INSIDE THIS FOLDER
PREFIX = "for_textract/"

OUTPUT_DIR = "output_for_S3"

# Create output folder
os.makedirs(OUTPUT_DIR, exist_ok=True)

# =========================
# AWS SESSION
# =========================
session = boto3.Session(
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    aws_session_token=AWS_SESSION_TOKEN,
    region_name=AWS_REGION
)

s3 = session.client("s3")
textract = session.client("textract")

# =========================
# LIST FILES
# =========================
def list_s3_files():
    response = s3.list_objects_v2(
        Bucket=BUCKET_NAME,
        Prefix=PREFIX
    )

    files = []
    for obj in response.get("Contents", []):
        key = obj["Key"]
        if not key.endswith("/"):
            files.append(key)

    return files

# =========================
# TEXTRACT OCR
# =========================
def extract_text(s3_key):
    print(type(s3_key), s3_key)
    response = textract.analyze_document(
        Document={
            "S3Object": {
                "Bucket": BUCKET_NAME,
                "Name": s3_key
            }
        },
        FeatureTypes=["FORMS", "TABLES"]
    )

    lines = []
    for block in response["Blocks"]:
        if block["BlockType"] == "LINE":
            lines.append(block["Text"])

    return "\n".join(lines)

# =========================
# SAVE MARKDOWN (KB FORMAT)
# =========================
def save_md(file_name, text, s3_key):
    md_path = os.path.join(OUTPUT_DIR, file_name + ".md")

    content = f"""# {file_name}

## Extracted Content
{text}

## Source
s3://{BUCKET_NAME}/{s3_key}
"""

    with open(md_path, "w", encoding="utf-8") as f:
        f.write(content)

# =========================
# SAVE JSON
# =========================
def save_json(file_name, text, s3_key):
    json_path = os.path.join(OUTPUT_DIR, file_name + ".json")

    data = {
        "file": file_name,
        "s3_key": s3_key,
        "text": text
    }

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

# =========================
# APPEND TO CSV
# =========================
def save_csv(rows):
    csv_path = os.path.join(OUTPUT_DIR, "knowledge_base.csv")

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["file", "s3_key", "content"])

        for row in rows:
            writer.writerow(row)

# =========================
# MAIN PIPELINE
# =========================
def process_all_files():
    files = list_s3_files()

    print(f"[FOUND] {len(files)} files\n")

    csv_rows = []

    for s3_key in files:
        file_name = s3_key.split("/")[-1].replace(".pdf", "")

        try:
            print(f"[PROCESSING] {s3_key}")

            # 1. OCR
            text = extract_text(s3_key)

            # 2. Save Markdown KB
            save_md(file_name, text, s3_key)

            # 3. Save JSON
            save_json(file_name, text, s3_key)

            # 4. Prepare CSV row
            csv_rows.append([file_name, s3_key, text[:5000]])  # limit size

            print(f"[DONE] {file_name}")

        except Exception as e:
            print(f"[ERROR] {s3_key}: {str(e)}")

    # Save CSV once
    save_csv(csv_rows)

    print("\n[COMPLETE] Knowledge base generated!")

# =========================
# RUN
# =========================
if __name__ == "__main__":
    process_all_files()