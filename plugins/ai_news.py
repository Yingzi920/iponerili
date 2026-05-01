from datetime import date
from .base import CalendarEvent

def plugin_name():
    return "ai_news"

def generate(config):
    # 保守默认：不强依赖网页结构。GitHub Actions 可扩展为 requests + BS4 抓取。
    sources = config.get("sources", {})
    desc = "\n".join([
        "AI 动态抓取槽位：",
        f"OpenRouter Rankings: {sources.get('openrouter_rankings', '')}",
        f"OpenAI / ChatGPT: {sources.get('openai_news', '')}",
        f"Codex: {sources.get('codex', '')}",
        f"OpenClaw: {sources.get('openclaw_releases', '')}",
        "",
        "扩展方式：在本插件中增加 fetch_* 函数，解析结果后生成当天摘要事件。"
    ])
    return [CalendarEvent(
        title="🧠 AI 动态抓取模块已启用",
        start=date.today().isoformat(),
        all_day=True,
        description=desc,
        categories=["AI简报"],
        uid_seed="ai-news-module-enabled"
    )]
