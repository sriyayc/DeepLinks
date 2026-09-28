from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Participant
from ..auth import get_current_user

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/users")
def list_all_users(
    strict_authz: bool = Query(
        default=False,
        description="Enable the role check for the workshop comparison.",
    ),
    db: Session = Depends(get_db),
    user: Participant = Depends(get_current_user),
):
    """Return all participants.

    INTENTIONAL VULNERABILITY: any authenticated user can access this
    admin-only endpoint.  When ``strict_authz=true`` the endpoint
    enforces ``role == 'admin'`` and returns 403 for regular participants.
    """
    if strict_authz and user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    participants = db.query(Participant).order_by(Participant.id).all()
    return [
        {
            "id": p.id,
            "display_name": p.display_name,
            "email": f"participant{p.id}@cybercart.workshop",
            "role": p.role,
        }
        for p in participants
    ]
