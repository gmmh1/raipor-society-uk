"""S3-compatible object storage adapter (MinIO in every deployed environment today).

This is the only module allowed to import ``boto3``. Swapping the storage provider,
or self-hosting a different S3-compatible service, means changing this file alone.
"""

import boto3
from django.conf import settings


class StorageError(RuntimeError):
    pass


def _get_client():
    return boto3.client(
        "s3",
        endpoint_url=settings.S3_ENDPOINT,
        aws_access_key_id=settings.S3_ACCESS_KEY,
        aws_secret_access_key=settings.S3_SECRET_KEY,
        region_name=settings.S3_REGION,
    )


def upload_bytes(*, key: str, data: bytes, content_type: str) -> None:
    try:
        _get_client().put_object(
            Bucket=settings.S3_BUCKET,
            Key=key,
            Body=data,
            ContentType=content_type,
        )
    except Exception as exc:  # boto3 raises provider-specific botocore exceptions
        raise StorageError(f"Failed to upload object '{key}': {exc}") from exc


def download_bytes(*, key: str) -> bytes:
    try:
        response = _get_client().get_object(Bucket=settings.S3_BUCKET, Key=key)
        return response["Body"].read()
    except Exception as exc:
        raise StorageError(f"Failed to download object '{key}': {exc}") from exc


def generate_presigned_download_url(*, key: str, expires_in: int = 3600) -> str:
    try:
        return _get_client().generate_presigned_url(
            "get_object",
            Params={"Bucket": settings.S3_BUCKET, "Key": key},
            ExpiresIn=expires_in,
        )
    except Exception as exc:
        raise StorageError(f"Failed to generate download URL for '{key}': {exc}") from exc


def delete_object(*, key: str) -> None:
    try:
        _get_client().delete_object(Bucket=settings.S3_BUCKET, Key=key)
    except Exception as exc:
        raise StorageError(f"Failed to delete object '{key}': {exc}") from exc
