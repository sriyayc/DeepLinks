# Task 2: search and reflected XSS

Search from `/products` or `/search`. Matching is case-insensitive across product names. An empty query lists everything. Results are ordered by ID and paginated six at a time in the frontend; pagination retains the query and workshop mode, and a new search resets the page. Database calls remain parameterized; `%` and `_` are literal search characters.

The product catalog also offers Books, Electronics, and Accessories filters. The selected category is stored in the `category` URL parameter, and choosing a category resets pagination to its first page. Categories are fixed presentation metadata in `backend/app/catalog.py`, so this task does not require a database migration or disturb the shared product schema.

## Local demonstration

1. Open `http://localhost:5173/search`.
2. Search for `python` to check normal search.
3. Enter `<script>alert('XSS demo')</script>` and submit. The default vulnerable mode triggers an alert.
4. Dismiss it, then add `&safe=true` to the URL. The same payload appears as text without executing.
5. Search for `headphones` in fixed mode to confirm subsequent searches keep `safe=true`.

Another harmless payload is `<img src="/missing-xss-demo.png" onerror="alert('XSS demo')">`. Use fictional local workshop data. These demos do not collect or transmit tokens.

## Why it works

`frontend/src/routes/search/+page.server.ts` reads the URL query and fetches matching products from FastAPI. The vulnerable branch of `+page.svelte` deliberately uses `{@html data.query}` to insert untrusted HTML into the initial document. Forms and mode/pagination links use full document navigation so script tags execute reproducibly rather than depending on client-side HTML update behavior.

The fixed branch uses `{data.query}`, which Svelte escapes. Only the query reflection is intentionally unsafe; product names, descriptions, input values, and generated links retain normal framework escaping. The comparison is intentionally hidden from the shopping interface so the site looks authentic. Organizers can add `safe=true` to the URL during the explanation. This parameter is a demo comparison, not a production security boundary: a deployed fixed version must remove the unsafe branch entirely.

## Validation

Build: `cd frontend && npm run build`.

Backend regressions (from `backend`): `DATABASE_URL=sqlite:// .venv/bin/python -m unittest discover -s tests -p 'test_search.py'`. These checks use isolated SQLite data, not the preview or Supabase.
