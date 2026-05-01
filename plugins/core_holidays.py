from datetime import date, timedelta
import requests

try:
    from lunardate import LunarDate
except Exception:
    LunarDate = None

from .base import CalendarEvent


def plugin_name():
    return "core_holidays"


def _add_event(events, title, d, desc="", cat="节日"):
    events.append(CalendarEvent(
        title=title,
        start=d.isoformat(),
        all_day=True,
        description=desc,
        categories=[cat],
        uid_seed=f"{cat}-{title}-{d.isoformat()}"
    ))


def nth_weekday(year, month, weekday, n):
    d = date(year, month, 1)
    while d.weekday() != weekday:
        d += timedelta(days=1)
    return d + timedelta(days=7 * (n - 1))


def fetch_china_holidays(year):
    """
    自动抓取中国大陆节假日/调休。
    使用 timor.tech 免费节假日 API；失败则返回空结果。
    """
    url = f"https://timor.tech/api/holiday/year/{year}"
    try:
        r = requests.get(url, timeout=12)
        r.raise_for_status()
        data = r.json()
        holidays = data.get("holiday", {}) or {}
    except Exception:
        return [], []

    holiday_days = []
    work_days = []

    for md, info in holidays.items():
        d = date.fromisoformat(f"{year}-{md}")

        name = info.get("name", "中国节假日")
        is_holiday = info.get("holiday", False)

        if is_holiday:
            holiday_days.append((name, d))
        else:
            work_days.append((name, d))

    return holiday_days, work_days


GLOBAL_FIXED = {
    "01-01": "元旦",
    "02-14": "情人节",
    "03-08": "妇女节",
    "04-01": "愚人节",
    "04-22": "世界地球日",
    "05-01": "劳动节",
    "06-01": "儿童节",
    "10-01": "国庆节",
    "10-31": "万圣节",
    "11-11": "光棍节",
    "12-24": "平安夜",
    "12-25": "圣诞节",
}

LUNAR_FESTIVALS = [
    (1, 1, "春节"),
    (1, 15, "元宵节"),
    (2, 2, "龙抬头"),
    (5, 5, "端午节"),
    (7, 7, "七夕"),
    (7, 15, "中元节"),
    (8, 15, "中秋节"),
    (9, 9, "重阳节"),
    (12, 8, "腊八节"),
    (12, 23, "北方小年"),
    (12, 24, "南方小年"),
]

SOLAR_TERMS_SAMPLE = {
    "01-05": "小寒", "01-20": "大寒",
    "02-04": "立春", "02-19": "雨水",
    "03-05": "惊蛰", "03-20": "春分",
    "04-04": "清明", "04-20": "谷雨",
    "05-05": "立夏", "05-21": "小满",
    "06-05": "芒种", "06-21": "夏至",
    "07-07": "小暑", "07-22": "大暑",
    "08-07": "立秋", "08-23": "处暑",
    "09-07": "白露", "09-23": "秋分",
    "10-08": "寒露", "10-23": "霜降",
    "11-07": "立冬", "11-22": "小雪",
    "12-07": "大雪", "12-21": "冬至",
}


def add_rule_based_festivals(events, year):
    rules = [
        ("👩 母亲节", nth_weekday(year, 5, 6, 2), "每年5月第二个星期日"),
        ("👨 父亲节", nth_weekday(year, 6, 6, 3), "每年6月第三个星期日"),
        ("🙏 感恩节", nth_weekday(year, 11, 3, 4), "每年11月第四个星期四"),
        ("💻 黑色星期五", nth_weekday(year, 11, 3, 4) + timedelta(days=1), "感恩节次日"),
    ]

    for title, d, desc in rules:
        _add_event(events, title, d, desc, "全球节日")


def generate(config):
    events = []
    current_year = date.today().year
    years_ahead = int(config.get("years_ahead", 5))

    for y in range(current_year, current_year + years_ahead):
        for md, name in GLOBAL_FIXED.items():
            m, d = map(int, md.split("-"))
            _add_event(events, f"🌐 {name}", date(y, m, d), "", "全球节日")

        add_rule_based_festivals(events, y)

        for md, name in SOLAR_TERMS_SAMPLE.items():
            m, d = map(int, md.split("-"))
            _add_event(events, f"🌿 二十四节气：{name}", date(y, m, d), "节气日期为通用近似值。", "节气")

        if LunarDate:
            for lm, ld, name in LUNAR_FESTIVALS:
                try:
                    sd = LunarDate(y, lm, ld).toSolarDate()
                    _add_event(events, f"🏮 农历{name}", sd, f"农历 {lm}月{ld}日", "农历节日")
                except Exception:
                    pass

        holiday_days, work_days = fetch_china_holidays(y)

        for name, d in holiday_days:
            _add_event(
                events,
                f"🇨🇳 {name}休假",
                d,
                "自动抓取：中国大陆法定节假日/调休休假日。",
                "中国休假"
            )

        for name, d in work_days:
            _add_event(
                events,
                f"⚠️ {name}调休上班",
                d,
                "自动抓取：中国大陆调休补班日。",
                "调休补班"
            )

    return events