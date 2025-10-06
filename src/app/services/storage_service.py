from typing import Optional
from bson import ObjectId
from app.db.mongo import fs, documents_collection

def save_file_to_gridfs(file_path: str, doc_id: str) -> str:
    """
    Store a file from local path into Mongo GridFS, link it to documents_collection[doc_id].
    Returns the created GridFS file_id as str.
    """
    with open(file_path, "rb") as f:
        file_id = fs.put(f, filename=file_path, doc_id=doc_id)
    documents_collection.update_one(
        {"_id": doc_id},
        {"$set": {"file_id": str(file_id), "file_stored": True}}
    )
    return str(file_id)

def get_file_from_gridfs(file_id: str) -> bytes:
    """
    Read a file's binary content from GridFS by file_id (stringified ObjectId).
    """
    gridout = fs.get(ObjectId(file_id))
    return gridout.read()

def has_file(doc_id: str) -> bool:
    """Check if document has a GridFS file linked."""
    doc = documents_collection.find_one({"_id": doc_id}, {"file_id": 1})
    return bool(doc and doc.get("file_id"))

def unlink_file(doc_id: str) -> None:
    """
    (Optional) Remove GridFS file linkage from document (does not delete from GridFS).
    Useful if you want to rotate files.
    """
    documents_collection.update_one(
        {"_id": doc_id},
        {"$unset": {"file_id": "", "file_stored": ""}}
    )


# ---- IGNORE ---

# import os
# from typing import Optional

# STORAGE_BACKEND = os.getenv("STORAGE_BACKEND", "gridfs").lower()

# # --- GridFS imports ---
# from app.db.mongo import fs, documents_collection
# from bson import ObjectId

# # --- S3 imports ---
# import boto3
# from botocore.exceptions import ClientError

# S3_BUCKET = os.getenv("S3_BUCKET", "my-pdf-bucket")
# S3_REGION = os.getenv("AWS_REGION", "us-east-1")
# S3_CLIENT = boto3.client("s3")


# --------------------------
# API functions for both backends
# --------------------------

# def save_file(file_path: str, doc_id: str) -> str:
#     """
#     Save file to the chosen backend (GridFS or S3).
#     Returns a file_id (GridFS ObjectId or S3 key).
#     """
#     if STORAGE_BACKEND == "gridfs":
#         with open(file_path, "rb") as f:
#             file_id = fs.put(f, filename=os.path.basename(file_path), doc_id=doc_id)
#         documents_collection.update_one(
#             {"_id": doc_id},
#             {"$set": {"file_id": str(file_id), "file_stored": True, "storage": "gridfs"}}
#         )
#         return str(file_id)

#     elif STORAGE_BACKEND == "s3":
#         key = f"{doc_id}/{os.path.basename(file_path)}"
#         try:
#             S3_CLIENT.upload_file(file_path, S3_BUCKET, key)
#             documents_collection.update_one(
#                 {"_id": doc_id},
#                 {"$set": {"file_id": key, "file_stored": True, "storage": "s3"}}
#             )
#             return key
#         except ClientError as e:
#             raise RuntimeError(f"Failed to upload to S3: {e}")

#     else:
#         raise ValueError(f"Unsupported STORAGE_BACKEND: {STORAGE_BACKEND}")


# def get_file(file_id: str) -> bytes:
#     """Retrieve file content from the chosen backend."""
#     if STORAGE_BACKEND == "gridfs":
#         gridout = fs.get(ObjectId(file_id))
#         return gridout.read()

#     elif STORAGE_BACKEND == "s3":
#         try:
#             response = S3_CLIENT.get_object(Bucket=S3_BUCKET, Key=file_id)
#             return response["Body"].read()
#         except ClientError as e:
#             raise RuntimeError(f"Failed to download from S3: {e}")

#     else:
#         raise ValueError(f"Unsupported STORAGE_BACKEND: {STORAGE_BACKEND}")


# def delete_file(file_id: str) -> None:
#     """Delete file from the chosen backend."""
#     if STORAGE_BACKEND == "gridfs":
#         fs.delete(ObjectId(file_id))
#         documents_collection.update_one(
#             {"file_id": file_id}, {"$unset": {"file_id": "", "file_stored": ""}}
#         )

#     elif STORAGE_BACKEND == "s3":
#         try:
#             S3_CLIENT.delete_object(Bucket=S3_BUCKET, Key=file_id)
#             documents_collection.update_one(
#                 {"file_id": file_id}, {"$unset": {"file_id": "", "file_stored": ""}}
#             )
#         except ClientError as e:
#             raise RuntimeError(f"Failed to delete from S3: {e}")

#     else:
#         raise ValueError(f"Unsupported STORAGE_BACKEND: {STORAGE_BACKEND}")
