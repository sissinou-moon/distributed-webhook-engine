import psycopg2.extras
from services.db import conn

class DashboardRepo:

    def get_stats(self, user_id):
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("""
            SELECT * FROM get_active_workflows(%s::UUID);
        """, (user_id,))
        rows = cur.fetchall()
        return [dict(row) for row in rows]

    def get_chart(self, user_id):
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("""
            SELECT DATE(date), COUNT(*) as events
            FROM events
            WHERE user_id = %s
            GROUP BY DATE(date)
            ORDER BY DATE(date) DESC
            LIMIT 7
        """, (user_id,))
        return [dict(row) for row in cur.fetchall()]

    def get_integrations(self, user_id):
        cur = conn.cursor()
        cur.execute("""
            SELECT app_id
            FROM integrations
            WHERE user_id = %s
        """, (user_id,))
        return [row[0] for row in cur.fetchall()]

    def get_last_events(self, user_id):
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("""
            SELECT id, date, status, metadata
            FROM events
            WHERE user_id = %s
            ORDER BY Date(date) DESC
            LIMIT 7
        """, (user_id,))
        return [dict(row) for row in cur.fetchall()]


repo = DashboardRepo()