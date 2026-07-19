# LegalBrief Agent — Frontend

AI-powered contract intelligence UI. This is a **frontend-only** build: all
data is mocked in `src/data/`, so it runs standalone with no backend.

## Setup

```bash
npm install
npm run dev       # http://localhost:5173
npm run build      # production build to /dist
npm run preview    # preview the production build
```

## Stack & why

| Package | Purpose |
|---|---|
| React 19 + Vite | fast dev server, modern React features |
| Tailwind CSS v4 (`@tailwindcss/vite`) | utility-first styling, no separate config file needed |
| React Router DOM v7 | client-side routing across pages |
| Framer Motion | page/element transitions (hero, modals, toasts, progress bar) |
| Lucide React | icon set used throughout |
| React Icons | installed per spec, available for any icon not in Lucide |
| React Markdown | renders AI chat responses (bold, lists, etc.) safely |

No `axios`, no API calls — every page reads from `src/data/*.js`. Each data
file mirrors what a real API response would look like, so swapping in real
calls later means: write a `services/` layer, replace the mock `setTimeout`
calls in the contexts/hooks with real requests, and the components
themselves don't need to change.

## Folder structure

```
src/
  assets/
  components/
    common/      Button, Input, Textarea, Card, Modal, Loader, Toast, EmptyState/ErrorState
    layout/      Navbar, Sidebar, Footer, DashboardLayout
    upload/      FileUploader, UploadProgress, FilePreview
    chat/        ChatWindow, ChatBubble, ChatInput, ChatHistory, SuggestedQuestions, TypingIndicator
    documents/   DocumentCard
    summary/     SummaryCard
    risk/        RiskCard, RiskScore
  pages/         Landing, Dashboard, Upload, Chat, Documents, Summary, RiskAnalysis, Settings
  context/       ThemeContext, DocumentContext, ChatContext
  hooks/         useTheme, useChat, useUpload
  data/          chatData.js, documentData.js, summaryData.js, riskData.js  <- mock data lives here
  utils/         constants.js, formatters.js
  routes/        AppRoutes.jsx
  App.jsx
  main.jsx
  index.css
```

## Routes

`/` , `/dashboard` , `/upload` , `/chat` , `/documents` , `/summary/:id` ,
`/risk-analysis/:id` , `/settings`

## Notes

- Dark mode is fully wired (ThemeContext + Tailwind `dark:` classes,
  toggle in the navbar and in Settings) - not just a placeholder.
- Upload flow simulates progress with a timer in `useUpload`; swap that
  block for real upload-progress events when a backend exists.
- Chat replies are randomly picked from a mock pool in `ChatContext`;
  replace the `setTimeout` with a real `askQuestion()` call later.
