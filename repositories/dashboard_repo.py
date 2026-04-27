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

    async def get_chart(self, user_id):
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("""
            SELECT DATE(created_at) as date, COUNT(*) as events
            FROM events
            WHERE user_id = %s
            GROUP BY date
            ORDER BY date DESC
            LIMIT 7
        """, (user_id,))
        return [dict(row) for row in cur.fetchall()]

    async def get_integrations_count(self, user_id):
        cur = conn.cursor()
        cur.execute("""
            SELECT COUNT(*) FROM integrations WHERE user_id = %s
        """, (user_id,))
        return cur.fetchone()[0]

    async def get_last_events(self, user_id):
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("""
            SELECT id, name, created_at
            FROM events
            WHERE user_id = %s
            ORDER BY created_at DESC
            LIMIT 3
        """, (user_id,))
        return [dict(row) for row in cur.fetchall()]


repo = DashboardRepo()