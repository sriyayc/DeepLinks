// Task 5 — OAuth / PKCE lab helpers.
// Minimal browser-side PKCE (RFC 7636) implementation for the CyberID demo login.

function base64UrlEncode(bytes: ArrayBuffer | Uint8Array): string {
  const arr = bytes instanceof Uint8Array ? bytes : new Uint8Array(bytes);
  let binary = "";
  for (const byte of arr) binary += String.fromCharCode(byte);
  return btoa(binary).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}

export function generateState(): string {
  return base64UrlEncode(crypto.getRandomValues(new Uint8Array(16)));
}

export function generateCodeVerifier(): string {
  return base64UrlEncode(crypto.getRandomValues(new Uint8Array(32)));
}

export async function generateCodeChallenge(verifier: string): Promise<string> {
  const data = new TextEncoder().encode(verifier);
  const digest = await crypto.subtle.digest("SHA-256", data);
  return base64UrlEncode(digest);
}

export interface AuthorizeParams {
  clientId: string;
  redirectUri: string;
  state: string;
  codeChallenge: string;
}

export function buildAuthorizeUrl(oauthBaseUrl: string, params: AuthorizeParams): string {
  const q = new URLSearchParams({
    response_type: "code",
    client_id: params.clientId,
    redirect_uri: params.redirectUri,
    state: params.state,
    code_challenge: params.codeChallenge,
    code_challenge_method: "S256",
  });
  return `${oauthBaseUrl}/authorize?${q.toString()}`;
}

/**
 * Probe an /authorize URL without letting the browser actually navigate.
 * redirect:"manual" resolves a 3xx as an opaque "opaqueredirect" type
 * (vulnerable — server accepted this redirect_uri), or an ordinary readable
 * JSON response (fixed — e.g. invalid_redirect_uri).
 */
export async function probeAuthorize(url: string): Promise<{ willRedirect: boolean; body?: unknown }> {
  const res = await fetch(url, { method: "GET", redirect: "manual", credentials: "omit" });
  if (res.type === "opaqueredirect" || res.status === 0) {
    return { willRedirect: true };
  }
  let body: unknown = undefined;
  try {
    body = await res.json();
  } catch {
    // ignore — non-JSON body
  }
  return { willRedirect: false, body };
}

const STORAGE_KEY_PREFIX = "cybercart_oauth_";

export function storePkceState(state: string, codeVerifier: string) {
  sessionStorage.setItem(STORAGE_KEY_PREFIX + state, codeVerifier);
}

export function takePkceState(state: string): string | null {
  const key = STORAGE_KEY_PREFIX + state;
  const verifier = sessionStorage.getItem(key);
  if (verifier) sessionStorage.removeItem(key);
  return verifier;
}