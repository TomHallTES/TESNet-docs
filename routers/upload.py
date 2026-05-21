from fastapi import APIRouter, UploadFile, File, Form, Header, HTTPException
from database import get_db
from s3 import upload_file_to_s3
import os

router = APIRouter()

ADMIN_TOKEN = os.environ.get("ADMIN_TOKEN", "changeme")
ALLOWED_TYPES = {"application/pdf", "application/octet-stream"}


def require_auth(x_admin_token: str):
    if x_admin_token != ADMIN_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized")


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    sku: str = Form(...),
    label: str = Form(...),
    doc_type: str = Form("Document"),
    x_admin_token: str = Header(...),
):
    require_auth(x_admin_token)

    contents = await file.read()
    if len(contents) > 20 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large (max 20MB)")

    url = upload_file_to_s3(contents, file.filename or "document.pdf", "application/pdf")

    with get_db() as conn:
        cur = conn.execute(
            "INSERT INTO product_documents (sku, label, doc_type, url) VALUES (?, ?, ?, ?)",
            (sku.strip(), label.strip(), doc_type.strip(), url)
        )
        conn.commit()

    return {"id": cur.lastrowid, "sku": sku, "label": label, "doc_type": doc_type, "url": url}
