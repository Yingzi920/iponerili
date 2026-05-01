from datetime import date, timedelta
from .base import CalendarEvent

def plugin_name():
    return "daily_life"

def _timed_event(title, day, hhmm, desc, cat):
    return CalendarEvent(
        title=title,
        start=f"{day.isoformat()}T{hhmm}:00",
        end=f"{day.isoformat()}T{hhmm}:00",
        all_day=False,
        description=desc,
        categories=[cat],
        uid_seed=f"{cat}-{title}-{day.isoformat()}-{hhmm}"
    )

def generate(config):
    life = config.get("daily_life", {})
    today = date.today()
    events = []
    for i in range(0, 370):
        d = today + timedelta(days=i)
        events.append(_timed_event("🔥 抖音续火花", d, life.get("douyin_streak_time", "21:00"), "每日固定提醒：打开抖音续火花。", "生活提醒"))
        events.append(_timed_event("🤖 AI 简报：模型/ChatGPT/Codex/OpenClaw", d, life.get("ai_briefing_time", "08:30"), "动态内容由 ai_news 插件写入摘要缓存；此事件用于每天查看。", "AI简报"))
        events.append(_timed_event("🎬 大陆院线电影速览", d, life.get("movie_digest_time", "19:30"), "动态内容由 china_movies 插件写入摘要缓存；此事件用于每天查看。", "电影"))
    return events
