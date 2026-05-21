from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from database import get_db
import os

router = APIRouter()

ADMIN_TOKEN = os.environ.get("ADMIN_TOKEN", "changeme")


def require_auth(x_admin_token: str = Header(...)):
    if x_admin_token != ADMIN_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized")


class DocumentIn(BaseModel):
    sku:      str
    label:    str
    doc_type: str = "Document"
    s3_url:   str


class DocumentUpdate(BaseModel):
    label:    str | None = None
    doc_type: str | None = None
    s3_url:   str | None = None


@router.get("/documents")
def list_documents(sku: str | None = None, x_admin_token: str = Header(...)):
    require_auth(x_admin_token)
    with get_db() as conn:
        if sku:
            rows = conn.execute(
                "SELECT * FROM documents WHERE sku = ? ORDER BY sku, doc_type, label", (sku,)
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM documents ORDER BY sku, doc_type, label"
            ).fetchall()
    return [dict(r) for r in rows]


@router.post("/documents", status_code=201)
def add_document(doc: DocumentIn, x_admin_token: str = Header(...)):
    require_auth(x_admin_token)
    with get_db() as conn:
        cur = conn.execute(
            "INSERT INTO documents (sku, label, doc_type, s3_url) VALUES (?, ?, ?, ?)",
            (doc.sku, doc.label, doc.doc_type, doc.s3_url)
        )
        conn.commit()
        return {"id": cur.lastrowid, **doc.dict()}


@router.patch("/documents/{doc_id}")
def update_document(doc_id: int, updates: DocumentUpdate, x_admin_token: str = Header(...)):
    require_auth(x_admin_token)
    fields = {k: v for k, v in updates.dict().items() if v is not None}
    if not fields:
        raise HTTPException(status_code=400, detail="No fields to update")
    set_clause = ", ".join(f"{k} = ?" for k in fields)
    with get_db() as conn:
        conn.execute(
            f"UPDATE documents SET {set_clause} WHERE id = ?",
            (*fields.values(), doc_id)
        )
        conn.commit()
    return {"updated": doc_id}


@router.delete("/documents/{doc_id}")
def delete_document(doc_id: int, x_admin_token: str = Header(...)):
    require_auth(x_admin_token)
    with get_db() as conn:
        conn.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
        conn.commit()
    return {"deleted": doc_id}
