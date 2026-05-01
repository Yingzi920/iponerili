from datetime import date
from .base import CalendarEvent

def plugin_name():
    return "china_movies"

def generate(config):
    sources = config.get("sources", {})
    desc = "\n".join([
        "大陆院线电影抓取槽位：",
        f"猫眼: {sources.get('maoyan', '')}",
        f"淘票票: {sources.get('taopiaopiao', '')}",
        "",
        "扩展方式：抓取片名、上映日期、地区、类型、评分/想看人数，生成上映日全天事件。"
    ])
    return [CalendarEvent(
        title="🎞️ 大陆院线电影抓取模块已启用",
        start=date.today().isoformat(),
        all_day=True,
        description=desc,
        categories=["电影"],
        uid_seed="china-movies-module-enabled"
    )]
