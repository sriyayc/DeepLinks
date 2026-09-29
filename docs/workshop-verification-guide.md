# CyberCart Workshop — Complete Verification Guide

> **You're a participant, not a developer.** This guide walks you through every lab step-by-step using your browser and a handful of simple commands. No coding experience needed.

---

## 🚀 Before You Start

### 1. Get your login link

Each participant has a unique login URL. Your instructor will share a CSV file or paste your link directly. It looks like this:

```
http://localhost:5173/login?token=abc123...
```

Just open that URL in your browser — you're instantly logged in. No password needed.

### 2. Confirm you're logged in

Go to **http://localhost:5173**

You should see **Logout** in the top-right corner (not "Login"). If you still see "Login", click your login link again.

---

## Lab 1 — 🔍 Reflected XSS (Search)

**What is it?** The search bar injects your input directly into the page as raw HTML, allowing scripts to run.

### Step 1 — Normal search

Go to **http://localhost:5173/search**

Search for: `python`

✅ You should see matching products listed normally.

### Step 2 — Trigger the vulnerability

Clear the search box and type this exactly, then press Enter:

```
<script>alert('XSS demo')</script>
```

✅ A pop-up alert should appear — **that's the XSS vulnerability!**

### Step 3 — See the fix

Dismiss the alert. Now add `&safe=true` to the URL so it looks like:

```
http://localhost:5173/search?q=<script>alert('XSS demo')</script>&safe=true
```

✅ The same input now appears as plain text — no alert. The `safe=true` flag enables the fix.

---

## Lab 2 — 🔗 IDOR (Broken Object-Level Authorization on Orders)

**What is it?** You can read **any** participant's order just by changing the order ID in the URL — the server doesn't check if it's yours.

### Step 1 — View your own orders

Go to **http://localhost:5173/orders**

You'll see a list of your orders with their IDs (e.g. `Order #42`).

### Step 2 — Access someone else's order

In your browser address bar, type:

```
http://localhost:8000/api/orders/1
```

Try a few numbers: `/api/orders/1`, `/api/orders/2`, `/api/orders/100`

✅ You can read orders belonging to **other participants** — that's the IDOR vulnerability!

### Step 3 — See the fix

Add `?strict_authz=true` to the URL:

```
http://localhost:8000/api/orders/1?strict_authz=true
```

✅ You now get `404 Order not found` for orders that don't belong to you.

---

## Lab 3 — 🎭 CSRF (Cross-Site Request Forgery)

**What is it?** A malicious website can silently change your shipping address by tricking your browser into making a request with your session cookie.

### Step 1 — Check your current shipping address

Go to **http://localhost:5173/orders** and note your shipping address.

### Step 2 — Visit the attacker's site

Open a **new tab** and go to:

```
http://localhost:7001
```

This is a fake attacker-controlled page. Just visiting it is enough — it silently submits a form to the shop using your session cookie.

### Step 3 — Confirm the attack worked

Go back to **http://localhost:5173/orders** and refresh.

✅ Your shipping address has changed — **without you doing anything!** That's CSRF.

### Step 4 — Learn more

Go to **http://localhost:5173/lab/csrf** to read the workshop explanation of why this works and how to defend against it.

---

## Lab 4 — 🛡️ Admin Dashboard (Broken Access Control / Privilege Escalation)

**What is it?** There is a hidden admin panel that any logged-in user can access — even regular participants who are not admins. The server checks *who you are* (authentication) but not *what you're allowed to do* (authorization).

### Step 1 — Discover the hidden page

Go to **http://localhost:5173** (the homepage)

Right-click anywhere on the page → **View Page Source**
(or press `Cmd+U` on Mac / `Ctrl+U` on Windows)

Press `Cmd+F` / `Ctrl+F` to search for **admin**

You'll find this comment hidden in the HTML:

```html
<!-- TODO: remove before launch — /admin -->
```

✅ The developer forgot to remove this before going live — a classic recon finding!

### Step 2 — Visit the hidden admin page

Navigate to:

```
http://localhost:5173/admin
```

✅ You can see the **full list of all 150 participants** — their IDs, names, emails, and roles — **even though you're a regular participant, not an admin!**

This is broken access control. The server only checks that you're logged in, not that you have admin privileges.

### Step 3 — Exploit it directly via the API

Open a new browser tab and go to:

```
http://localhost:8000/api/admin/users
```

✅ You get the complete user list as JSON — confirming the vulnerability lives in the **server-side API**, not just the frontend UI.

### Step 4 — Identify the admin accounts

Look through the results for entries where `"role": "admin"`. You should find:

| ID   | Name  | Role  |
|------|-------|-------|
| 1000 | admin | admin |

Everyone else (IDs 1001–1150) has `"role": "participant"`.

### Step 5 — See the fix

Add `?strict_authz=true` to the API URL:

```
http://localhost:8000/api/admin/users?strict_authz=true
```

✅ You get `{"detail": "Admin access required"}` — a **403 Forbidden** response.

Now log in as the admin account (ID 1000 — your instructor will share the token) and try the same URL with `?strict_authz=true`:

```
http://localhost:8000/api/admin/users?strict_authz=true
```

✅ Admins can still access the data. The fix correctly allows admins while blocking regular participants.

---

## 🔑 Summary Table

| Lab | Vulnerability | Test URL | Fix Toggle |
|-----|--------------|----------|------------|
| XSS | Reflected Cross-Site Scripting | `/search` — enter `<script>alert('XSS')</script>` | `&safe=true` |
| IDOR | Broken Object-Level Authorization | `/api/orders/1` | `?strict_authz=true` |
| CSRF | Cross-Site Request Forgery | Visit `http://localhost:7001` while logged in | See `/lab/csrf` |
| Privilege Escalation | Broken Access Control | `/api/admin/users` or `/admin` page | `?strict_authz=true` |

---

## ❓ Troubleshooting

**"Access denied: Could not reach the API"**
→ The backend is not running. Ask your instructor to restart it.

**Page shows "Login" instead of "Logout"**
→ Your session expired or the cookie wasn't set. Visit your login link again.

**The XSS alert doesn't fire**
→ Some browsers block `<script>` tags. Try: `<img src=x onerror="alert('XSS')">`

**`/admin` shows "Loading…" forever**
→ You might not be logged in. Visit your login URL first, then retry `/admin`.

**`/api/orders/1` returns `404`**
→ Try a few different numbers (`/2`, `/5`, `/10`). Order IDs depend on the seed data.
