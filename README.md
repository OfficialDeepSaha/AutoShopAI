# Shopify AI Analytics (Monorepo)

End-to-end, chat-driven analytics for Shopify stores. This monorepo contains:
- Frontend: React + Vite + Tailwind chat UI.
- Rails API: Shopify OAuth + API gateway to the AI service.
- Python AI Service: FastAPI agent that generates ShopifyQL, queries Shopify Admin GraphQL, and explains insights using OpenAI.

## Repository Structure
- `frontend/` – Vite React app (TailwindCSS). Calls Rails API.
- `rails_api/` – Rails 7 API-only app. Handles Shopify OAuth and exposes `/api/v1/questions`.
- `python_ai_service/` – FastAPI app with `POST /ask`. Implements `AnalyticsAgent`.

---

# 1) Setup Instructions

## Prerequisites
- Node.js ≥ 18, npm
- Python ≥ 3.10, pip
- Ruby ≥ 3.2, Rails ≥ 7.1, Bundler
- PostgreSQL (for local DB) or a DATABASE_URL

## Environment Variables

### Frontend (`frontend/.env`)
- `VITE_API_URL` – Base URL for Rails API (default `http://localhost:3000`).

Example:
```
VITE_API_URL=http://localhost:3000
```

### Rails API (`rails_api/.env`)
- `SHOPIFY_API_KEY` – Shopify app API key
- `SHOPIFY_API_SECRET` – Shopify app API secret
- `AI_SERVICE_URL` – URL of the Python AI service (e.g., `http://localhost:8000`)
- `DATABASE_URL` – Postgres connection URL (optional if using local config)

Example:
```
SHOPIFY_API_KEY=your_key
SHOPIFY_API_SECRET=your_secret
AI_SERVICE_URL=http://localhost:8000
DATABASE_URL=postgresql://user:pass@localhost:5432/shopify_analytics
```

### Python AI Service (`python_ai_service/.env`)
- `OPENAI_API_KEY` – OpenAI API key

Example:
```
OPENAI_API_KEY=sk-...
```

## Install & Run (Local)

### 1. Start Python AI Service
```
cd python_ai_service
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```
- Endpoint: `POST /ask`
- Reads `OPENAI_API_KEY` from `.env`

Note on OpenAI package version
- This service uses the legacy `openai.ChatCompletion.create` API. If you install the latest `openai` Python SDK (v1+), that call will fail.
- Quick fix: pin the package to 0.28.x:
```
pip install 'openai<1'
```
- Or, refactor to the v1 client (`from openai import OpenAI; client = OpenAI(); client.chat.completions.create(...)`).

### 2. Start Rails API
```
cd rails_api
bundle install
# Configure database.yml or ensure DATABASE_URL is set
rails db:create db:migrate
# Option A: Seed a store row (edit db/seeds.rb with your domain & token)
rails db:seed
# Option B: Connect via OAuth (recommended): see "Shopify OAuth" below
rails s -p 3000
```
- Endpoints: `/shopify/oauth/install`, `/shopify/oauth/callback`, `POST /api/v1/questions`

### 3. Start Frontend
```
cd frontend
npm install
cp .env.example .env   # or create .env manually
# Ensure VITE_API_URL points to Rails (http://localhost:3000)
npm run dev
```
- Opens Vite dev server (default `http://localhost:5173`)

## Shopify OAuth (Rails)
1. Create a Shopify app and obtain API Key/Secret.
2. Set Rails env vars: `SHOPIFY_API_KEY`, `SHOPIFY_API_SECRET`.
3. Set App Callback URL to: `http://localhost:3000/shopify/oauth/callback`
4. Start Rails, then visit:
   - `http://localhost:3000/shopify/oauth/install?shop=your-store.myshopify.com`
5. After successful callback, Rails upserts a `Store` record with the access token.

Required scopes (from code):
```
read_orders, read_products, read_inventory, read_reports, read_analytics,
write_products, write_orders, write_customers, write_inventory
```

CORS: The `rack-cors` gem is present. If you see browser CORS errors, ensure it’s configured to allow requests from your Vite dev origin (e.g., `http://localhost:5173`).

