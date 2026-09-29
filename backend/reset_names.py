import sys
import os

from app.database import SessionLocal
from app.models import Participant

db = SessionLocal()
participants = db.query(Participant).all()

for p in participants:
    if p.id != 1000:
        p.display_name = f"participant{p.id}"

db.commit()
db.close()
print("Display names reset successfully.")
