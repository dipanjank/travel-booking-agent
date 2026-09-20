# QA App Frontend

SvelteKit chat UI for the travel booking agent. Communicates with the backend API for authentication and conversational flight search/booking.

## Tech Stack

- [SvelteKit](https://svelte.dev/docs/kit) with Svelte 5 (runes mode)
- TypeScript
- [`@sveltejs/adapter-node`](https://svelte.dev/docs/kit/adapter-node) for production builds

## Pages

| Route          | Description                                      | Auth     |
|----------------|--------------------------------------------------|----------|
| `/login`       | Username/password login form                     | Public   |
| `/`            | Home page with menu cards                        | Required |
| `/flights`     | Chat interface for flight search via agent       | Required |
| `/bookings`    | Booking history (placeholder)                    | Required |
| `/admin/users` | User management (create, list, delete)           | Admin    |

Unauthenticated users are redirected to `/login` via a layout-level route guard.

## Architecture

### Auth Store (`lib/auth.svelte.ts`)

Reactive auth state using Svelte 5 runes. Holds the access token, expiry timestamp, and user role (decoded from the JWT payload), persisted to `sessionStorage` so state survives page reloads within a tab. Exposes `isAdmin` for role-based UI visibility.

### API Wrapper (`lib/api.ts`)

All backend communication goes through this module:

- `login(username, password)` — `POST /api/auth/login`, stores access token on success
- `logout()` — `POST /api/auth/logout`, clears auth state
- `apiFetch(path, init)` — Authenticated fetch wrapper that:
  - Attaches `Authorization: Bearer <token>` header
  - Sends `credentials: 'include'` (for the HttpOnly refresh cookie)
  - On 401, attempts a silent refresh via `POST /api/auth/refresh` and retries once

### Chat UI (`routes/flights/+page.svelte`)

Conversational interface for flight search. Messages are sent to `POST /api/chat` via `apiFetch`. A `thread_id` (UUID) is generated per browser session and stored in `sessionStorage` to support multi-turn conversations. The UI shows user and assistant message bubbles with a loading indicator while the agent responds.

### Route Guard (`routes/+layout.ts`)

Client-side only (`ssr = false`). Checks `auth.isAuthenticated` before every navigation and redirects to `/login` for protected routes.

## Development

```bash
npm install
npm run dev
```

The dev server proxies `/api` requests to `http://localhost:8000` (the backend), configured in `vite.config.ts`.

Type-check:

```bash
npm run check
```

## Build

```bash
npm run build
npm run preview  # preview production build locally
```

The production build outputs to `build/` and runs as a standalone Node.js server on port 3000.

## Docker

```bash
docker build -t qa-app-frontend .
docker run -p 3000:3000 qa-app-frontend
```

## Project Structure

```
src/
  lib/
    auth.svelte.ts   Reactive auth store (access token, expiry)
    api.ts           API wrapper (login, logout, apiFetch with auto-refresh)
    assets/          Static assets imported by components
  routes/
    +layout.ts       Route guard (redirect to /login if unauthenticated)
    +layout.svelte   Root layout (nav bar with links and logout)
    +page.svelte     Home page (menu cards)
    login/
      +page.svelte   Login form
    flights/
      +page.svelte   Chat interface for flight search
    bookings/
      +page.svelte   Booking history (placeholder)
    admin/users/
      +page.svelte   User management (admin only)
  app.html           HTML shell
  app.d.ts           TypeScript declarations
static/              Static assets served as-is
```
