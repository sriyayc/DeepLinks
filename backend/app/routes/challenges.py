"""CTF scoring + leaderboard.

Self-contained: only touches the new ``challenge_events`` table. Grading of the
puzzles stays client-side (workshop, not a competitive CTF); these endpoints
record a solve (+points) or a hint reveal (-points), once each per participant
per challenge, and expose the leaderboard.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..auth import get_current_user
from ..database import get_db
from ..models import ChallengeEvent, Participant

router = APIRouter(prefix="/api/challenges", tags=["challenges"])

# (points for solving, cost of revealing the hint) by difficulty tier.
EASY = (50, 10)
MEDIUM = (100, 25)
HARD = (200, 50)

# challenge id -> tier. Keep in sync with frontend challenges.ts (challengeTier).
CHALLENGES = {
    "rot13-intro": EASY,
    "parceltrack-idor": EASY,
    "pocket-pad": EASY,
    "streetlights": EASY,
    "runaway": MEDIUM,
    "behind-the-page": EASY,
    "concert-leak": EASY,
    "encrypted-tea": EASY,
    "lost-laptop": EASY,
}


class ChallengeRef(BaseModel):
    challenge_id: str


def _score(db: Session, participant_id: int) -> int:
    total = (
        db.query(func.coalesce(func.sum(ChallengeEvent.points), 0))
        .filter(ChallengeEvent.participant_id == participant_id)
        .scalar()
    )
    return int(total or 0)


def _record(db: Session, participant_id: int, challenge_id: str, kind: str, points: int):
    """Insert one event if this (participant, challenge, kind) has none yet."""
    existing = (
        db.query(ChallengeEvent)
        .filter(
            ChallengeEvent.participant_id == participant_id,
            ChallengeEvent.challenge_id == challenge_id,
            ChallengeEvent.kind == kind,
        )
        .first()
    )
    if existing:
        return False
    db.add(
        ChallengeEvent(
            participant_id=participant_id,
            challenge_id=challenge_id,
            kind=kind,
            points=points,
        )
    )
    db.commit()
    return True


@router.post("/solve")
def solve(
    body: ChallengeRef,
    db: Session = Depends(get_db),
    user: Participant = Depends(get_current_user),
):
    tier = CHALLENGES.get(body.challenge_id)
    if not tier:
        raise HTTPException(status_code=404, detail="Unknown challenge")
    added = _record(db, user.id, body.challenge_id, "solve", tier[0])
    return {"awarded": tier[0] if added else 0, "already": not added, "score": _score(db, user.id)}


@router.post("/hint")
def hint(
    body: ChallengeRef,
    db: Session = Depends(get_db),
    user: Participant = Depends(get_current_user),
):
    tier = CHALLENGES.get(body.challenge_id)
    if not tier:
        raise HTTPException(status_code=404, detail="Unknown challenge")
    added = _record(db, user.id, body.challenge_id, "hint", -tier[1])
    return {"cost": tier[1] if added else 0, "already": not added, "score": _score(db, user.id)}


@router.get("/me")
def my_progress(
    db: Session = Depends(get_db),
    user: Participant = Depends(get_current_user),
):
    events = (
        db.query(ChallengeEvent)
        .filter(ChallengeEvent.participant_id == user.id)
        .all()
    )
    return {
        "score": sum(e.points for e in events),
        "solved": [e.challenge_id for e in events if e.kind == "solve"],
        "hinted": [e.challenge_id for e in events if e.kind == "hint"],
    }


@router.get("/leaderboard")
def leaderboard(db: Session = Depends(get_db)):
    rows = (
        db.query(
            Participant.id,
            Participant.display_name,
            func.coalesce(func.sum(ChallengeEvent.points), 0).label("score"),
        )
        .join(ChallengeEvent, ChallengeEvent.participant_id == Participant.id)
        .group_by(Participant.id, Participant.display_name)
        .order_by(func.coalesce(func.sum(ChallengeEvent.points), 0).desc())
        .limit(20)
        .all()
    )
    return [
        {"participant_id": r[0], "display_name": r[1], "score": int(r[2])}
        for r in rows
    ]
