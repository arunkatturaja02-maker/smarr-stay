# StaySmart

**Smart Hotel Room Allocation & Housekeeping Service Prioritization System**

This repository currently implements **Module 1: Authentication & Role Management** only.

Module 1 provides secure staff registration, administrator approval, login, JWT-based sessions, and role-based authorization for three staff roles:

| Role | Dashboard |
| --- | --- |
| `RECEPTIONIST` | `/receptionist/dashboard` |
| `HOUSEKEEPING_MANAGER` | `/manager/dashboard` |
| `HOUSEKEEPING_STAFF` | `/staff/dashboard` |

The dashboards are intentionally placeholders. Room management, bookings, service requests, priority calculation, staff assignment, inspections, and guest verification are **not** part of this module.

---

## 1. Technology stack

- **Frontend:** React 19 + Vite (JavaScript, not TypeScript) + React Router + Axios
- **Backend:** Python + FastAPI + Pydantic
- **Database:** PostgreSQL
- **ORM:** SQLAlchemy 2.x
- **Migrations:** Alembic
- **Passwords:** Argon2id via `pwdlib[argon2]`
- **Sessions:** signed JWT access token stored in an **HttpOnly cookie**
- **Tests:** pytest + FastAPI TestClient with an isolated temporary SQLite database

---

## 2. Project structure

```text
smarr-stay/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── deps.py            # JWT + role authorization dependencies
│   │   │   └── routes/
│   │   │       ├── auth.py        # registration, login, me, logout
│   │   │       └── health.py      # API/database health check
│   │   ├── core/
│   │   │   ├── config.py          # environment settings
│   │   │   └── security.py        # Argon2 hashing + JWT helpers
│   │   ├── db/
│   │   │   ├── base.py
│   │   │   └── session.py
│   │   ├── models/user.py         # users table model
│   │   ├── schemas/auth.py        # Pydantic validation
│   │   ├── services/auth_service.py
│   │   └── main.py                # FastAPI application
│   ├── alembic/
│   │   └── versions/0001_create_users.py
│   ├── scripts/manage_accounts.py # local approval/disable CLI (not HTTP)
│   ├── tests/
│   ├── .env.example
│   ├── alembic.ini
│   ├── requirements.txt
│   └── requirements-dev.txt
├── frontend/
│   ├── src/
│   │   ├── api/                   # Axios client + error normalisation
│   │   ├── auth/                  # auth context, routes guards, role config
│   │   ├── components/            # shared UI
│   │   ├── pages/                 # login, registration, status pages
│   │   └── pages/dashboards/      # three role dashboards
│   ├── .env.example
│   ├── package.json
│   └── vite.config.js
├── .gitignore
└── README.md
```

---

## 3. Prerequisites

Install:

- **Python 3.11+** (this project was verified with Python 3.14.5)
- **Node.js 22+** and npm (verified with Node 24.16 and npm 11.13)
- **PostgreSQL 15+**
- Git

Check:

```powershell
python --version
node --version
npm --version
psql --version
```

> The tests do **not** require PostgreSQL. They use a temporary SQLite database created for each test run. PostgreSQL is required for actually running the application.

---

## 4. PostgreSQL setup

