# LegalBrief

## Setup

```bash
npm i
cp .env.example .env   # then fill in the values below
npm run dev
```

Open http://localhost:5173

## Environment variables (`.env`)

| Variable | Description |
|---|---|
| `VITE_API_BASE_URL` | Base URL of your backend, trailing slash included (e.g. `https://api.example.com/`). Used for `api/upload` and `api/chat`. |
| `VITE_SUPABASE_URL` | Your Supabase project URL. |
| `VITE_SUPABASE_ANON_KEY` | Your Supabase anon/public key. |

## Expected Supabase schema

This app assumes two tables already exist (unchanged from the original app):

**`documents`**
| column | type |
|---|---|
| `id` | uuid / int, primary key |
| `file_name` | text |
| `status` | text (`valid` / `invalid`) |
| `created_at` | timestamp, default `now()` |

**`chat_messages`**
| column | type |
|---|---|
| `id` | uuid / int, primary key |
| `document_id` | references `documents.id` |
| `role` | text (`user` / `assistant` / `error`) |
| `content` | text |
| `created_at` | timestamp, default `now()` |

## Project structure

```
src/
  main.jsx              # React entry point
  LegalBriefApp.jsx      # Main app: state, API calls, Supabase reads/writes
  LegalBriefApp.css       # Design system (tokens, layout, components)
  lib/supabase.js         # Supabase client
  components/
    Sidebar.jsx            # Recent documents list + "New chat"
    TopBar.jsx              # Doc title, status badge, upload/replace button
    ChatThread.jsx           # Message list
    ChatDock.jsx              # Chat input row
```

## Backend contract (unchanged)

- `POST {VITE_API_BASE_URL}api/upload` — multipart form with a `file` field. Expects JSON back with `status: "Valid" | "Invalid"`.
- `POST {VITE_API_BASE_URL}api/chat` — JSON body `{ question }`. Expects JSON back with `{ answer }` (or `{ detail }` on non-2xx).
