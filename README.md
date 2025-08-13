# DEMO – Chat Application

A Next.js (App Router) project with a simple AI chat interface.

## Requirements
- Node.js 18.18+ or 20+
- pnpm 9+

If you don't have pnpm:
```bash
npm i -g pnpm
```

## Getting Started (Development)
1. Install dependencies:
```bash
pnpm install
```

2. Configure environment variables. Create a `.env.local` file in the project root:
```bash
GEMINI_API_KEY=your_gemini_api_key_here
```
- This key is used by the server route at `app/api/chat/route.ts`.
- Do not prefix secrets with `NEXT_PUBLIC_` (that would expose them to the client).

3. Run the dev server:
```bash
pnpm dev
```
Then open `http://localhost:3000`.

## Available Scripts
- Development:
```bash
pnpm dev
```
- Lint:
```bash
pnpm lint
```
- Build (production):
```bash
pnpm build
```
- Start (serve production build):
```bash
pnpm start
```

## Production
1. Build the app:
```bash
pnpm build
```
2. Ensure the `GEMINI_API_KEY` environment variable is set on the host.
3. Start the server:
```bash
pnpm start
```

## Deployment Notes
- Vercel: add the `GEMINI_API_KEY` in Project Settings → Environment Variables (apply to Development/Preview/Production), then redeploy.
- Self-hosted: set `GEMINI_API_KEY` in your process manager (systemd, Docker, etc.) or use a `.env` file loaded by your runtime.

## Project Structure (high-level)
- `app/`: Next.js App Router pages and API routes
  - `api/chat/route.ts`: Chat completion endpoint using Gemini API
  - `page.tsx`: Main app page (chat UI)
  - `layout.tsx`: Root layout
- `components/`: UI components (chat area, message input, sidebar, shadcn/ui)
- `hooks/`, `lib/`: utilities and hooks
- `styles/`: global styles

## Notes
- This project uses Tailwind CSS (v4) and shadcn/ui components.
- Environment files (`.env*`) are ignored by Git (see `.gitignore`).