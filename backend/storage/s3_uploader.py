import boto3
import os
from botocore.exceptions import NoCredentialsError
from dotenv import load_dotenv

load_dotenv()

s3 = boto3.client('s3',
                  aws_access_key_id=os.getenv("AWS_ACCESS_KEY"),
                  aws_secret_access_key=os.getenv("AWS_SECRET_KEY"))

BUCKET_NAME = os.getenv("S3_BUCKET")

def upload_to_s3(file_path, tender_id):
    file_name = f"{tender_id}.zip"
    try:
        s3.upload_file(file_path, BUCKET_NAME, file_name)
        s3_url = f"https://{BUCKET_NAME}.s3.amazonaws.com/{file_name}"
        return s3_url
    except FileNotFoundError:
        print("The file was not found")
    except NoCredentialsError:
        print("Credentials not available")
