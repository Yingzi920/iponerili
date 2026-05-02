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


def daterange(start, end):
    d = start
    while d <= end:
        yield d
        d += timedelta(days=1)


# 兜底：2026 官方放假调休
CHINA_FALLBACK_HOLIDAYS = {
    2026: [
        ("元旦", "2026-01-01", "2026-01-03"),
        ("春节", "2026-02-15", "2026-02-23"),
        ("清明节", "2026-04-04", "2026-04-06"),
        ("劳动节", "2026-05-01", "2026-05-05"),
        ("端午节", "2026-06-19", "2026-06-21"),
        ("中秋节", "2026-09-25", "2026-09-27"),
        ("国庆节", "2026-10-01", "2026-10-07"),
    ]
}

CHINA_FALLBACK_WORKDAYS = {
    2026: [
        ("元旦", "2026-01-04"),
        ("春节", "2026-02-14"),
        ("春节", "2026-02-28"),
        ("劳动节", "2026-05-09"),
        ("国庆节", "2026-09-20"),
        ("国庆节", "2026-10-10"),
    ]
}


def fetch_china_holidays(year):
    url = f"https://timor.tech/api/holiday/year/{year}"

    holiday_days = []
    work_days = []

    try:
        r = requests.get(url, timeout=12)
        r.raise_for_status()
        data = r.json().get("holiday", {}) or {}

        for md, info in data.items():
            try:
                d = date.fromisoformat(f"{year}-{md}")
            except Exception:
                continue

            name = info.get("name", "假期")
            type_code = info.get("type", 0)

            if type_code == 1 or (type_code == 2 and name):
                holiday_days.append((name, d))
            elif type_code == 0 and name:
                work_days.append((name, d))

    except Exception:
        pass

    return holiday_days, work_days


def apply_fallback_if_needed(year, holiday_days, work_days):
    existing = {d for _, d in holiday_days}

    for name, start_s, end_s in CHINA_FALLBACK_HOLIDAYS.get(year, []):
        start = date.fromisoformat(start_s)
        end = date.fromisoformat(end_s)

        full_range = list(daterange(start, end))
        missing_count = sum(1 for d in full_range if d not in existing)

        # 只要这个假期区间缺任何一天，就用兜底补全整段
        if missing_count > 0:
            for d in full_range:
                holiday_days.append((name, d))
                existing.add(d)

    existing_work = {d for _, d in work_days}
    for name, day_s in CHINA_FALLBACK_WORKDAYS.get(year, []):
        d = date.fromisoformat(day_s)
        if d not in existing_work:
            work_days.append((name, d))

    return holiday_days, work_days


def merge_same_day(items):
    result = {}
    for name, d in items:
        result.setdefault(d, name)
    return [(name, d) for d, name in result.items()]


def group_ranges(items):
    if not items:
        return []

    items = sorted(items, key=lambda x: x[1])
    ranges = []

    start_name, start = items[0]
    prev = start

    for name, d in items[1:]:
        if (d - prev).days == 1 and name == start_name:
            prev = d
        else:
            ranges.append((start_name, start, prev))
            start_name, start = name, d
            prev = d

    ranges.append((start_name, start, prev))
    return ranges


def add_china_holidays(events, year):
    holiday_days, work_days = fetch_china_holidays(year)
    holiday_days, work_days = apply_fallback_if_needed(year, holiday_days, work_days)

    holiday_days = merge_same_day(holiday_days)
    work_days = merge_same_day(work_days)

    for name, start, end in group_ranges(holiday_days):
        total = (end - start).days + 1
        d = start
        idx = 1

        while d <= end:
            _add_event(
                events,
                f"🇨🇳 {name}休假（第{idx}/{total}天）",
                d,
                f"{start} 至 {end}。联网抓取，不完整时自动兜底补全。",
                "中国休假"
            )
            d += timedelta(days=1)
            idx += 1

    for name, d in work_days:
        _add_event(
            events,
            f"⚠️ {name}调休上班",
            d,
            "中国大陆调休补班日。",
            "调休补班"
        )


GLOBAL_FIXED = {
    "01-01": "元旦 / New Year",
    "02-14": "情人节 / Valentine’s Day",
    "03-08": "国际妇女节",
    "03-15": "消费者权益日",
    "04-01": "愚人节 / April Fool’s Day",
    "04-22": "世界地球日",
    "05-01": "劳动节 / Labour Day",
    "06-01": "儿童节",
    "10-01": "国庆节",
    "10-31": "万圣节 / Halloween",
    "11-11": "光棍节 / Singles’ Day",
    "12-24": "平安夜 / Christmas Eve",
    "12-25": "圣诞节 / Christmas",
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


def add_global_fixed(events, year):
    for md, name in GLOBAL_FIXED.items():
        m, d = map(int, md.split("-"))
        _add_event(events, f"🌐 {name}", date(year, m, d), "", "全球节日")


def add_rule_based_global(events, year):
    thanksgiving = nth_weekday(year, 11, 3, 4)

    rules = [
        ("👩 母亲节 / Mother’s Day", nth_weekday(year, 5, 6, 2), "每年5月第二个星期日"),
        ("👨 父亲节 / Father’s Day", nth_weekday(year, 6, 6, 3), "每年6月第三个星期日"),
        ("🙏 感恩节 / Thanksgiving", thanksgiving, "美国感恩节：每年11月第四个星期四"),
        ("💻 黑色星期五 / Black Friday", thanksgiving + timedelta(days=1), "感恩节次日"),
        ("🌐 网络星期一 / Cyber Monday", thanksgiving + timedelta(days=4), "感恩节后的星期一"),
    ]

    for title, d, desc in rules:
        _add_event(events, title, d, desc, "全球节日")


def add_lunar(events, year):
    if LunarDate is None:
        return

    for lm, ld, name in LUNAR_FESTIVALS:
        try:
            sd = LunarDate(year, lm, ld).toSolarDate()
            _add_event(events, f"🏮 农历{name}", sd, f"农历 {lm}月{ld}日", "农历节日")
        except Exception:
            pass


def add_solar_terms(events, year):
    for md, name in SOLAR_TERMS_SAMPLE.items():
        m, d = map(int, md.split("-"))
        _add_event(events, f"🌿 二十四节气：{name}", date(year, m, d), "节气日期为通用近似值。", "节气")


def generate(config):
    events = []
    current_year = date.today().year
    years_ahead = int(config.get("years_ahead", 5))

    for year in range(current_year, current_year + years_ahead):
        add_global_fixed(events, year)
        add_rule_based_global(events, year)
        add_lunar(events, year)
        add_solar_terms(events, year)
        add_china_holidays(events, year)

    return events