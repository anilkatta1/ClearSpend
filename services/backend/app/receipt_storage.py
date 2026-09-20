import base64
import io
import os
from functools import lru_cache
from urllib.parse import urlsplit

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from minio import Minio
from minio.error import S3Error

from app.config import settings

ENVELOPE_MAGIC = b"CS01"
NONCE_BYTES = 12


class ReceiptStorageError(RuntimeError):
    pass


def _encryption_key() -> bytes:
    try:
        key = base64.b64decode(settings.receipt_encryption_key, validate=True)
    except ValueError as exc:
        raise ReceiptStorageError("Receipt encryption key is not valid base64") from exc
    if len(key) != 32:
        raise ReceiptStorageError("Receipt encryption key must decode to 32 bytes")
    return key


def encrypt_receipt(content: bytes, object_key: str) -> bytes:
    nonce = os.urandom(NONCE_BYTES)
    ciphertext = AESGCM(_encryption_key()).encrypt(nonce, content, object_key.encode())
    return ENVELOPE_MAGIC + nonce + ciphertext


def decrypt_receipt(envelope: bytes, object_key: str) -> bytes:
    if (
        not envelope.startswith(ENVELOPE_MAGIC)
        or len(envelope) <= len(ENVELOPE_MAGIC) + NONCE_BYTES
    ):
        raise ReceiptStorageError("Receipt object has an invalid encryption envelope")
    nonce_start = len(ENVELOPE_MAGIC)
    nonce = envelope[nonce_start : nonce_start + NONCE_BYTES]
    ciphertext = envelope[nonce_start + NONCE_BYTES :]
    try:
        return AESGCM(_encryption_key()).decrypt(nonce, ciphertext, object_key.encode())
    except Exception as exc:
        raise ReceiptStorageError("Receipt object failed authenticated decryption") from exc


@lru_cache
def storage_client() -> Minio:
    endpoint = urlsplit(settings.receipt_storage_endpoint)
    address = endpoint.netloc or endpoint.path
    if not address:
        raise ReceiptStorageError("Receipt storage endpoint is invalid")
    return Minio(
        address,
        access_key=settings.receipt_storage_access_key,
        secret_key=settings.receipt_storage_secret_key,
        secure=settings.receipt_storage_secure,
    )


def ensure_receipt_buckets() -> None:
    try:
        client = storage_client()
        for bucket in (settings.receipt_quarantine_bucket, settings.receipt_clean_bucket):
            if not client.bucket_exists(bucket):
                client.make_bucket(bucket)
    except (OSError, S3Error) as exc:
        raise ReceiptStorageError("Receipt object storage is unavailable") from exc


def put_quarantined_receipt(object_key: str, content: bytes, content_type: str) -> None:
    ensure_receipt_buckets()
    encrypted = encrypt_receipt(content, object_key)
    try:
        storage_client().put_object(
            settings.receipt_quarantine_bucket,
            object_key,
            io.BytesIO(encrypted),
            len(encrypted),
            content_type="application/octet-stream",
            metadata={"original-content-type": content_type, "encryption": "AES-256-GCM"},
        )
    except (OSError, S3Error) as exc:
        raise ReceiptStorageError("Could not write quarantined receipt") from exc


def get_receipt(bucket: str, object_key: str) -> bytes:
    try:
        response = storage_client().get_object(bucket, object_key)
    except (OSError, S3Error) as exc:
        raise ReceiptStorageError("Could not read receipt object") from exc
    try:
        return decrypt_receipt(response.read(), object_key)
    finally:
        response.close()
        response.release_conn()


def promote_receipt(object_key: str, content: bytes, content_type: str) -> None:
    encrypted = encrypt_receipt(content, object_key)
    try:
        storage_client().put_object(
            settings.receipt_clean_bucket,
            object_key,
            io.BytesIO(encrypted),
            len(encrypted),
            content_type="application/octet-stream",
            metadata={"original-content-type": content_type, "encryption": "AES-256-GCM"},
        )
        storage_client().remove_object(settings.receipt_quarantine_bucket, object_key)
    except (OSError, S3Error) as exc:
        raise ReceiptStorageError("Could not promote receipt to clean storage") from exc


def remove_receipt(bucket: str, object_key: str) -> None:
    try:
        storage_client().remove_object(bucket, object_key)
    except (OSError, S3Error) as exc:
        raise ReceiptStorageError("Could not remove receipt object") from exc
