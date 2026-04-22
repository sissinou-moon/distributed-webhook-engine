from celery import Celery
import psycopg2
from services.db import conn

celery = Celery(
    "worker",
    broker="redis://localhost:6379/0"
)

@celery.task(bind=True, max_retries=3)
def process_event(self, event_id, data):
    try:
        # simulate work (call API / send email...)
        print("Processing:", data)

        # update DB → success
        cur = conn.cursor()
        cur.execute(
            "UPDATE events SET status=%s WHERE id=%s",
            ("Done", event_id)
        )
        conn.commit()

    except Exception as e:
        raise self.retry(exc=e, countdown=5)