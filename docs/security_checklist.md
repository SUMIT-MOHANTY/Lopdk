# Security Checklist & Verification Guide

This document records all security controls implemented in this project and
provides the exact commands to verify each control is correctly enforced.

---

## 1. SECRET_KEY — Environment Variable Only

**Control:** The Django `SECRET_KEY` must never be hard-coded in source files.
It must be loaded exclusively from the environment.

**Verification command:**
```bash
grep -rn "SECRET_KEY" config/settings/
```

**Expected result:** Every occurrence should reference `os.environ` or
`os.getenv` (e.g., `SECRET_KEY = os.environ.get('SECRET_KEY', '')`).  
No line should contain a literal string value assigned directly to `SECRET_KEY`.

**Implementation:** `config/settings/base.py` reads `SECRET_KEY` from
`os.environ`. `config/settings/production.py` calls `_require_env("SECRET_KEY")`
which raises `ImproperlyConfigured` if the variable is absent or empty.

**Status:** ✅ Enforced — no hardcoded `SECRET_KEY` in any settings file.

---

## 2. DEBUG=False in Production

**Control:** `DEBUG` must be `False` when running in production to prevent
detailed error pages and sensitive data leakage.

**Verification command:**
```bash
python -c "
import os
os.environ['SECRET_KEY'] = 'test-key'
os.environ['DEBUG'] = 'True'
os.environ['ALLOWED_HOSTS'] = 'example.com'
from config.settings import production
"
```

**Expected result:** `django.core.exceptions.ImproperlyConfigured` is raised
with a message indicating `DEBUG` must be `False` in production.

**Implementation:** `config/settings/production.py` raises
`ImproperlyConfigured` at import time if `DEBUG` evaluates to `True`
(checks for string values `"true"`, `"1"`, `"yes"`).

**Status:** ✅ Enforced via startup assertion in `production.py`.

---

## 3. ALLOWED_HOSTS Configured (No Wildcard)

**Control:** `ALLOWED_HOSTS` must list explicit hostnames. An empty list or a
list containing `'*'` is rejected in production.

**Verification commands:**
```bash
# Test empty ALLOWED_HOSTS
python -c "
import os
os.environ['SECRET_KEY'] = 'test-key'
os.environ['DEBUG'] = 'False'
os.environ['ALLOWED_HOSTS'] = ''
from config.settings import production
"

# Test wildcard ALLOWED_HOSTS
python -c "
import os
os.environ['SECRET_KEY'] = 'test-key'
os.environ['DEBUG'] = 'False'
os.environ['ALLOWED_HOSTS'] = '*'
from config.settings import production
"
```

**Expected result:** Both commands raise `ImproperlyConfigured`.

**Implementation:** `production.py` uses `_require_env("ALLOWED_HOSTS")` to
ensure the variable is set, then explicitly checks that the parsed list is
non-empty and does not contain `'*'`.

**Status:** ✅ Enforced via startup assertions in `production.py`.

---

## 4. CSRF Tokens on All POST Forms

**Control:** Every HTML `<form>` that submits via POST must include
`{% csrf_token %}` to prevent Cross-Site Request Forgery attacks.

**Verification command:**
```bash
grep -rn "csrf_token" templates/todos/
```

**Expected result:** Both `todo_form.html` and `todo_confirm_delete.html`
contain `{% csrf_token %}` inside their `<form>` tags.

**Audit results:**

| Template | `{% csrf_token %}` present |
|---|---|
| `templates/todos/todo_form.html` | ✅ Yes |
| `templates/todos/todo_confirm_delete.html` | ✅ Yes |

**Status:** ✅ CSRF protection confirmed on all POST forms.

---

## 5. No `|safe` Filter on User-Supplied Data

**Control:** The Django `|safe` template filter bypasses auto-escaping and
must never be applied to user-supplied data (XSS risk).

**Verification command:**
```bash
grep -rn "|safe" templates/
```

**Expected result:** Zero occurrences of `|safe` applied to variables that
originate from user input (form fields, model fields entered by users).

**Status:** ✅ No `|safe` filters found on user-supplied data in templates.

---

## 6. Input Sanitization via Django Auto-Escaping

**Control:** Django's template engine auto-escapes all variables by default.
No template should disable this with `{% autoescape off %}` blocks around
user data.