Security: Use `.env` files locally and never commit secrets. Rotate any leaked credentials immediately.

---

# 2) Architecture

- Frontend (React) posts questions to Rails API.
- Rails looks up the store access token and proxies the request to the Python AI service.
- Python agent builds or selects a ShopifyQL query, calls Shopify Admin GraphQL (`shopifyqlQuery`), then asks OpenAI to generate a concise, business-friendly explanation.
- Rails returns the agent’s `answer` to the frontend for display.

Key data store: Rails `stores` table
- `shop_domain` (unique)
- `access_token`

Shopify APIs used:
- Admin GraphQL: `shopifyqlQuery` (API version `2025-10` in agent)

---

# 3) Agent Flow Description (Python `AnalyticsAgent`)

1) Parse intent and dates (`parse_request`)
- Heuristics for common queries (e.g., "top products", last 7/30 days)
- Otherwise calls OpenAI (`gpt-4o-mini`) to map question → `{ intent, since, until }`

2) Build ShopifyQL
- If intent matches a predefined report, fills a template (see `PREDEFINED_QUERIES`)
- Else uses OpenAI to generate ShopifyQL (`build_shopifyql`)

3) Execute ShopifyQL
- Calls Shopify Admin GraphQL `shopifyqlQuery` with the built query
- Handles API errors and parse errors

4) Explain
- Sends raw results + question to OpenAI to produce a concise answer
- Currency and tone rules enforced in the prompt

5) Special handler: `reorder_forecast`
- Runs two queries (sales last 30d, current inventory)
- Computes daily sell-through, 30-day forecast, and reorder qty per SKU

---

# 4) API Reference and Samples

## Rails API
- `POST /api/v1/questions`
  - Body:
    ```json
    {
      "store_id": "your-store.myshopify.com",
      "question": "Top products in the last 30 days"
    }
    ```
  - Response (example):
    ```json
    {
      "answer": "Your top products are ... (concise explanation)",
      "confidence": "high"
    }
    ```

Sample cURL:
```
curl -X POST "http://localhost:3000/api/v1/questions" \
  -H "Content-Type: application/json" \
  -d '{
    "store_id": "your-store.myshopify.com",
    "question": "Show sales trend last 30 days"
  }'
```

## Python AI Service
- `POST /ask`
  - Body:
    ```json
    {
      "shop_domain": "your-store.myshopify.com",
      "access_token": "shpat_...",
      "question": "Top products this month"
    }
    ```
  - Response (example): same shape as Rails proxy

Sample cURL:
```
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "shop_domain": "your-store.myshopify.com",
    "access_token": "shpat_...",
    "question": "Top products this month"
  }'
```

## Shopify OAuth
- Install URL: `GET /shopify/oauth/install?shop=your-store.myshopify.com`
- Callback URL: `GET /shopify/oauth/callback`

---

# 5) Optional: Architecture Diagram

```mermaid
flowchart TD
  U[User] --> F[Frontend]
  F --> R[Rails API]
  R --> P[Python AI Service]
  R --> DB[Postgres]
  P --> S[Shopify GraphQL]
  P --> O[OpenAI]
  P --> R
  R --> F
  F --> U
```

---

# 6) Dev Tips & Troubleshooting
- CORS: If the browser blocks requests from `http://localhost:5173`, configure `rack-cors` to allow that origin.
- 404 `Store not found`: Ensure OAuth completed or seed a store row containing `shop_domain` and `access_token`.
- Shopify `parseErrors`: The generated ShopifyQL may be invalid. Try a simpler or known intent (e.g., "top products"), or adjust the question.
- 401/403 from Shopify: Verify access token and scopes.
- Rate limits: Scripts that seed data include retry logic; expect delays when 429s occur.

# 7) Scripts (Optional)
- `python_ai_service/generate_sales.py` – creates mock orders via REST to help populate analytics.
- `python_ai_service/seed_store.py` – creates customers, products, and orders. Edit store domain and token before running.

Use with caution; respect rate limits and never commit real credentials.

---

# License
For internal/demo use unless otherwise specified.
