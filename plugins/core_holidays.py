from datetime import date, timedelta

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


def last_weekday(year, month, weekday):
    if month < 12:
        d = date(year, month + 1, 1) - timedelta(days=1)
    else:
        d = date(year, 12, 31)
    while d.weekday() != weekday:
        d -= timedelta(days=1)
    return d


GLOBAL_FIXED = {
    "01-01": "元旦",
    "02-14": "情人节",
    "03-08": "妇女节",
    "04-01": "愚人节",
    "05-01": "劳动节",
    "06-01": "儿童节",
    "10-01": "国庆节",
    "12-25": "圣诞节",
}


LUNAR_FESTIVALS = [
    (1, 1, "春节"),
    (1, 15, "元宵节"),
    (5, 5, "端午节"),
    (8, 15, "中秋节"),
    (9, 9, "重阳节"),
]


SOLAR_TERMS_SAMPLE = {
    "02-04": "立春",
    "03-20": "春分",
    "06-21": "夏至",
    "09-23": "秋分",
    "12-21": "冬至",
}


def add_rule_based_festivals(events, year):
    rules = [
        ("👩 母亲节", nth_weekday(year, 5, 6, 2)),
        ("👨 父亲节", nth_weekday(year, 6, 6, 3)),
        ("🙏 感恩节", nth_weekday(year, 11, 3, 4)),
    ]

    for title, d in rules:
        _add_event(events, title, d, "", "全球节日")


def add_china_holidays(events):
    HOLIDAYS_2026 = [
        ("元旦休假", "2026-01-01", "2026-01-03"),
        ("春节休假", "2026-02-15", "2026-02-23"),
        ("清明节休假", "2026-04-04", "2026-04-06"),
        ("劳动节休假", "2026-05-01", "2026-05-05"),
        ("端午节休假", "2026-06-19", "2026-06-21"),
        ("中秋节休假", "2026-09-25", "2026-09-27"),
        ("国庆节休假", "2026-10-01", "2026-10-07"),
    ]

    WORKDAYS_2026 = [
        "2026-01-04",
        "2026-02-14",
        "2026-02-28",
        "2026-05-09",
        "2026-09-20",
        "2026-10-10",
    ]

    def add_range(title, start, end):
        d = date.fromisoformat(start)
        end_d = date.fromisoformat(end)
        while d <= end_d:
            _add_event(events, f"🇨🇳 {title}", d, "", "中国休假")
            d += timedelta(days=1)

    for title, s, e in HOLIDAYS_2026:
        add_range(title, s, e)

    for d in WORKDAYS_2026:
        _add_event(events, "⚠️ 调休上班", date.fromisoformat(d), "", "补班")


def generate(config):
    events = []
    current_year = date.today().year

    for y in range(current_year, current_year + 3):
        for md, name in GLOBAL_FIXED.items():
            m, d = map(int, md.split("-"))
            _add_event(events, name, date(y, m, d))

        add_rule_based_festivals(events, y)

        for md, name in SOLAR_TERMS_SAMPLE.items():
            m, d = map(int, md.split("-"))
            _add_event(events, f"节气：{name}", date(y, m, d))

        if LunarDate:
            for lm, ld, name in LUNAR_FESTIVALS:
                try:
                    sd = LunarDate(y, lm, ld).toSolarDate()
                    _add_event(events, f"农历{name}", sd)
                except:
                    pass

    add_china_holidays(events)

    return events