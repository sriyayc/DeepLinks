# CyberCart — Deep-Link Security Workshop

A deliberately simple fake e-commerce application intended as a local cybersecurity workshop lab.

## Stack

- Frontend: SvelteKit + TypeScript
- Backend: FastAPI + SQLite + Supabase
- Fake OAuth provider: FastAPI
- Attacker/demo site: FastAPI
- Containerization: Docker Compose

## Safety

This project is designed to run locally. It contains intentionally incomplete security controls so workshop organizers can add isolated vulnerabilities.

Do not connect it to real OAuth providers, real payment systems, real credentials, or production databases.

## Run locally

### Backend

```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend

Create a SvelteKit app in `frontend/` using the official SvelteKit scaffold, then copy the provided `frontend/src` files into it:

```bash
npm create svelte@latest frontend
cd frontend
npm install
npm run dev
```

The starter frontend expects the API at `http://localhost:8000`.

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

The base project intentionally does **not** implement the vulnerabilities. Add each lab as a separate, clearly marked workshop mode.
