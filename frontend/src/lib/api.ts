import { env } from "$env/dynamic/public";

export const publicApiBaseUrl = env.PUBLIC_API_BASE_URL || "http://localhost:8000";
