from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel
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
        "role": participant.role,
        "message": "Login successful",
    }


class IdLoginRequest(BaseModel):
    participant_id: int
    password: str


@router.post("/login-id")
def login_with_id(body: IdLoginRequest, response: Response, db: Session = Depends(get_db)):
    """Simple workshop login: numeric participant ID + a shared password.

    Lets participants sign in with the number handed to them instead of a long
    token link. The shared password means anyone who knows an ID can sign in as
    it — acceptable for a workshop, and it does not affect any lab.
    """
    if body.password != settings.WORKSHOP_PASSWORD:
        raise HTTPException(status_code=401, detail="Incorrect workshop password")

    participant = db.query(Participant).filter(Participant.id == body.participant_id).first()
    if not participant:
        raise HTTPException(status_code=401, detail="Unknown participant ID")

    session_id = create_session(db, participant.id)
    set_session_cookie(response, session_id)

    return {
        "participant_id": participant.id,
        "display_name": participant.display_name,
        "role": participant.role,
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
    response.delete_cookie(
        "session_id",
        path="/",
        httponly=settings.SESSION_COOKIE_HTTPONLY,
        samesite=settings.SESSION_COOKIE_SAMESITE,
        secure=settings.SESSION_COOKIE_SECURE,
    )
    return {"message": "Logged out"}


@router.get("/lab/csrf-status")
def csrf_status():
    """Describe the deliberately unprotected state-changing endpoint."""
    samesite = settings.SESSION_COOKIE_SAMESITE
    return {
        "samesite": samesite,
        "secure": settings.SESSION_COOKIE_SECURE,
        "vulnerable": True,
        "cross_site_cookie_allowed": samesite == "none",
        "status": "VULNERABLE — the shipping-address endpoint requires no CSRF token",
    }
