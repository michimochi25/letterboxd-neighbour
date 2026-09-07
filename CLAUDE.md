# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

Backend (run from `backend/`, venv activated):
```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload        # dev server on :8000
python main.py                   # same app, no reload, binds 0.0.0.0
```

Frontend (run from `frontend/`, pnpm is the package manager — a `pnpm-lock.yaml` is committed):
```bash
pnpm install
pnpm dev        # vite dev server
pnpm build      # tsc -b && vite build (type errors fail the build)
pnpm lint       # eslint
```

`frontend/.env` is gitignored and required — without `VITE_API_URL=http://localhost:8000` the fetch in `App.tsx` targets `undefined/api/compare`. `VITE_POSTHOG_KEY` and `VITE_POSTHOG_HOST` are optional: `main.tsx` only calls `posthog.init` when the key is set, so analytics no-ops without them.

There is no test suite and no Python linter/formatter configured. `pnpm build` (which type-checks) is the only automated check in the repo.

## Architecture

Two independent processes: a FastAPI backend that scrapes Letterboxd and computes a score, and a Vite/React SPA that renders it. The only contract between them is `POST /api/compare` — `{user1, user2}` in, the object shaped by `frontend/src/types.ts` (`Data`) out. Changing the response shape in `backend/main.py` requires updating `types.ts` in the same change; nothing enforces this.

### Backend (`backend/main.py`, single file)

Whole request is one async pipeline, no database, no cache — every comparison re-scrapes both users from scratch, which is why the UI warns it may take a while.

1. `scrape_user` fetches `letterboxd.com/{user}/films/page/1/`, parses the paginator to learn the page count, then fans out pages 2..N concurrently. Two hard limits matter: pages are capped at **50** and an `asyncio.Semaphore(MAX_CONCURRENT_REQUESTS = 3)` throttles in-flight requests. Raising the semaphore is what gets the scraper 403'd.
2. Requests go through `curl_cffi.AsyncSession(impersonate="chrome120")` rather than plain httpx — Letterboxd blocks default Python TLS fingerprints. This is load-bearing; the last commit was a 403 fix.
3. Ratings are parsed out of the CSS class on the rating span (`rated-9` → 4.5). Films are keyed by Letterboxd **slug** throughout; an unrated film has rating `0`, which is also the "not rated" sentinel used to filter later.
4. `calculate_similarity` computes Jaccard over all watched slugs, then Pearson over the inner join filtered to `rating > 0` on both sides. Pearson requires ≥5 shared rated films (else `0.0`) and has a zero-variance special case, since `pearsonr` is undefined there. Score is `0.7 * ((pearson + 1) / 2) + 0.3 * jaccard`, and the 70/30 split is also stated verbatim in the explainer dialog in `App.tsx` — keep them in sync.
5. Poster URLs for the top-5 disagreements are scraped lazily, one film page each, in a second parallel batch, out of the `application/ld+json` script tag (CDATA wrappers stripped by string splitting).

Failures are swallowed per-page and return empty film lists, so a partial scrape silently yields a low-confidence score rather than an error. CORS is wide open (`allow_origins=["*"]`).

### Frontend (`frontend/src/`)

`App.tsx` holds all state and the entire UI; there is no router and no data layer. `components/ui/` is shadcn/ui (new-york style, neutral base, `@` → `src` alias) — treat those as generated and add new shadcn components via the CLI rather than hand-writing them. `components/` holds the three app-specific ones (`Card`, `StackedBar`, `DisagreeRow`). Styling is Tailwind v4 via the Vite plugin (no `tailwind.config.js`; theme lives in `@theme` in `src/index.css`).

The Letterboxd palette is hardcoded as literal hex in class strings, thresholded the same way in three places in `App.tsx`: `≤30` orange `#ff8000`, `31–60` green `#00e054`, `>60` blue `#40bcf4`.

`recharts` is a dependency but unused — `StackedBar` is hand-rolled divs. There is a commented-out "Top 5 Agreement" block in `App.tsx` and a matching `agreeableMovies` field commented out in `types.ts`; the backend never returned it.
