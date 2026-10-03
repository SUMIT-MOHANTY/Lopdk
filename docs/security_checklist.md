# Security Checklist & Verification Guide

This document records all security controls implemented in this project and
provides the exact commands to verify each control is correctly enforced.

---

## 1. SECRET_KEY — Environment Variable Only

**Control:** The Django `SECRET_KEY` must never be hard-coded in source files.
It must be loaded exclusively from the environment.

**Verification command:**
```bash
grep -r "SECRET_KEY" config/settings/
```

**Expected result:** Every occurrence should reference `os.environ` or
`os.getenv` (e.g., `SECRET_KEY = os.environ.get('SECRET_KEY', '')`).  
No line should contain a literal string value assigned directly to `SECRET_KEY`.

**Status:** ✅ Enforced in `config/settings/base.py` via `os.environ`.

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
with the message *"DEBUG is set to True"*.

**Implementation:** `config/settings/production.py` raises
`ImproperlyConfigured` at import time if `DEBUG` evaluates to `True`.

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
No template should disable this with `{% autoescape off %}` or use
`{% autoescape off %}` blocks around user data.

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
| Django deployment checks | `manage.py check --deploy` | Any system check warning/error |
| Unit tests | Pytest | Any test failure |
| Code coverage | pytest-cov | Coverage < 80% |

**Pipeline file:** `.github/workflows/ci.yml`  
**Lint config:** `setup.cfg` — `[flake8]`, `[tool:pytest]`, `[coverage:run]`, `[coverage:report]`

---

## 8. Environment Variable Documentation

All required environment variables are documented in `.env.example`:

| Variable | Required | Description |
|---|---|---|
| `SECRET_KEY` | ✅ Yes | Django cryptographic signing key |
| `DEBUG` | ✅ Yes | `False` in production, `True` in development |
| `ALLOWED_HOSTS` | ✅ Yes | Comma-separated list of valid hostnames |
| `DATABASE_URL` | ✅ Yes | Database connection string |
| `DJANGO_SETTINGS_MODULE` | Recommended | Settings module path |

---

## Quick Full Audit Command

Run all security checks at once:

```bash
echo "=== 1. SECRET_KEY hardcoded check ==="
grep -rn "SECRET_KEY\s*=\s*['\"]" config/settings/ && echo "FAIL: hardcoded SECRET_KEY found" || echo "PASS: no hardcoded SECRET_KEY"

echo "=== 2. CSRF tokens in forms ==="
grep -l "csrf_token" templates/todos/todo_form.html templates/todos/todo_confirm_delete.html

echo "=== 3. |safe filter audit ==="
grep -rn "|safe" templates/ && echo "WARNING: |safe found — review manually" || echo "PASS: no |safe filters"

echo "=== 4. autoescape off audit ==="
grep -rn "autoescape off" templates/ && echo "FAIL: autoescape disabled" || echo "PASS: auto-escaping active"

echo "=== 5. Flake8 lint ==="
flake8 . --config=setup.cfg

echo "=== 6. Pytest with coverage ==="
pytest --cov=. --cov-config=setup.cfg --cov-report=term-missing --cov-fail-under=80
```
