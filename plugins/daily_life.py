from datetime import date, timedelta
from .base import CalendarEvent

def plugin_name():
    return "daily_life"

def _event(title, d, time):
    return CalendarEvent(
        title=title,
        start=f"{d.isoformat()}T{time}:00",
        all_day=False,
        description="",
        categories=["生活提醒"],
        uid_seed=f"{title}-{d}-{time}"
    )

def generate(config):
    today = date.today()
    events = []

    for i in range(0, 365):
        d = today + timedelta(days=i)

        # 🔥 抖音续火花
        events.append(_event("🔥 抖音续火花", d, "21:00"))

        # 💊 吃药提醒
        events.append(_event("💊 吃药提醒", d, "16:30"))

    return events