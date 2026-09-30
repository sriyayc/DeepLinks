import { env } from "$env/dynamic/public";

// Same-origin: browser API calls go to the frontend, which proxies /api to the
// backend (see vite.config.ts). This keeps the shop session cookie first-party
// and means participants only ever need the frontend URL. Intentionally not
// read from env so a stale PUBLIC_API_BASE_URL can't force cross-origin calls.
export const publicApiBaseUrl = "";

// Public origin of the attacker/CSRF demo site. On Railway set
// PUBLIC_ATTACKER_BASE_URL to the attacker-site service's public URL.
export const publicAttackerBaseUrl =
  env.PUBLIC_ATTACKER_BASE_URL || "http://localhost:7001";

// CTF challenges are locked until an instructor sets PUBLIC_CHALLENGES_ENABLED
// to "true" on the frontend service (default locked).
export const publicChallengesEnabled = env.PUBLIC_CHALLENGES_ENABLED === "true";

// Task 5 — OAuth / PKCE lab config.
export const publicOauthBaseUrl = env.PUBLIC_OAUTH_BASE_URL || "http://localhost:9000";
export const publicOauthClientId = env.PUBLIC_OAUTH_CLIENT_ID || "cybercart";

// CyberCart's own callback, exactly as registered in oauth-server's
// `clients[...].redirect_uris`. Must match exactly or the "fixed" flow will
// also be rejected.
export const publicOauthRedirectUri =
  env.PUBLIC_OAUTH_REDIRECT_URI || "http://localhost:5173/oauth/callback";

// The redirect_uri a spoofed/phishing authorize link would use instead of
// CyberCart's real callback.
export const publicOauthAttackerRedirectUri =
  env.PUBLIC_OAUTH_ATTACKER_REDIRECT_URI ||
  "https://layer8-attacker.up.railway.app/oauth/callback";