Create a dedicated database and user. Example (run from a terminal where PostgreSQL's `bin` directory is available):

```powershell
createuser -U postgres --pwprompt staysmart_user
createdb -U postgres --owner=staysmart_user staysmart
```

When prompted, choose a strong password. Do not reuse a login password.

If your PostgreSQL installation uses a different admin user or port, adjust the commands.

You can verify the connection:

```powershell
psql -U staysmart_user -h localhost -d staysmart -c "SELECT current_database();"
```

### Database URL

The backend reads the connection string from `DATABASE_URL`. The format is:

```text
postgresql+psycopg://USER:PASSWORD@HOST:PORT/DATABASE
```

If the password contains URL-special characters, URL-encode them. For example, `@` becomes `%40`.

---

## 5. Backend setup

### 5.1 Create a virtual environment

From the repository root:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
```

If PowerShell blocks activation, run this for the current terminal:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

You can also run commands without activating:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
```

### 5.2 Install dependencies

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
```

`requirements-dev.txt` includes the runtime requirements plus pytest and httpx2.

### 5.3 Configure environment variables

Copy the example file:

```powershell
Copy-Item .env.example .env
```

macOS/Linux:

```bash
cp .env.example .env
```

Generate a strong JWT secret:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Put the result in `backend/.env` as `JWT_SECRET_KEY`.

Example `backend/.env` (replace every placeholder):

```dotenv
DATABASE_URL=postgresql+psycopg://staysmart_user:YOUR_URL_ENCODED_PASSWORD@localhost:5432/staysmart
JWT_SECRET_KEY=THE_RANDOM_VALUE_GENERATED_ABOVE
ACCESS_TOKEN_EXPIRE_MINUTES=30
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
ENVIRONMENT=development
COOKIE_SECURE=false
COOKIE_SAMESITE=lax
```

**Never commit `backend/.env`.** It is already excluded by `.gitignore`. Never put a real JWT secret in `.env.example` or source code.

Important settings:

| Variable | Purpose |
| --- | --- |
| `DATABASE_URL` | PostgreSQL SQLAlchemy connection string |
| `JWT_SECRET_KEY` | Signing secret; minimum 32 characters; required |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token/cookie lifetime (5–1440 minutes) |
| `CORS_ORIGINS` | Comma-separated allowed frontend origins |
| `ENVIRONMENT` | `development`, `test`, or `production` |
| `COOKIE_SECURE` | Must be `true` over HTTPS; required in production |
| `COOKIE_SAMESITE` | `lax` recommended for same-site deployments |

The application intentionally **fails to start** if `DATABASE_URL` or a strong `JWT_SECRET_KEY` is missing, or if the example placeholders have not been replaced.

### 5.4 Run the Alembic migration

From `backend/` with the virtual environment active:

```powershell
alembic upgrade head
```

Useful commands:

```powershell
alembic current        # show the current migration revision
alembic history        # list migrations
alembic upgrade head   # apply all pending migrations
```

Do not run `alembic downgrade` against a database containing data you need: the initial migration's downgrade drops the `users` table.

The migration creates:

- `users` table
- PostgreSQL enum type `user_role`
- UUID primary key
- Unique indexes on `email` and `employee_id`
- Indexes for `role`, `is_active`, and `is_approved`
- `created_at` / `updated_at` timezone-aware timestamps

### 5.5 Start the backend

From `backend/`:

```powershell
uvicorn app.main:app --reload --port 8000
```

Check:

- API root: <http://localhost:8000/>
- Health/DB check: <http://localhost:8000/api/health>
- Interactive API docs: <http://localhost:8000/docs>

If `/api/health` returns 503, PostgreSQL is not reachable or `DATABASE_URL` is wrong.

---

## 6. Account approval workflow

### The security rule

Public registration creates accounts with:

- `is_active = true`
- `is_approved = false`

An unapproved account **cannot log in** and **cannot use protected APIs**, even if a token was somehow issued previously. Approval is checked again from the database on every protected request.

There is **no public or unauthenticated approval endpoint** and **no public superuser registration endpoint**.

Approval is performed locally by someone with server access, the backend environment, and PostgreSQL credentials:

```powershell
# List accounts awaiting approval
python -m scripts.manage_accounts list --status pending

# Approve by email or employee ID
python -m scripts.manage_accounts approve --email manager@example.com
python -m scripts.manage_accounts approve --employee-id MGR-001

# Disable or re-enable an account
python -m scripts.manage_accounts disable --employee-id MGR-001
python -m scripts.manage_accounts enable --employee-id MGR-001

# List approved/all accounts
python -m scripts.manage_accounts list --status approved
python -m scripts.manage_accounts list --status all
```

The CLI is a local database administration tool. It is not exposed by FastAPI and must not be deployed as a web endpoint.

### Creating the first authorized staff account

1. Start the backend and frontend.
2. Open the registration page for the desired role.
3. Register the manager or receptionist account. It will be unapproved.
4. From `backend/`, run the approval CLI:

   ```powershell
   python -m scripts.manage_accounts approve --email the-account@example.com
   ```

5. Sign in at <http://localhost:5173/login>.

This controlled registration + local approval process is the intended initial-account bootstrap. There is no admin account seeded with a default password.

### Housekeeping staff

Housekeeping staff registration uses the same policy: public registration, then explicit administrator approval.

---

## 7. Frontend setup

From the repository root:

```powershell
cd frontend
npm install
```

Optional: copy the frontend environment example if your API is not at `http://localhost:8000`:

```powershell
Copy-Item .env.example .env
```

The content is:

```dotenv
VITE_API_BASE_URL=http://localhost:8000
```

Start the development server:

```powershell
npm run dev
```

Open <http://localhost:5173>.

Other frontend commands:

```powershell
npm run lint
npm run build
npm run preview
```

The backend CORS configuration must include the exact frontend origin (`http://localhost:5173` by default). If Vite chooses a different port, set `strictPort`/port in `vite.config.js` or add the new origin to `CORS_ORIGINS`.

### Vite build note for restricted Windows machines

Vite 8 uses Rolldown, which normally loads a native binary. This project includes `@rolldown/binding-wasm32-wasi` as a development dependency so the build can fall back to WebAssembly if an Application Control policy blocks the native `.node` file. On normal machines the native binding is used automatically.

---

## 8. Pages and how to test each role

| Page | URL |
| --- | --- |
| Login | `/login` |
| Registration chooser | `/register` |
| Receptionist registration | `/register/receptionist` |
| Manager registration | `/register/manager` |
| Housekeeping staff registration | `/register/staff` |
| Pending approval | `/pending-approval` |
| Access denied | `/unauthorized` |
| Receptionist dashboard | `/receptionist/dashboard` |
| Manager dashboard | `/manager/dashboard` |
| Staff dashboard | `/staff/dashboard` |

### Test the receptionist role

1. Register at `/register/receptionist`.
2. Approve the account with the CLI.
3. Sign in.
4. You should be redirected to `/receptionist/dashboard`.
5. While signed in, manually open `/manager/dashboard`. You should see the access-denied page.

### Test the manager role

1. Register at `/register/manager`.
2. Approve with the CLI.
3. Sign in and confirm redirect to `/manager/dashboard`.
4. Manually open `/receptionist/dashboard`; access should be denied.

### Test the housekeeping staff role

1. Register at `/register/staff`.
2. Approve with the CLI.
3. Sign in and confirm redirect to `/staff/dashboard`.
4. Manually open another role's dashboard; access should be denied.

### Other checks

- Register, then try to log in before approval → clear pending-approval message.
- Disable an approved account with the CLI, then try an already-open session → protected API returns `403 account_disabled`.
- Use a wrong password → generic invalid-credentials message.
- Log out → cookie cleared, `/api/auth/me` returns 401.
- Refresh after login → session is restored from the HttpOnly cookie.
- Try `/api/auth/me` in a private window → 401.

Frontend route guards improve the user experience, but the backend independently enforces every permission.

---

## 9. API endpoints

All routes are under `http://localhost:8000`.

| Method | Endpoint | Access | Purpose |
| --- | --- | --- | --- |
| `POST` | `/api/auth/register/receptionist` | Public | Register unapproved receptionist |
| `POST` | `/api/auth/register/manager` | Public | Register unapproved manager |
| `POST` | `/api/auth/register/staff` | Public | Register unapproved housekeeping staff |
| `POST` | `/api/auth/login` | Public | Validate credentials, issue JWT cookie |
| `GET` | `/api/auth/me` | Any approved active role | Return safe profile |
| `POST` | `/api/auth/logout` | Public (clears cookie) | Clear authentication cookie |
| `GET` | `/api/health` | Public | API + database health |
| `GET` | `/` | Public | API status |
| `GET` | `/docs` | Public (development) | OpenAPI documentation |

### Registration request body

```json
{
  "full_name": "Priya Sharma",
  "employee_id": "REC-1042",
  "email": "priya@example.com",
  "phone_number": "+91 98765 43210",
  "password": "StrongPass1",
  "confirm_password": "StrongPass1"
}
```

The role is determined by the endpoint. Sending an extra `role` field is rejected by Pydantic (`422`).

### Login request body

```json
{
  "identifier": "priya@example.com",
  "password": "StrongPass1"
}
```

`identifier` can be an email address or an employee ID.

### Safe profile response from `/api/auth/me`

```json
{
  "id": "UUID",
  "full_name": "Priya Sharma",
  "employee_id": "REC-1042",
  "email": "priya@example.com",
  "phone_number": "+91 98765 43210",
  "role": "RECEPTIONIST"
}
```

`password_hash` is never included in any API response.

### Authorization pattern for future modules

Use the existing dependencies instead of writing new token logic:

```python
from typing import Annotated
from fastapi import APIRouter, Depends
from app.api.deps import require_roles
from app.models.user import User, UserRole

router = APIRouter()


@router.get("/manager-only")
def manager_only(
    user: Annotated[
        User, Depends(require_roles(UserRole.HOUSEKEEPING_MANAGER))
    ],
):
    return {"message": f"Hello {user.full_name}"}
```

For endpoints available to multiple roles, pass multiple roles to `require_roles(...)`. Authorization always uses the user reloaded from PostgreSQL, not the role claim sent by the browser.

---

## 10. Authentication and security design

### Passwords

- Hashed with **Argon2id** using `pwdlib`.
- Plain-text passwords are never stored, logged, or returned.
- Login compares the submitted password against the hash.
- Unknown identifiers still perform a dummy hash verification to reduce timing-based account discovery.

### JWT

- Signed with `JWT_SECRET_KEY` using HS256.
- Contains `sub` (user UUID), `role`, `type`, `iss`, `iat`, `exp`, and `jti`.
- Default lifetime: 30 minutes.
- Signature, expiry, issuer, token type, and required claims are validated.
- The token role claim is **not trusted** for permission checks. `get_current_user()` reloads the user from PostgreSQL and `require_roles()` checks the database role.

### Cookie strategy

- The JWT is set as an **HttpOnly**, `SameSite=Lax` cookie.
- The frontend does not store the JWT in `localStorage` or `sessionStorage`.
- Axios uses `withCredentials: true`.
- Local development uses `COOKIE_SECURE=false` because it runs over HTTP.
- Production requires HTTPS and `COOKIE_SECURE=true`; the settings reject insecure production cookies.

**CSRF trade-off:** `SameSite=Lax` blocks the cookie on most cross-site state-changing requests and login uses a JSON body. If the production frontend and API are deployed on different sites and `COOKIE_SAMESITE=none` is required, add a CSRF token mechanism (for example, a double-submit token) before exposing state-changing endpoints. Prefer deploying the frontend and API on the same site.

**Logout:** logout clears the cookie. JWTs are stateless, so a copied token remains valid until it expires. The short expiry limits this. A server-side denylist can be added later if immediate revocation is required.

### Error handling

- Invalid login credentials return the same generic message for wrong passwords and unknown accounts.
- Pending and disabled accounts return `403` only after a correct password is supplied.
- Missing/invalid/expired tokens return `401`.
- Cross-role access returns `403 forbidden`.
- Duplicate registration returns `409` with a safe field-specific message.
- PostgreSQL connection failures return `503 database_unavailable` without exposing connection details.

### Not included in Module 1

- Login rate limiting / account lockout
- Email verification or password reset
- CSRF tokens for cross-site cookie deployment
- Admin UI for approvals
- Guest authentication or booking verification
- Refresh tokens

These are deliberate scope boundaries for Module 1, not hidden features.

---

## 11. Running the tests

From `backend/` with the virtual environment active:

```powershell
python -m pytest -q
```

The tests:

1. Create a fresh temporary SQLite database in the system temp directory.
2. Run the **real Alembic migration** against it.
3. Never read `DATABASE_URL` from `backend/.env`.
4. Never connect to or erase the PostgreSQL development database.
5. Delete the temporary database after the test session.

The suite covers:

- Registration creates an Argon2 hash, not plain text
- Duplicate email and employee ID rejection
- Fixed role assignment per endpoint and rejection of client-supplied roles
- Password strength and confirmation validation
- Approved-account login with HttpOnly cookie
- Generic invalid-credentials responses
- Unapproved accounts blocked at login and at protected endpoints
- Disabled accounts blocked at login and at protected endpoints
- Unauthenticated access rejection
- Receptionist blocked from manager-only behavior
- Staff blocked from receptionist-only behavior
- Tampered JWT role claim ignored in favour of the database role
- Expired token rejection
- Safe `/api/auth/me` profile fields
- Logout clears the session
- Example placeholder JWT secret and database password rejection

**Verified locally:** `26 passed` with pytest. Frontend `npm run lint` and `npm run build` also pass. A live HTTP smoke test against a temporary SQLite database confirmed registration (`201`), pending login (`403 account_pending_approval`), approval, login (`200`), HttpOnly/`SameSite=Lax` cookie, `/me` without `password_hash`, CORS credentials, and logout.

The migration was also applied successfully to a local PostgreSQL 18 instance, and the health and login endpoints were smoke-tested against it. The generated SQL includes `CREATE TYPE user_role`, unique indexes, and the downgrade `DROP TYPE`.

---

## 12. Common errors and solutions

| Symptom | Likely cause | Solution |
| --- | --- | --- |
| `ValidationError` mentioning `JWT_SECRET_KEY` | Missing or too-short secret | Generate a 48-byte secret and update `backend/.env` |
| `ValidationError` mentioning `DATABASE_URL` | Missing environment variable | Copy `.env.example` to `.env` and fill it in |
| `/api/health` returns 503 | PostgreSQL down, wrong host/port, wrong password | Check the PostgreSQL service and `DATABASE_URL` |
| `psycopg.OperationalError` | Database/user does not exist or password is wrong | Re-run PostgreSQL setup; URL-encode special characters |
| `relation "users" does not exist` | Migration not applied | Run `alembic upgrade head` from `backend/` |
| `alembic: command not found` | Virtual environment not active | Activate `.venv` or run `python -m alembic upgrade head` |
| CORS error in browser | Frontend origin not listed | Add the exact origin/port to `CORS_ORIGINS` and restart FastAPI |
| Login succeeds but `/me` returns 401 | Cookie not sent | Keep `withCredentials: true`, use same-site hosts, do not set `COOKIE_SECURE=true` over local HTTP |
| `403 account_pending_approval` | Account not approved | Run the approval CLI |
| `403 account_disabled` | Account disabled | Run `python -m scripts.manage_accounts enable ...` |
| `409 email_in_use` / `employee_id_in_use` | Duplicate registration | Use a different email/employee ID or sign in |
| `422` on registration | Validation failed, role field supplied, or passwords mismatch | Read the field errors shown by the form |
| Access denied after login | Role does not own that dashboard | Use the dashboard that matches your role |
| `npm run build` fails with a native binding error | Application Control blocks Rolldown's native file | The WASM fallback dependency is included; run `npm install` again. If still blocked, allow the binary or use Vite 7 |
| Direct dashboard URL returns 404 after production build | Web server has no SPA fallback | Configure the web server to serve `index.html` for unknown frontend routes |
| Vite starts on a different port | Port 5173 is occupied | The project sets `strictPort: true`; free the port or update CORS |

---

## 13. Module boundaries and future guest access

This module deliberately contains **no** room management, bookings, service requests, priority calculation, staff assignment, inspection, or guest booking validation.

The architecture leaves room for later guest access:

- Staff authentication and guest verification will be separate flows.
- A future guest endpoint can verify a phone number and active checked-in booking before issuing a guest-specific token.
- Guest permissions must not be added to the staff role dependencies; use a separate guest authentication dependency and separate route namespace.
- Approval and staff-role rules must never be reused to authenticate guests.

No guest endpoint is implemented now.
