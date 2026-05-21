import boto3
import os
import uuid
from botocore.exceptions import ClientError

AWS_ACCESS_KEY_ID     = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
AWS_S3_BUCKET         = os.environ.get("AWS_S3_BUCKET", "tesdocs")
AWS_S3_REGION         = os.environ.get("AWS_S3_REGION", "eu-west-1")


def get_s3_client():
    return boto3.client(
        "s3",
        region_name=AWS_S3_REGION,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    )


def upload_file_to_s3(file_bytes: bytes, filename: str, content_type: str = "application/pdf") -> str:
    """Upload bytes to S3 and return the public URL."""
    client = get_s3_client()
    ext = filename.rsplit(".", 1)[-1] if "." in filename else "pdf"
    key = f"product-docs/{uuid.uuid4().hex}.{ext}"

    client.put_object(
        Bucket=AWS_S3_BUCKET,
        Key=key,
        Body=file_bytes,
        ContentType=content_type,
    )

    url = f"https://{AWS_S3_BUCKET}.s3.{AWS_S3_REGION}.amazonaws.com/{key}"
    return url
