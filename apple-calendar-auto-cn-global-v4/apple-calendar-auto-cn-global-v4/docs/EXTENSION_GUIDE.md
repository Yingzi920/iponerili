# 扩展指南

## 推荐扩展模块

### 1. legal_deadlines
案件期限、开庭、举证、上诉期、保全期限。

### 2. finance_bills
信用卡还款、订阅扣费、流量卡续费、服务器/VPS 到期。

### 3. travel_itinerary
火车、机票、酒店、景点预约。

### 4. notion_sync
从 Notion 数据库读取事件并写入日历。

### 5. telegram_push
重要事件同步推送到 Telegram。

### 6. openclaw_bridge
让 OpenClaw 读取日历任务，并执行每日自动简报或检查。

## 插件约定

每个插件只做一件事：

- 抓取
- 清洗
- 生成 CalendarEvent

不要直接写 calendar.ics，由 `generate_calendar.py` 统一生成。
