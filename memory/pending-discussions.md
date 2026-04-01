# 待讨论事项

> 最后更新：2026-04-01 by Code-主控台
>
> 跨会话的待决策事项追踪。已决策的条目移入 decisions.md，已落地的条目删除。
> 所有会话启动时应阅读本文件。

## 采集管线

- [x] **统一输出 JSON schema** — ✅ 已由 Code-news 实现统一格式，数据落盘到 `projects/news/output/`
- [x] **Steam API 定时 cron** — ✅ 已实现，每小时自动采集，输出 `steam-latest.json`
- [x] **B站 API 试通** — ✅ 已实现，每小时自动采集，输出 `bilibili-latest.json`
- [x] **Discord 频道结构发现** — ✅ Issue #59 已完成，频道列表已获取
- [ ] **Discord 频道监控范围** — 由制作人标注哪些频道进日报监控、哪些做资产归档。已确认的高价值频道：影画长廊 Morimens Gallery (ID: 1304022107847659520)。
- [ ] **Twitter/X 接入** — 需 TWITTER_BEARER_TOKEN
- [ ] **NGA 接入** — 需 NGA_FORUM_ID
- [ ] **TapTap 接入** — 需 TAPTAP_APP_ID

## 存储

- [x] **大文件存储方案** — ✅ 已决策：Discord 数据分级存储（git 60天 + Releases 月归档），其他资产暂留 git（见 decisions.md）

## 日报流程

- [ ] **Chrome 手动采集规范** — 小红书、NGA、贴吧、Arca Live 无公开 API。需定义操作步骤和输出格式，让手动采集数据能进入报告管线。
- [x] **两套采集系统合并** — ✅ 已决策不建第三套系统，统一 JSON schema 后逐个接数据源

## 数据校验

- [ ] **Wiki JSON 数据抽查** — projects/wiki/data/db/ 下 18 个 JSON 的准确性，运营官负责抽查报告，制作人决定是否派 Issue 修正。尚未启动。

## 站点

- [ ] **启用 GitHub Discussions** — Giscus 评论系统（Issue #91）需要在仓库 Settings → General → Features 中启用 Discussions 功能才能生效
