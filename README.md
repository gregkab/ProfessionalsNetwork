# Professionals Network Prototype

A small full-stack application for unifying professional sign-ups from multiple sources (direct, partner, internal). Built with **Django REST Framework** and **React + Vite**.

---

## Setup Instructions

### Prerequisites

- Python 3.12+
- Node.js 20.19+ (or 22.12+)
- npm 9+

### Backend

```bash
# From the project root
python -m venv .venv
source .venv/bin/activate        # macOS/Linux
# .venv\Scripts\activate         # Windows

pip install -r requirements.txt

cd backend
python manage.py migrate
python manage.py runserver       # → http://localhost:8000
```

### Frontend

```bash
# From the project root
cd frontend
npm install
npm run dev                      # → http://localhost:5173
```

Open http://localhost:5173 in your browser. The frontend communicates with the Django API at http://localhost:8000.

---

## API Endpoints

| Method | URL                         | Description                                      |
| ------ | --------------------------- | ------------------------------------------------ |
| GET    | `/api/professionals/`       | List all professionals (optional `?source=` filter) |
| POST   | `/api/professionals/`       | Create a single professional                     |
| POST   | `/api/professionals/bulk/`  | Bulk create/update (upsert by email, then phone) |

### Single Create — `POST /api/professionals/`

```json
{
  "full_name": "Jane Doe",
  "email": "jane@example.com",
  "phone": "555-0100",
  "job_title": "Engineer",
  "company_name": "Acme Inc.",
  "source": "direct"
}
```

### Bulk Upsert — `POST /api/professionals/bulk/`

```json
[
  { "full_name": "Jane Doe", "email": "jane@example.com", "source": "partner" },
  { "full_name": "John Smith", "phone": "555-0200", "source": "internal" }
]
```

Returns per-item results with status `created`, `updated`, or `error` to support partial success.

---

## Assumptions & Trade-offs

- **SQLite** is used for simplicity. In production, swap to PostgreSQL.
- **CORS** is fully open (`CORS_ALLOW_ALL_ORIGINS = True`) for local development convenience.
- **Email and phone** are each unique but individually nullable. At least one must be provided per professional.
- The **bulk endpoint** processes items sequentially to guarantee per-record error isolation. For very large batches, this could be optimized with `bulk_create` / `bulk_update` and database transactions.
- **No authentication** is implemented — this is a prototype.
- The frontend uses simple tab-based navigation rather than a router, keeping the prototype lightweight.
- **Naming: `phone` vs `phone_number`** — the prompt uses `phone_number` in the bulk endpoint description but `phone` in the model spec. I used `phone` consistently across all endpoints and the model for simplicity.
- **Phone uniqueness** — the model spec doesn't explicitly mark `phone` as unique, but the single-create endpoint spec requires unique phone validation, and the bulk endpoint uses phone as a fallback upsert key (which implies uniqueness). I added a unique constraint on `phone` to satisfy both requirements.

---

## PDF Resume Extension — Design Considerations

### How would the system process and interpret the content of the uploaded PDF?

Use a Python PDF extraction library like **pdfplumber** or **PyPDF2** to pull raw text from the uploaded file. The extracted text can then be fed through:

1. **Regex / heuristic parsing** — look for patterns like email addresses, phone numbers, section headers ("Experience", "Education").
2. **LLM-based extraction** — send the raw text to a language model (e.g., OpenAI API) with a structured prompt asking it to return JSON with fields like `full_name`, `email`, `phone`, `job_title`, `company_name`. This gives better accuracy on varied resume formats.

A two-pass approach (heuristics for high-confidence fields, LLM for the rest) balances cost and accuracy.

### What is the proposed method for handling the actual file upload?

- Add a `resume` `FileField` to the `Professional` model (or a separate `Resume` model linked via FK).
- The POST endpoint accepts `multipart/form-data` instead of (or in addition to) JSON.
- Store the file on disk (`MEDIA_ROOT`) for development, or on S3 / cloud storage in production.
- Processing can happen synchronously for small files, or be offloaded to a task queue (Celery) for larger workloads.

### What additional functionalities or elements would be incorporated into the frontend?

- **File input / drag-and-drop zone** on the Add Professional form.
- **Preview step** — after upload, show extracted fields for the user to review and correct before final submission.
- **Progress indicator** during upload and processing.
- A link to download / view the original PDF from the professionals list table.

---

## Tests

The backend includes 23 tests organized into separate modules covering all three endpoints and the model layer:

```bash
cd backend
python manage.py test professionals -v2
```

Coverage includes: model validation and ordering, single create (success, email-only, phone-only, duplicate email/phone, invalid source, missing required fields), list (all, filtered, empty filter, response field completeness), and bulk (create, upsert-by-email, upsert-by-phone-fallback, email-priority over phone, partial success, empty list, invalid input).

---

## Estimated Time Spent

Approximately 2 hours, including backend API, frontend UI, tests, and documentation.

---

## What I'd Improve With More Time

- Add pagination to the professionals list endpoint and table.
- Implement proper form validation with inline field errors on the frontend.
- Add frontend tests (Vitest + React Testing Library).
- Use React Router for proper URL-based navigation.
- Add authentication and permissions.
- Containerize with Docker Compose for one-command setup.
