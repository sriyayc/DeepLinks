import type { PageServerLoad } from "./$types";
import { env } from "$env/dynamic/private";

type Product = {
  id: number;
  name: string;
  description: string;
  price: number;
  image: string | null;
  category: string;
};

export const load: PageServerLoad = async ({ url, fetch }) => {
  const query = url.searchParams.get("q") ?? "";
  const safe = url.searchParams.get("safe") === "true";
  let results: Product[] = [];
  let error = "";

  try {
    const response = await fetch(
      `${env.API_BASE_URL || "http://localhost:8000"}/api/search?${new URLSearchParams({ q: query })}`,
      { signal: AbortSignal.timeout(5000) },
    );
    if (!response.ok) throw new Error("Search API failed");
    const body = await response.json();
    if (!Array.isArray(body.results)) throw new Error("Invalid search response");
    results = body.results;
  } catch {
    error = "Search is unavailable. Check that the shop API is running, then try again.";
  }

  return { query, safe, results, error };
};
