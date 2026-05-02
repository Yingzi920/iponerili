from datetime import date
from .base import CalendarEvent
import json
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE_DIR = ROOT / "data" / "cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

def plugin_name():
    return "ai_news"

def fetch_url(url, timeout=20):
    try:
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "YingSmartCalendar/1.0"
            }
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read().decode("utf-8", errors="ignore")
    except Exception as e:
        return f"[ERROR] {url} -> {e}"

def parse_rss(url, limit=5):
    text = fetch_url(url)
    if text.startswith("[ERROR]"):
        return [text]

    items = []
    try:
        root = ET.fromstring(text)
        for item in root.findall(".//item")[:limit]:
            title = item.findtext("title") or ""
            link = item.findtext("link") or ""
            if title:
                items.append(f"- {title}\n  {link}")
    except Exception as e:
        items.append(f"[RSS解析失败] {url} -> {e}")

    return items or [f"[无内容] {url}"]

def fetch_github_releases(repo, limit=5):
    url = f"https://api.github.com/repos/{repo}/releases"
    text = fetch_url(url)
    if text.startswith("[ERROR]"):
        return [text]

    try:
        data = json.loads(text)
        items = []
        for r in data[:limit]:
            name = r.get("name") or r.get("tag_name") or "release"
            html = r.get("html_url", "")
            items.append(f"- {repo}: {name}\n  {html}")
        return items or [f"[无 release] {repo}"]
    except Exception as e:
        return [f"[GitHub解析失败] {repo} -> {e}"]

def fetch_openrouter_rankings():
    url = "https://openrouter.ai/rankings"
    text = fetch_url(url)

    if text.startswith("[ERROR]"):
        return [text]

    # OpenRouter 页面是动态网页，这里先做保守抓取：
    # 能访问则提示页面可用；深度模型榜单解析后续可接 OpenRouter API 或页面解析。
    if "openrouter" in text.lower() or "rankings" in text.lower():
        return [
            "- OpenRouter Rankings 页面可访问",
            "  https://openrouter.ai/rankings"
        ]

    return ["- OpenRouter Rankings 页面已抓取，但未解析出结构化内容"]

def generate(config):
    today = date.today().isoformat()
    sources = config.get("sources", {})

    sections = []

    sections.append("【OpenRouter 模型榜】")
    sections.extend(fetch_openrouter_rankings())

    sections.append("")
    sections.append("【OpenAI / ChatGPT 动态】")
    openai_rss = sources.get("openai_news") or "https://openai.com/news/rss.xml"
    sections.extend(parse_rss(openai_rss, limit=5))

    sections.append("")
    sections.append("【Codex / OpenAI GitHub】")
    sections.extend(fetch_github_releases("openai/codex", limit=3))

    sections.append("")
    sections.append("【OpenClaw Releases】")
    openclaw_repo = sources.get("openclaw_repo") or sources.get("openclaw_releases_repo") or ""
    if openclaw_repo:
        sections.extend(fetch_github_releases(openclaw_repo, limit=5))
    else:
        sections.append("- 未配置 openclaw_repo，例如：owner/repo")

    desc = "\n".join(sections)

    cache = {
        "date": today,
        "summary": desc
    }
    (CACHE_DIR / "ai_news.json").write_text(
        json.dumps(cache, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    return [CalendarEvent(
        title="🤖 AI 简报：模型/ChatGPT/Codex/OpenClaw",
        start=today,
        all_day=False,
        description=desc,
        categories=["AI简报"],
        uid_seed=f"ai-news-{today}"
    )]