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
    主源：timor.tech 节假日 API。
    注意：该 API 官方说明最多配置到当前时间往后一年的节假日。
    """
    url = f"https://timor.tech/api/holiday/year/{year}?type=Y&week=N"
    try:
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        data = r.json()
        holiday_data = data.get("holiday", {}) or {}
    except Exception:
        return [], []

    holiday_days = []
    work_days = []

    for md, info in holiday_data.items():
        try:
            d = date.fromisoformat(f"{year}-{md}")
        except Exception:
            continue

        name = info.get("name", "中国节假日")
        is_holiday = bool(info.get("holiday", False))

        if is_holiday:
            holiday_days.append((name, d))
        else:
            work_days.append((name, d))

    return sorted(holiday_days, key=lambda x: x[1]), sorted(work_days, key=lambda x: x[1])


GLOBAL_FIXED = {
    "01-01": "元旦 / New Year",
    "02-14": "情人节 / Valentine’s Day",
    "03-08": "国际妇女节",
    "03-15": "消费者权益日",
    "04-01": "愚人节 / April Fool’s Day",
    "04-22": "世界地球日",
    "05-01": "劳动节 / Labour Day",
    "06-01": "儿童节",
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


def add_rule_based_global_festivals(events, year):
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


def add_china_holidays(events, year):
    holiday_days, work_days = fetch_china_holidays(year)

    for name, d in holiday_days:
        _add_event(
            events,
            f"🇨🇳 {name}休假",
            d,
            "联网自动抓取：中国大陆法定节假日/调休休假日。",
            "中国休假"
        )

    for name, d in work_days:
        _add_event(
            events,
            f"⚠️ {name}调休上班",
            d,
            "联网自动抓取：中国大陆调休补班日。",
            "调休补班"
        )


def generate(config):
    events = []
    current_year = date.today().year
    years_ahead = int(config.get("years_ahead", 5))

    for y in range(current_year, current_year + years_ahead):
        for md, name in GLOBAL_FIXED.items():
            m, d = map(int, md.split("-"))
            _add_event(events, f"🌐 {name}", date(y, m, d), "", "全球节日")

        add_rule_based_global_festivals(events, y)

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

        add_china_holidays(events, y)

    return events