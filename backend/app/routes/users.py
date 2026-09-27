from fastapi import APIRouter, Depends, Form, HTTPException, Request, Response
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Participant, UserSession
from ..auth import create_session, set_session_cookie, get_current_user
from ..config import settings

router = APIRouter(prefix="/api", tags=["users"])


@router.get("/login")
def login(token: str, response: Response, db: Session = Depends(get_db)):
    participant = db.query(Participant).filter(Participant.access_token == token).first()
    if not participant:
        raise HTTPException(status_code=401, detail="Invalid login token")

    session_id = create_session(db, participant.id)
    set_session_cookie(response, session_id)

    return {
        "participant_id": participant.id,
        "display_name": participant.display_name,
        "message": "Login successful",
    }


@router.get("/me")
def me(user: Participant = Depends(get_current_user)):
    return {"participant_id": user.id, "display_name": user.display_name}


@router.post("/logout")
def logout(request: Request, response: Response, db: Session = Depends(get_db)):
    session_id = request.cookies.get("session_id")
    if session_id:
        db.query(UserSession).filter(UserSession.session_id == session_id).delete()
        db.commit()
    response.delete_cookie("session_id", path="/")
    return {"message": "Logged out"}


# ---------------------------------------------------------------------------
# TASK 4 — CSRF VULNERABLE ENDPOINT
# ---------------------------------------------------------------------------
# Accepts application/x-www-form-urlencoded so a plain HTML <form> can
# trigger it cross-origin.  There is NO CSRF token — the only protection
# is the session cookie, which has SameSite=None so the browser sends it
# even from a different origin (evil.local / localhost:7000).
# Fix: set SESSION_COOKIE_SAMESITE=lax in .env
# ---------------------------------------------------------------------------
@router.post("/me/update")
def update_profile(
    display_name: str = Form(...),
    db: Session = Depends(get_db),
    user: Participant = Depends(get_current_user),
):
    """
    VULNERABLE — No CSRF token. Accepts form-encoded body.
    Any cross-origin page can silently trigger this while the victim is
    logged in, because the session cookie is SameSite=None.
    """
    if not display_name or len(display_name) > 50:
        raise HTTPException(status_code=400, detail="display_name must be 1–50 chars")

    user.display_name = display_name
    db.commit()
    return {
        "participant_id": user.id,
        "display_name": user.display_name,
        "message": "Profile updated",
    }


@router.get("/lab/csrf-status")
def csrf_status():
    """Returns current cookie SameSite setting so the lab page can show
    whether CSRF is currently exploitable or fixed."""
    samesite = settings.SESSION_COOKIE_SAMESITE
    vulnerable = samesite == "none"
    return {
        "samesite": samesite,
        "secure": settings.SESSION_COOKIE_SECURE,
        "vulnerable": vulnerable,
        "status": "VULNERABLE — SameSite=None sends cookie cross-origin" if vulnerable
                  else f"PROTECTED — SameSite={samesite} blocks cross-origin requests",
    }
