import asyncio
from repositories.dashboard_repo import repo

async def run_db(fn, *args):
    return await asyncio.to_thread(fn, *args)

async def get_dashboard(user_id):
    stats = await run_db(repo.get_stats, user_id)
    chart = await run_db(repo.get_chart, user_id)
    final_stats = {
        "total_workflows": 0,
        "total_events": 0,
        "success_rate": 0
    }

    # 1- NORMLIZE THE STATS DATA
    for stat in stats:
        final_stats.update({
            "total_workflows": final_stats['total_workflows'] + 1,
            "total_events": final_stats['total_events'] + stat['total_events'],
            "success_rate": (final_stats['success_rate'] + (stat['done_events'] / stat['total_events']) * 100) / (final_stats['total_workflows'] + 1)
        })

    return {
        "success": True,
        "message": "Dashboard",
        "metadata": {
            "stats": final_stats,
            "chart": chart
        }
    }