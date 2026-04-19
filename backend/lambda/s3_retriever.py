"""S3 knowledge base retriever.

This module looks for documents in a configured S3 bucket and returns a
concatenated context string containing documents that match the user's query.
It's intentionally simple to keep the lambda package small. For production,
replace with an embeddings/vector search.
"""

import os
import logging
from typing import List

import boto3

logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("LOG_LEVEL", "INFO"))


def _list_bucket_objects(s3_client, bucket: str) -> List[dict]:
    paginator = s3_client.get_paginator("list_objects_v2")
    page_iter = paginator.paginate(Bucket=bucket)
    for page in page_iter:
        for obj in page.get("Contents", []) if page.get("Contents") else []:
            yield obj


def get_context(query: str, max_chars: int = 4000) -> str:
    bucket = os.getenv("S3_BUCKET", "upou-admissions-kb")
    s3 = boto3.client("s3")

    if not query:
        return ""

    query_terms = [t.strip().lower() for t in query.split() if t.strip()]
    if not query_terms:
        return ""

    pieces: List[str] = []
    for obj in _list_bucket_objects(s3, bucket):
        key = obj.get("Key")
        try:
            resp = s3.get_object(Bucket=bucket, Key=key)
            body = resp["Body"].read().decode("utf-8")
        except Exception:
            logger.exception("Failed to read object %s from bucket %s", key, bucket)
            continue

        text = body.lower()
        if any(term in text for term in query_terms):
            pieces.append(body)
            # stop early if we already reached the max chars
            if sum(len(p) for p in pieces) >= max_chars:
                break

    context = "\n---\n".join(pieces)
    # Trim to max_chars preserving word boundaries
    if len(context) > max_chars:
        context = context[:max_chars]
        # try to cut at the last newline to avoid chopping sentences
        last_newline = context.rfind("\n")
        if last_newline > 0:
            context = context[:last_newline]

    return context