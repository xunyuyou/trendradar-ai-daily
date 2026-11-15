# 全球 AI 热点采集（基于 TrendRadar）

本仓库由 [sansan0/TrendRadar](https://github.com/sansan0/TrendRadar) 的 "Use this template" 生成，
遵循上游 **GPL-3.0** 许可证，版权声明见 `LICENSE`。热榜数据来自开源项目
[newsnow](https://github.com/ourongxing/newsnow) 的公开 API。

## 运行方式

`.github/workflows/crawler.yml` 每天在 **北京时间 08:00 / 12:00 / 20:00** 抓取一次：

- 数据源：`config/config.yaml` 中 `platforms.sources`（当前全部可用热榜）+ `rss.feeds`（全球 AI 媒体/官方博客/论文）
- 筛选：`config/frequency_words.txt` 的中英双语 AI 关键词（纯关键词匹配，不调用任何 LLM，零费用）
- 报告：`index.html` 为最新快照；`reports/YYYY-MM-DD/HHMM.html` 为当天各时段归档；`output/txt/<日期>/` 为纯文本快照
- 推送：全部关闭，日报由 WorkBuddy 云端定时任务读取公开地址后生成

公开报告地址（供 WorkBuddy 读取）：

    https://raw.githubusercontent.com/xunyuyou/trendradar-ai-daily/master/index.html

## 维护

- 改关键词：编辑 `config/frequency_words.txt` 并推送，workflow 会在 `config/**` 变更时自动重跑一次
- 增删平台：编辑 `config/config.yaml` 的 `platforms.sources`
- 增删 RSS：编辑 `rss.feeds`；`freshness_filter.max_age_days: 1` 保证只看当天
- 改频率：编辑 `.github/workflows/crawler.yml` 的 cron（GitHub Actions 使用 UTC，北京时间减 8 小时）

## 说明

上游官方 workflow 带有 7 天试用签到机制（作者为节约 GitHub 公共资源而设计）。
本仓库的工作流是自建轻量版本，不含该检查代码，也不修改作者任何源文件；
作为对公共资源的尊重，抓取频率从官方默认的每小时降为每天 3 次。
每日报告提交会持续产生仓库活动，同时规避 GitHub「60 天无活动自动停用定时任务」的平台规则。
