# Ying 智能订阅日历 v4

这是一个可托管在 GitHub 的苹果日历订阅项目，支持：

- 中国农历传统节日
- 二十四节气
- 中国大陆法定休假/补班数据槽位
- 全球通用节日
- 抖音续火花提醒
- AI 简报入口：OpenRouter、ChatGPT/OpenAI、Codex、OpenClaw
- 大陆院线电影入口：猫眼、淘票票
- 插件化扩展：以后新增模块只需要放入 `plugins/`

## 快速使用

1. 新建 GitHub 仓库。
2. 上传本项目全部文件。
3. 在仓库 Actions 页面启用 workflow。
4. 手动运行一次 `Update Smart Calendar`。
5. 订阅：

```text
https://raw.githubusercontent.com/你的用户名/你的仓库名/main/calendar.ics
```

iPhone 路径：

```text
设置 → 日历 → 账户 → 添加账户 → 其他 → 添加已订阅的日历
```

## 扩展方式

新增一个插件：

```text
plugins/legal_deadlines.py
```

实现：

```python
from .base import CalendarEvent

def plugin_name():
    return "legal_deadlines"

def generate(config):
    return [
        CalendarEvent(
            title="示例事件",
            start="2026-05-01",
            all_day=True,
            description="说明",
            categories=["扩展模块"],
            uid_seed="legal-deadlines-demo"
        )
    ]
```

然后在 `config.json` 的 `enabled_plugins` 里加入：

```json
"legal_deadlines"
```

## 设计原则

- 插件之间互不影响
- 抓取失败不破坏已有 calendar.ics
- 动态数据先缓存，再写入日历
- 苹果日历只订阅一个稳定 Raw 链接
- 以后可接 Notion、Telegram、OpenClaw、财务账单、案件期限
