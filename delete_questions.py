from app.database.database import SessionLocal
from app.database.models import Question

with SessionLocal() as db:
    deleted = db.query(Question).delete()
    db.commit()
    print(f"Deleted {deleted} questions (options/images cascade-deleted).")
