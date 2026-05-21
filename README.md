# Tesnet Docs Widget

Injects a **Documents** tab into BigCommerce product pages, pulling files from AWS S3 via a FastAPI backend.

---

## Stack

| Layer     | Tech                        |
|-----------|-----------------------------|
| Backend   | FastAPI + SQLite            |
| Storage   | AWS S3 (pre-signed URLs)    |
| Hosting   | Railway                     |
| Frontend  | Vanilla JS widget           |

---

## Local Development

```bash
pip install -r requirements.txt
python -c "from database import init_db; init_db()"  # initialise DB
uvicorn main:app --reload
```

The API will be at `http://localhost:8000`.  
Interactive docs at `http://localhost:8000/docs`.

---

## Deploying to Railway

1. Push this repo to GitHub.
2. Create a new Railway project → **Deploy from GitHub repo**.
3. Set the following environment variables in Railway:

| Variable     | Description                                  |
|--------------|----------------------------------------------|
| `ADMIN_TOKEN`| Secret token for the admin API               |
| `DB_PATH`    | Path to your SQLite file (default: `docs.db`)|

4. In Railway, add a **Volume** and mount it at `/data`, then set `DB_PATH=/data/docs.db`.  
   This persists your database across deploys.

5. Upload your existing `docs.db` to the volume via the Railway CLI:
   ```bash
   railway run -- cp /path/to/your/docs.db /data/docs.db
   ```

6. Once deployed, copy your Railway public URL (e.g. `https://your-app.railway.app`).

---

## Update widget.js

Open `static/widget.js` and update line 5:

```js
const API_BASE = "https://your-app.railway.app"; // ← replace with your Railway URL
```

Then redeploy.

---

## BigCommerce — product.html snippet

These two lines should already be present in your theme's `product.html`:

```html
<div id="tesnet-docs" data-sku="{{product.sku}}" style="display:none"></div>
<script async src="https://your-app.railway.app/static/widget.js"></script>
```

Update the script `src` to your new Railway URL.

---

## Admin API

All admin endpoints require the header: `X-Admin-Token: <your ADMIN_TOKEN>`

| Method | Endpoint                  | Description              |
|--------|---------------------------|--------------------------|
| GET    | `/admin/documents`        | List all documents       |
| GET    | `/admin/documents?sku=X`  | Filter by SKU            |
| POST   | `/admin/documents`        | Add a document           |
| PATCH  | `/admin/documents/{id}`   | Update a document        |
| DELETE | `/admin/documents/{id}`   | Delete a document        |

### Add a document (example)

```bash
curl -X POST https://your-app.railway.app/admin/documents \
  -H "X-Admin-Token: changeme" \
  -H "Content-Type: application/json" \
  -d '{
    "sku": "ABC-123",
    "label": "ABC-123 Data Sheet",
    "doc_type": "Data Sheet",
    "s3_url": "https://your-bucket.s3.amazonaws.com/docs/abc-123-datasheet.pdf"
  }'
```

### Supported `doc_type` values

- Data Sheet
- Manual
- Certificate
- Drawing
- Brochure
- Installation
- Compliance
- Document *(fallback)*