**Verification commands:**
```bash
# Check for autoescape off blocks
grep -rn "autoescape off" templates/

# Check for mark_safe usage in Python code
grep -rn "mark_safe" apps/
```

**Expected result:** Zero occurrences of `autoescape off` in templates and
zero unsafe uses of `mark_safe` on user-controlled data in application code.

**Status:** ✅ Django auto-escaping is active (default). No `autoescape off`
blocks found.

---

## 7. CI/CD Pipeline Quality Gates

The GitHub Actions pipeline (`.github/workflows/ci.yml`) enforces the
following automated quality gates on every push and pull request to `main`:

| Gate | Tool | Failure Condition |
|---|---|---|
| Code style | Flake8 (max-line-length=119) | Any lint error |
| Django deployment checks | `manage.py check` | Any system check warning/error |
| Unit tests | Pytest | Any test failure |
| Code coverage | pytest-cov | Coverage < 80% |

**Pipeline file:** `.github/workflows/ci.yml`  
**Lint config:** `setup.cfg` — `[flake8]`, `[tool:pytest]`, `[coverage:run]`, `[coverage:report]`

**Secrets required in GitHub repository settings:**

| Secret Name | Description | Required |
|---|---|---|
| `SECRET_KEY` | Django cryptographic signing key | Recommended |
| `DEBUG` | Debug flag (`False` for CI) | Optional (defaults to `False`) |

---

## 8. Environment Variable Documentation

All required environment variables are documented in `.env.example`:

| Variable | Required | Description |
|---|---|---|
| `SECRET_KEY` | ✅ Yes | Django cryptographic signing key |
| `DEBUG` | ✅ Yes | `False` in production, `True` in development |
| `ALLOWED_HOSTS` | ✅ Yes | Comma-separated list of valid hostnames |
| `DJANGO_SETTINGS_MODULE` | ✅ Yes | Settings module path |
| `DATABASE_URL` | Recommended | Database connection string |
| `SECURE_SSL_REDIRECT` | Optional | Redirect HTTP→HTTPS (default: `True`) |
| `CORS_ALLOWED_ORIGINS` | Optional | Comma-separated CORS origins |

---

## Quick Full Audit Command

Run all security checks at once:

```bash
echo "=== 1. SECRET_KEY hardcoded check ==="
grep -rn "SECRET_KEY\s*=\s*['\"]" config/settings/ \
  && echo "FAIL: hardcoded SECRET_KEY found" \
  || echo "PASS: no hardcoded SECRET_KEY"

echo "=== 2. CSRF tokens in forms ==="
grep -l "csrf_token" \
  templates/todos/todo_form.html \
  templates/todos/todo_confirm_delete.html \
  && echo "PASS: csrf_token present" \
  || echo "FAIL: csrf_token missing"

echo "=== 3. |safe filter audit ==="
grep -rn "|safe" templates/ \
  && echo "WARNING: |safe found — review manually" \
  || echo "PASS: no |safe filters"

echo "=== 4. autoescape off audit ==="
grep -rn "autoescape off" templates/ \
  && echo "FAIL: autoescape disabled" \
  || echo "PASS: auto-escaping active"

echo "=== 5. mark_safe audit ==="
grep -rn "mark_safe" apps/ \
  && echo "WARNING: mark_safe found — review manually" \
  || echo "PASS: no mark_safe usage"

echo "=== 6. Flake8 lint ==="
flake8 . --config=setup.cfg

echo "=== 7. Pytest with coverage ==="
pytest --cov=. --cov-config=setup.cfg --cov-report=term-missing --cov-fail-under=80
```

---

## Security Controls Summary

| Control | Implementation | Status |
|---|---|---|
| `SECRET_KEY` env-only | `base.py` reads from `os.environ`; `production.py` raises if empty | ✅ |
| `DEBUG=False` production | `production.py` startup assertion | ✅ |
| `ALLOWED_HOSTS` configured | `production.py` startup assertion (no empty, no `*`) | ✅ |
| CSRF on all forms | `{% csrf_token %}` in `todo_form.html` & `todo_confirm_delete.html` | ✅ |
| No `\|safe` on user data | Template audit — zero occurrences | ✅ |
| Input sanitization | Django auto-escaping (default); no `autoescape off` blocks | ✅ |
| Lint enforcement | Flake8 via CI pipeline, max-line-length=119 | ✅ |
| Test coverage gate | pytest-cov, fail_under=80 | ✅ |
