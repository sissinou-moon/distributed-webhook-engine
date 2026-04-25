from celery import Celery
import psycopg2
from services.db import conn
import psycopg2.extras
from actions.send_email import send_email
from actions.notion import createDatabase

celery = Celery(
    "worker",
    broker="redis://localhost:6379/0"
)

@celery.task(bind=True, max_retries=3)
def process_event(self, event_id, data, workflow, integrations):
    try:
        # CALL API / OR SEND EMAIL
        print("Processing:", data)
        
        for action in workflow.get("steps"):
            if dict(action).get("action") == "send_email":
                send_email(dict(action).get("to_email"), dict(action).get("subject"), dict(action).get("body"), dict(action).get("from_email"))
            elif dict(action).get("action") == "notion_create_database":
                for integration in integrations:
                    if integration.get("app_id") == 1:
                        print("Creating Database ⏳")
                        result = createDatabase(dict(action).get("page_id"), dict(action).get("title"), dict(integration.get("metadata")).get("access_token"))
                        print(result)

        # 2- UPDATE THE STATUS OF THE EVENT IN DB
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute(
            "UPDATE events SET status=%s WHERE id=%s",
            ("Done", event_id)
        )
        conn.commit()

        print("TASK RECEIVED")

    except Exception as e:
        raise self.retry(exc=e, countdown=5)