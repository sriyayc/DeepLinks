# Task: Admin Dashboard — broken access control / privilege escalation

CyberCart includes a hidden admin panel at `/admin` that lists every registered user. The endpoint checks that the caller is authenticated but **does not verify that they hold the `admin` role** — any logged-in participant can read the full user list.

## Discovery

1. Open `http://localhost:5173/` in a browser.
2. Right-click → **View Page Source** (or press `Ctrl+U` / `Cmd+U`).
3. Near the bottom of the HTML you will find:

   ```html
   <!-- TODO: remove before launch — /admin -->
   ```

4. Navigate to `http://localhost:5173/admin` to open the admin dashboard.

## Exploitation

Any participant with a valid session cookie can call the API directly. Log in as any non-admin user (e.g. participant 1010) and then:

```bash
# 1. Authenticate and capture the session cookie
curl -c cookies.txt "http://localhost:8000/api/login?token=<participant-1010-token>"

# 2. Access the admin endpoint — succeeds despite not being an admin
curl -b cookies.txt http://localhost:8000/api/admin/users
```

The response contains every user's ID, display name, generated email, and role — including which accounts are admins (IDs 1001, 1002, 1003).

## The vulnerability

In `backend/app/routes/admin.py`, the endpoint uses `Depends(get_current_user)` to confirm the session is valid but performs **no role check**:

```python
@router.get("/users")
def list_all_users(
    ...
    user: Participant = Depends(get_current_user),
):
    # No check that user.role == "admin"
    ...
```

This is a textbook **Broken Access Control** (OWASP A01:2021) / **privilege escalation** issue: authentication ≠ authorization.

## Fix toggle

Append `?strict_authz=true` to enable the role check — the same query-parameter pattern used in the IDOR lab (`/api/orders/{id}?strict_authz=true`).

```bash
# Non-admin → 403
curl -b cookies.txt "http://localhost:8000/api/admin/users?strict_authz=true"
# {"detail":"Admin access required"}

# Admin (e.g. participant 1001) → 200
curl -b admin-cookies.txt "http://localhost:8000/api/admin/users?strict_authz=true"
```

When `strict_authz=true`, the endpoint returns **403 Admin access required** for any user whose `role` is not `"admin"`.

## Admin accounts

The following seeded participants have `role = "admin"`:

| ID   | Display name    |
|------|-----------------|
| 1001 | participant1001 |
| 1002 | participant1002 |
| 1003 | participant1003 |

All other participants (1004–1120) remain `role = "participant"`.

## Validation

New tests (from `backend/`):

```bash
DATABASE_URL=sqlite:// .venv/bin/python -m unittest discover -s tests -p 'test_admin.py'
```

Existing test suites should continue to pass unchanged:

```bash
DATABASE_URL=sqlite:// .venv/bin/python -m unittest discover -s tests -p 'test_orders.py'
DATABASE_URL=sqlite:// .venv/bin/python -m unittest discover -s tests -p 'test_search.py'
```
