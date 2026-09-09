from fastapi import APIRouter
from pydantic import BaseModel
from urllib.parse import urlparse

router = APIRouter(prefix="/api/agent", tags=["agent"])

class LinkRequest(BaseModel):
    url: str

@router.post("/inspect")
def inspect_agent_link(body: LinkRequest):
    parsed = urlparse(body.url)

    # Baseline only: the agent does not execute actions.
    # Add workshop-specific vulnerable/secure policies here.
    return {
        "url": body.url,
        "scheme": parsed.scheme,
        "domain": parsed.netloc,
        "path": parsed.path,
        "query": parsed.query,
        "proposed_action": "VIEW",
        "executed": False,
        "message": "Link inspected; no action executed.",
    }
