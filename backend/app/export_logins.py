import csv
import os
from dotenv import load_dotenv

from .database import SessionLocal
from .models import Participant

load_dotenv()

SHOP_BASE_URL = os.getenv("SHOP_BASE_URL", "http://localhost:5173")


def export_logins(path: str = "participant_logins.csv"):
    db = SessionLocal()
    participants = db.query(Participant).order_by(Participant.id).all()

    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["participant_id", "display_name", "login_url"])
        for p in participants:
            login_url = f"{SHOP_BASE_URL}/login?token={p.access_token}"
            writer.writerow([p.id, p.display_name, login_url])

    db.close()
    print(f"Wrote {len(participants)} login links to {path}")


if __name__ == "__main__":
    export_logins()