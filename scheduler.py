import time
import sqlite3
import threading
from social_mock import post_to_social
import datetime
DB_NAME = "database.db"

def scheduler_worker():
    while True:
        try:
            conn = sqlite3.connect(DB_NAME)
            c = conn.cursor()
            c.execute("SELECT id, platform, message, image, schedule_time FROM schedules WHERE done = 0")
            jobs = c.fetchall()
            now = datetime.datetime.now()
            for job in jobs:
                job_id, platform, message, image, schedule_time = job
                try:
                    sched_time = datetime.datetime.fromisoformat(schedule_time)
                except Exception:
                    continue
                if now >= sched_time:
                    try:
                        post_to_social(platform, message, image)
                    except Exception:
                        pass
                    c.execute("UPDATE schedules SET done = 1 WHERE id=?", (job_id,))
                    conn.commit()
            conn.close()
        except Exception:
            pass
        time.sleep(5)

def start_scheduler():
    t = threading.Thread(target=scheduler_worker, daemon=True)
    t.start()
