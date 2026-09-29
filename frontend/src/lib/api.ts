import { env } from "$env/dynamic/public";

export const publicApiBaseUrl = env.PUBLIC_API_BASE_URL || "http://localhost:8000";

// Public origin of the attacker/CSRF demo site. On Railway set
// PUBLIC_ATTACKER_BASE_URL to the attacker-site service's public URL.
export const publicAttackerBaseUrl =
  env.PUBLIC_ATTACKER_BASE_URL || "http://localhost:7001";
