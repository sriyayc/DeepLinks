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

Any participant with a valid session cookie can access the admin dashboard directly in their browser. 

1. Log in to the application as any non-admin user (e.g., participant 1010).
2. Based on the HTML comment you discovered in the previous step, manually type `http://localhost:5173/admin` into your browser's address bar.
3. The page loads successfully and displays the hidden dashboard, proving you have bypassed the role restriction!

The response contains every user's ID, display name, generated email, and role — including which account is the admin (ID 1000).

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

To see the fix in action, the backend supports a `?strict_authz=true` parameter. You can test this via the raw API in your browser:

1. While logged in as your non-admin user, navigate to `http://localhost:8000/api/admin/users?strict_authz=true`.
   You will receive a **403 Forbidden** response (`{"detail":"Admin access required"}`).
2. Now log in as the actual admin (user `1000`).
3. Navigate to the same URL: `http://localhost:8000/api/admin/users?strict_authz=true`.
   The request successfully returns the data.

When `strict_authz=true`, the endpoint returns **403 Admin access required** for any user whose `role` is not `"admin"`.

## Admin accounts

The following seeded participant has `role = "admin"`:

| ID   | Display name |
|------|--------------|
| 1000 | admin        |

All other participants (1001–1150) remain `role = "participant"`.

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
