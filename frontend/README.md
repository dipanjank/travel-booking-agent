# QA App Frontend

SvelteKit chat UI for the travel booking agent. Communicates with the backend API for authentication and conversational flight search/booking.

## Tech Stack

- [SvelteKit](https://svelte.dev/docs/kit) with Svelte 5 (runes mode)
- TypeScript
- [`@sveltejs/adapter-node`](https://svelte.dev/docs/kit/adapter-node) for production builds

## Development

```bash
npm install
npm run dev
```

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
  routes/        Page routes (SvelteKit file-based routing)
  lib/           Shared modules, components, and assets
  app.html       HTML shell
  app.d.ts       TypeScript declarations
static/          Static assets served as-is
```
