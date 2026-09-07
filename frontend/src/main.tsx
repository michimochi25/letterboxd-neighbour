import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import posthog from 'posthog-js'
import { PostHogProvider } from '@posthog/react'
import './index.css'
import App from './App.tsx'

// Analytics is optional. Without VITE_POSTHOG_KEY posthog is never initialised,
// which makes every capture() downstream a no-op and sends no requests.
const posthogKey = import.meta.env.VITE_POSTHOG_KEY

if (posthogKey) {
  posthog.init(posthogKey, {
    api_host: import.meta.env.VITE_POSTHOG_HOST || 'https://us.i.posthog.com',
    defaults: '2026-05-30',
    // Autocapture records href and link text, and our links carry the compared
    // usernames (see DisagreeRow). Events are captured explicitly instead.
    autocapture: false,
  })
}

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <PostHogProvider client={posthog}>
      <App />
    </PostHogProvider>
  </StrictMode>,
)
