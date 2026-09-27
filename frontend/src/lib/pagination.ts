export function paginate<T>(items: T[], requestedPage: string | null, pageSize = 6) {
  const totalPages = Math.max(1, Math.ceil(items.length / pageSize));
  const parsed = requestedPage && /^[1-9]\d*$/.test(requestedPage)
    ? Number(requestedPage)
    : 1;
  const currentPage = Math.min(Number.isSafeInteger(parsed) ? parsed : 1, totalPages);
  const startIndex = (currentPage - 1) * pageSize;
  return {
    currentPage,
    totalPages,
    items: items.slice(startIndex, startIndex + pageSize),
    first: items.length ? startIndex + 1 : 0,
    last: Math.min(startIndex + pageSize, items.length),
  };
}

export function pageHref(url: URL, pageNumber: number): string {
  const params = new URLSearchParams(url.searchParams);
  params.set("page", String(pageNumber));
  return `${url.pathname}?${params}`;
}
