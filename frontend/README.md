# StaySmart Frontend

React + Vite frontend for Module 1 (authentication and role management).

See the [root README](../README.md) for full setup, API, approval workflow, and security documentation.

## Commands

```bash
npm install
npm run dev      # http://localhost:5173
npm run lint
npm run build
```

## Environment

Copy `.env.example` to `.env` only if the API is not running at `http://localhost:8000`:

```dotenv
VITE_API_BASE_URL=http://localhost:8000
```

Authentication uses an HttpOnly cookie. JWTs are not stored in localStorage or sessionStorage.
