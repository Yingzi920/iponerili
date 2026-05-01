import importlib
import json
import hashlib
from pathlib import Path
from datetime import datetime, timedelta

ROOT = Path(__file__).resolve().parent
CONFIG = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))

def esc(s):
    return str(s or "").replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")

def fold(line):
    # RFC5545 line folding
    b = line.encode("utf-8")
    if len(b) <= 73:
        return line
    out, cur = [], ""
    for ch in line:
        if len((cur + ch).encode("utf-8")) > 73:
            out.append(cur)
            cur = " " + ch
        else:
            cur += ch
    out.append(cur)
    return "\r\n".join(out)

def uid(seed):
    return hashlib.sha1(seed.encode("utf-8")).hexdigest() + "@ying-calendar"

def event_to_ics(ev):
    lines = ["BEGIN:VEVENT"]
    lines.append(f"UID:{uid(ev.uid_seed or ev.title + ev.start)}")
    lines.append(f"DTSTAMP:{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}")
    lines.append(f"SUMMARY:{esc(ev.title)}")
    if ev.all_day:
        lines.append(f"DTSTART;VALUE=DATE:{ev.start.replace('-', '')}")
        try:
            from datetime import date
            d = date.fromisoformat(ev.start[:10]) + timedelta(days=1)
            lines.append(f"DTEND;VALUE=DATE:{d.isoformat().replace('-', '')}")
        except Exception:
            pass
    else:
        # Floating local time; Apple Calendar uses subscriber timezone.
        lines.append(f"DTSTART:{ev.start.replace('-', '').replace(':', '')}")
    if ev.description:
        lines.append(f"DESCRIPTION:{esc(ev.description)}")
    if ev.location:
        lines.append(f"LOCATION:{esc(ev.location)}")
    if ev.categories:
        lines.append(f"CATEGORIES:{esc(','.join(ev.categories))}")
    lines.append("END:VEVENT")
    return "\r\n".join(fold(x) for x in lines)

def load_events():
    events = []
    for name in CONFIG.get("enabled_plugins", []):
        mod = importlib.import_module(f"plugins.{name}")
        events.extend(mod.generate(CONFIG))
    return events

def main():
    events = load_events()
    cal_lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Ying Smart Calendar//CN Global Lunar AI Movies//ZH",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        f"X-WR-CALNAME:{esc(CONFIG.get('calendar_name', '智能日历'))}",
        f"X-WR-TIMEZONE:{esc(CONFIG.get('timezone', 'Asia/Shanghai'))}",
    ]
    for ev in events:
        cal_lines.append(event_to_ics(ev))
    cal_lines.append("END:VCALENDAR")
    (ROOT / "calendar.ics").write_text("\r\n".join(cal_lines) + "\r\n", encoding="utf-8")
    print(f"Generated calendar.ics with {len(events)} events.")

if __name__ == "__main__":
    main()
