# CyberCart — Deep-Link Security Workshop

A deliberately simple fake e-commerce application intended as a local cybersecurity workshop lab.

## Stack

- Frontend: SvelteKit + TypeScript
- Backend: FastAPI + SQLAlchemy + PostgreSQL/Supabase
- Fake OAuth provider: FastAPI
- Attacker/demo site: FastAPI
- Containerization: Docker Compose

## Safety

This project is designed to run locally. It contains intentionally incomplete security controls so workshop organizers can add isolated vulnerabilities.

Do not connect it to real OAuth providers, real payment systems, real credentials, or production databases. The deliberately vulnerable routes are for a local workshop only.

## Task 3 — My Orders and IDOR

The application seeds 120 participants (`1001` through `1120`). Each participant has an opaque, randomly generated login token and two to five orders with sequential IDs. Login tokens are exchanged for an HTTP-only session cookie; orders endpoints require that session.

The regular order list is correctly scoped to the current participant:

```text
GET /api/orders
```

The individual order endpoint supports two workshop modes:

| URL | Behaviour |
| --- | --- |
| `GET /api/orders/{order_id}` | **Intentional IDOR.** It loads by the supplied sequential order ID without verifying that the order belongs to the logged-in participant. |
| `GET /api/orders/{order_id}?strict_authz=true` | Demonstrates the fix. It returns `404` when the requested order belongs to another participant. |

The Svelte routes mirror this API:

```text
/orders
/orders/{order_id}
/orders/{order_id}?strict_authz=true
```

Order detail shows the participant ID, status, total, shipping address, and items. This makes the cross-participant access clear during the workshop.

`strict_authz` is intentionally an explicit query parameter for side-by-side comparison. The default remains vulnerable, which is the required Task 3 workshop behavior. This IDOR comparison is independent of PKCE; PKCE belongs to the separate OAuth workshop flow.

## Run locally

### Backend

```bash
cd /Users/ann.gracia/DeepLinks-Workshop-/backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Create a local configuration file and add the workshop database URL. Do not commit this file.

```bash
cp .env.example .env
```

At minimum, set `DATABASE_URL` to the supplied PostgreSQL/Supabase connection URL. For local HTTP development, use:

```env
SESSION_COOKIE_SAMESITE=lax
SESSION_COOKIE_SECURE=false
```

Start the API with the virtual environment's Python so it uses the packages just installed:

```bash
python -m uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd /Users/ann.gracia/DeepLinks-Workshop-/frontend
npm install
npm run dev
```

The starter frontend expects the API at `http://localhost:8000`.

## Test the IDOR workshop flow

With the backend running, generate local login links:

```bash
cd /Users/ann.gracia/DeepLinks-Workshop-/backend
source .venv/bin/activate
python -m app.export_logins
```

This creates a local, Git-ignored `participant_logins.csv` file. It contains active workshop login tokens, so do not share or commit it.

1. Open participant 1002's login URL from the CSV and note one of their order IDs on `/orders`.
2. Open participant 1001's login URL. Their `/orders` list contains only their own orders.
3. As participant 1001, visit `/orders/{1002-order-id}`. The page displays participant `#1002`'s order: this is the intentional IDOR.
4. Visit `/orders/{1002-order-id}?strict_authz=true`. The page returns **Order not found**, demonstrating the ownership check.
5. Visit `/orders/{1001-order-id}?strict_authz=true`. The current participant's own order still loads.

## Automated tests

Install the test-only dependency and run the backend suite:

```bash
cd /Users/ann.gracia/DeepLinks-Workshop-/backend
source .venv/bin/activate
python -m pip install -r requirements-test.txt
python -m unittest discover -s tests
```

The order tests use an isolated SQLite test database and cover:

- authenticated, participant-scoped order listing;
- unauthenticated rejection;
- own-order retrieval and nonexistent-order `404` responses;
- expected cross-participant access in vulnerable mode;
- cross-participant denial and own-order access in `strict_authz=true` mode.

### OAuth demo server

```bash
cd oauth-server
python -m venv .venv
# activate it
pip install -r requirements.txt
uvicorn app.main:app --reload --port 9000
```

## Suggested lab order

1. Deep-link fundamentals
2. Reflected XSS
3. IDOR
4. OAuth redirect handling
5. Authorization-code exchange
6. PKCE
7. Agentic navigation and link validation

The starter project keeps workshop vulnerabilities isolated by task. This checkout includes the Task 3 IDOR demonstration and its strict-mode comparison; merge other task branches without replacing the shared authentication, database, or route structure.
