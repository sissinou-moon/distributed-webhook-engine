import psycopg2.extras
import asyncio
from repositories.dashboard_repo import repo
from services.db import conn

async def run_db(fn, *args):
    return await asyncio.to_thread(fn, *args)

async def get_dashboard(user_id):
    stats = await run_db(repo.get_stats, user_id)
    chart = await run_db(repo.get_chart, user_id)
    integrations = await run_db(repo.get_integrations, user_id)
    last_events = await run_db(repo.get_last_events, user_id)


    final_stats = {
        "total_workflows": 0,
        "total_events": 0,
        "success_rate": 0
    }

    try:
        # 1- NORMLIZE THE STATS DATA
        for stat in stats:
            final_stats.update({
                "total_workflows": final_stats['total_workflows'] + 1,
                "total_events": final_stats['total_events'] + stat['total_events'],
                "success_rate": (final_stats['success_rate'] + (stat['done_events'] / stat['total_events']) * 100) / (final_stats['total_workflows'] + 1)
            })

        # 2- FETCH THE APP INTEGRATIONS
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("SELECT * FROM apps WHERE id = ANY(%s)", (integrations,))
        integration_details = cur.fetchall()
        cur.close()
    except Exception as e:
        raise e
    # end try

    return {
        "success": True,
        "message": "Dashboard",
        "metadata": {
            "stats": final_stats,
            "chart": chart,
            "integrations": [dict(app) for app in integration_details],
            "last_events": last_events
        }
    }