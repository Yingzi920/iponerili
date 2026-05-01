from datetime import date, timedelta
try:
    from lunardate import LunarDate
except Exception:
    LunarDate = None
from .base import CalendarEvent

def plugin_name():
    return "core_holidays"

SOLAR_TERMS_SAMPLE = {
    "02-04": "立春", "02-19": "雨水", "03-05": "惊蛰", "03-20": "春分",
    "04-04": "清明", "04-20": "谷雨", "05-05": "立夏", "05-21": "小满",
    "06-05": "芒种", "06-21": "夏至", "07-07": "小暑", "07-22": "大暑",
    "08-07": "立秋", "08-23": "处暑", "09-07": "白露", "09-23": "秋分",
    "10-08": "寒露", "10-23": "霜降", "11-07": "立冬", "11-22": "小雪",
    "12-07": "大雪", "12-21": "冬至", "01-05": "小寒", "01-20": "大寒"
}

GLOBAL_FIXED = {
    "01-01": "元旦 / New Year",
    "02-14": "情人节 / Valentine's Day",
    "03-08": "国际妇女节",
    "04-22": "世界地球日",
    "05-01": "劳动节 / Labour Day",
    "10-31": "万圣节 / Halloween",
    "12-24": "平安夜 / Christmas Eve",
    "12-25": "圣诞节 / Christmas"
}

LUNAR_FESTIVALS = [
    (1, 1, "春节"),
    (1, 15, "元宵节"),
    (5, 5, "端午节"),
    (7, 7, "七夕"),
    (7, 15, "中元节"),
    (8, 15, "中秋节"),
    (9, 9, "重阳节"),
    (12, 8, "腊八节"),
    (12, 23, "北方小年"),
    (12, 24, "南方小年"),
]

def _add_event(events, title, d, desc="", cat="节日"):
    events.append(CalendarEvent(
        title=title,
        start=d.isoformat(),
        all_day=True,
        description=desc,
        categories=[cat],
        uid_seed=f"{cat}-{title}-{d.isoformat()}"
    ))

def generate(config):
    today_year = date.today().year
    years = range(today_year, today_year + int(config.get("years_ahead", 5)))
    events = []
    for y in years:
        for md, title in GLOBAL_FIXED.items():
            m, d = map(int, md.split("-"))
            _add_event(events, f"🌐 {title}", date(y, m, d), cat="全球节日")

        for md, term in SOLAR_TERMS_SAMPLE.items():
            m, d = map(int, md.split("-"))
            _add_event(events, f"🌿 二十四节气：{term}", date(y, m, d), "节气日期为通用近似值，后续可接入精确天文算法。", "节气")

        if LunarDate is not None:
            for lm, ld, name in LUNAR_FESTIVALS:
                try:
                    sd = LunarDate(y, lm, ld).toSolarDate()
                    _add_event(events, f"🏮 农历{name}", sd, f"农历 {lm}月{ld}日", "农历节日")
                except Exception:
                    pass
        else:
            _add_event(events, "🏮 农历节日模块待 GitHub Actions 安装依赖后启用", date(y, 1, 1), "本地未安装 lunardate；上传 GitHub 后会通过 requirements.txt 自动安装并生成准确农历节日。", "农历节日")

    # 2026 official fallback sample; later years can be filled by auto-fetch/manual JSON.
    fallback = {
        "2026-01-01": "元旦休假",
        "2026-02-15": "春节休假开始",
        "2026-02-23": "春节休假结束",
        "2026-04-04": "清明节休假",
        "2026-05-01": "劳动节休假",
        "2026-06-19": "端午节休假",
        "2026-09-25": "中秋节休假",
        "2026-10-01": "国庆节休假开始",
        "2026-10-07": "国庆节休假结束"
    }
    for ds, title in fallback.items():
        _add_event(events, f"🇨🇳 {title}", date.fromisoformat(ds), "中国大陆法定休假/调休数据槽位，可由抓取器自动更新。", "中国休假")
    return events
