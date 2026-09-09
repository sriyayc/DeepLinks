from fastapi import APIRouter, HTTPException
from urllib.parse import urlparse

router = APIRouter(prefix="/api/deeplinks", tags=["deeplinks"])

ALLOWED_SCHEME = "cybercart"

@router.get("/inspect")
def inspect_link(url: str):
    parsed = urlparse(url)

    if parsed.scheme == ALLOWED_SCHEME:
        destination = parsed.netloc or parsed.path.strip("/").split("/")[0]
        path = parsed.path
    else:
        destination = parsed.netloc
        path = parsed.path

    return {
        "original": url,
        "scheme": parsed.scheme,
        "domain": parsed.netloc,
        "path": path,
        "query": parsed.query,
        "destination": destination,
        "baseline_allowed_scheme": parsed.scheme == ALLOWED_SCHEME,
    }

@router.get("/resolve")
def resolve_link(url: str):
    parsed = urlparse(url)

    if parsed.scheme != ALLOWED_SCHEME:
        raise HTTPException(status_code=400, detail="Unsupported deep-link scheme")

    return {
        "action": parsed.netloc,
        "path": parsed.path,
        "query": parsed.query,
    }
