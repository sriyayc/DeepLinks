import { env } from "$env/dynamic/public";

export const publicApiBaseUrl = env.PUBLIC_API_BASE_URL || "http://localhost:8000";

// Public origin of the attacker/CSRF demo site. On Railway set
// PUBLIC_ATTACKER_BASE_URL to the attacker-site service's public URL.
export const publicAttackerBaseUrl =
  env.PUBLIC_ATTACKER_BASE_URL || "http://localhost:7001";

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