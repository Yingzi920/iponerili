# 上传 GitHub 步骤

## 方式一：网页上传

1. 打开 GitHub，新建仓库，例如 `ying-smart-calendar`
2. 上传本项目所有文件
3. 进入 Actions，启用 workflow
4. 点击 `Update Smart Calendar` → `Run workflow`
5. 等待生成/更新 `calendar.ics`

订阅链接：

```text
https://raw.githubusercontent.com/你的用户名/ying-smart-calendar/main/calendar.ics
```

## 方式二：命令行上传

```bash
git init
git add .
git commit -m "init smart calendar"
git branch -M main
git remote add origin https://github.com/你的用户名/ying-smart-calendar.git
git push -u origin main
```
