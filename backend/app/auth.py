import secrets
from fastapi import Request, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from .database import get_db
from .models import Participant, UserSession
from .config import settings


def get_current_user(request: Request, db: Session = Depends(get_db)) -> Participant:
    session_id = request.cookies.get("session_id")
    if not session_id:
        raise HTTPException(status_code=401, detail="Login required")

    session = db.query(UserSession).filter(UserSession.session_id == session_id).first()
    if not session:
        raise HTTPException(status_code=401, detail="Invalid or expired session")

    participant = db.query(Participant).filter(Participant.id == session.participant_id).first()
    if not participant:
        raise HTTPException(status_code=401, detail="Unknown participant")

    return participant


def create_session(db: Session, participant_id: int) -> str:
    session_id = secrets.token_hex(24)
    db.add(UserSession(session_id=session_id, participant_id=participant_id))
    db.commit()
    return session_id


def set_session_cookie(response: Response, session_id: str) -> None:
    response.set_cookie(
        key="session_id",
        value=session_id,
        httponly=settings.SESSION_COOKIE_HTTPONLY,
        samesite=settings.SESSION_COOKIE_SAMESITE,
        secure=settings.SESSION_COOKIE_SECURE,
        max_age=60 * 60 * 8,
        path="/",
    )