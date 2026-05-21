from fastapi import APIRouter, HTTPException
from database import get_db

router = APIRouter()

# Map doc_type strings to icon CSS classes (Font Awesome)
ICON_MAP = {
    "Data Sheet":       "fa-file-pdf",
    "Manual":           "fa-book",
    "Certificate":      "fa-certificate",
    "Drawing":          "fa-drafting-compass",
    "Brochure":         "fa-newspaper",
    "Installation":     "fa-tools",
    "Compliance":       "fa-shield-alt",
    "Document":         "fa-file-alt",
}


@router.get("/docs")
def get_docs(sku: str):
    if not sku:
        raise HTTPException(status_code=400, detail="SKU is required")

    with get_db() as conn:
        rows = conn.execute(
            "SELECT label, doc_type, url FROM product_documents WHERE sku = ? ORDER BY doc_type, label",
            (sku,)
        ).fetchall()

    if not rows:
        return {"sku": sku, "documents": []}

    documents = [
        {
            "label":    row["label"],
            "doc_type": row["doc_type"],
            "icon":     ICON_MAP.get(row["doc_type"], "fa-file-alt"),
            "url":      row["url"],
        }
        for row in rows
    ]

    return {"sku": sku, "documents": documents}
