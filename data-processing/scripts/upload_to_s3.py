import boto3
import os

s3 = boto3.client("s3")
bucket = "upou-admissions-kb"

def upload_folder(folder):
    for file in os.listdir(folder):
        s3.upload_file(f"{folder}/{file}", bucket, file)

upload_folder("../processed")