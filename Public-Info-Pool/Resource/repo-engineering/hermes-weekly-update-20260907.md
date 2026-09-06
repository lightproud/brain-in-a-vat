# Black Pool 周更公告 · 上游 v2026.8.31（引擎 0.21.0）

> 银芯周更例程自动产出（每周一 00:00 北京时间 / 周日 16:00 UTC 起跑）。
> 本档三合一：**新内容公告** + **zip 下载链接** + **BPA 更新指南**。
> 上游 [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent)（MIT）——
> 黑池为其品牌换装 + 内网适配的二次开发衍生物，非纯自研。

## 一、本次更新是什么

| 项 | 值 |
|----|----|
| 上游 pin | `v2026.8.27` → **`v2026.8.31`**（commit `29112bef0992`，2026-08-31） |
| 引擎版本 | 0.20.6 → **0.21.0** |
| 黑池版本 | 0.1.0（品牌版本号不随上游走） |
| 上游提交 | 911 个 |
| 快照变更 | 537 新增 / 1080 修改 / 100 删除文件 |
| 快照规模 | 10,925 文件 / 188MB |
| 补丁核对 | 三张补丁全部干净落位（品牌两张规则引擎重出，特性补丁 `--check` 通过） |

本周对黑池用户实际可感知的变化，挑对内网日常使用最相关的几条：`/plan` 从可选技能升成
每个客户端面（CLI/TUI/Discord/Desktop）都自带的内置命令，用前不用再手动装；状态栏新增
缓存命中率 / 延迟 / 每秒 token 三项可按需开关的实时指标；群聊（Group Chat）拿到了跨网关
故障转移与重放能力，authority 网关掉线不再打断会话；桌面端预览文件卡新增下载按钮，
文件不必再手动去源目录找；board（看板）新增导出/导入，可整块搬走或备份；cron 自然语言
排期解析扩了一批新写法（如「weekdays at 9am」、无 every 的自然日期）；本次也是一次纯缺陷
修复重头戏（540 条 fix，覆盖率远超 86 条 feat），多集中在 buzz(nostr) 消息投递、Windows
桌面端会话恢复、狀態库并发写入这几处历史老毛病上，多数属于「用户不会点名感谢、但天天在
受益」的底盘加固。

## 二、变更清单

上游区间 `v2026.8.27` → `v2026.8.31`，共 **911** 个提交。

| 类别 | 条数 |
|------|------|
| 新增能力（feat） | 86 |
| 缺陷修复（fix） | 540 |
| 性能（perf） | 3 |
| 重构（refactor） | 50 |
| CI（ci） | 2 |
| 测试（test） | 91 |
| 文档（docs） | 36 |
| 样式（style） | 4 |
| 杂务（chore） | 54 |
| 回退（revert） | 1 |
| 未分类（other） | 44 |

### 新增能力（feat，86 条）

- **cron** feat(cron): doctor flags overdue next_run_at as silent non-firing  `f2f7a3bf`
- feat: add cron doctor health check  `b028fe63`
- **browser** feat(browser): honor browser.engine=lightpanda in Browser Use mode  `e3a85ae5`
- **buzz** feat(buzz): compose thread-topology cluster — reply_in_thread opt-out, NIP-10 root anchoring on all send paths, _PLATFORM_DEFAULTS tier  `972f0314`
- **buzz** feat(buzz): implement edit_message and delete_message so replies can stream  `34c10f83`
- **worktree** feat(worktree): pushed open-PR lanes reclaim their disk; cron tick prunes worktrees  `3a351a96`
- **openviking** feat(openviking): use user memory by default  `823bcc88`
- **bot-mode** feat(bot-mode): add scoped cross-gateway Group Chat transport  `e7433910`
- **bot-mode** feat(bot-mode): run same-gateway Group Chats without Desktop  `93c7089f`
- **delegation** feat(delegation): surface config-level model_not_found notice in delegation batch reports  `c05d04ff`
- **bot-mode** feat(bot-mode): Group Chats survive the authority gateway dying — log replication and fenced takeover  `e730deed`
- **bot-mode** feat(bot-mode): replay pages carry authority lineage; pin byte-bounded replay  `cc4b5ba1`
- **bot-mode** feat(bot-mode): add durable Group Chat authority and replay  `cbc67b93`
- **photon** feat(photon): read-receipt toggle, receipt-type alias, docs  `d63f996a`
- **photon** feat(photon): support iMessage read receipts  `9744fc0c`
- **compaction** feat(compaction): system prompt always rebuilds at the commit boundary — updates finally reach long-lived sessions (#98426)  `514707ff`
- **telegram** feat(telegram): inline command picker — search every command and skill, no menu cap  `5bdaea64`
- **mcp-oauth** feat(mcp-oauth): Desktop MCP OAuth now completes against remote backends (client-side callback relay)  `0f5dd5c4`
- **skills-hub** feat(skills-hub): impeccable joins the optional-skills catalog, content pulled live from upstream  `45d9c33d`
- **discord** feat(discord): expose /plan in the native slash-command picker  `83f4524b`
- feat: /plan graduates from bundled skill to built-in command on every surface  `0f3fcacd`
- **cli** feat(cli): add /plan command (#67264)  `5c6e5e7e`
- **delegation** feat(delegation): honor delegation.request_overrides on all three resolution branches with explicit-over-runtime merge precedence  `bacb90fe`
- **delegation** feat(delegation): forward delegation.request_overrides on direct-endpoint branch  `d3bfd2e9`
- **tui** feat(tui): status rule shows cache-hit %, latency, t/s and honors display.status_bar.fields  `86a2fdc6`
- **desktop** feat(desktop): real-profile browsing toggle in Capabilities → Tools → Browser  `6cb6aeb1`
- feat: allow configured background review tools  `c8bbde77`
- **cli** feat(cli): tui status bar per-field toggle + cache/latency/tps  `3548fc80`
- **cli** feat(cli): show prompt cache hit rate in status bar  `4bc7e624`
- **cli** feat(cli): add display.status_bar.fields config for customizing status bar  `fb786d2f`
- **providers** feat(providers): curated picker lists for the Alibaba CN variants  `93b6cf2e`
- **providers** feat(providers): curated model list for alibaba-token-plan picker  `46076b2d`
- **browser** feat(browser): Brave Origin works for real-profile browsing and default-browser detection  `b6d535dd`
- **loop** feat(loop): first wakeup fires immediately by default  `1a47a364`
- **loop** feat(loop): add --start-now to fire the first wakeup immediately  `796babaa`
- **relay** feat(relay): delete_message over the additive delete op — fresh-final preview cleanup  `3f36c87e`
- feat: /btw rides the background-review cache-parity fork for full-context answers  `578f85cf`
- feat:add hy4-preview model and tokenplan provider  `0fb5cab0`
- **providers** feat(providers): add Nebius Token Factory provider  `13bad590`
- **providers** feat(providers): send Hermes-Agent User-Agent on Router requests  `ceb54f5a`
- **providers** feat(providers): add Ramp Router (router.com) provider plugin  `804f8b47`
- feat: /btw now answers side questions with conversation context; /background renamed to /bg  `74a95a3d`
- **todo** feat(todo): nested subtasks via optional parent field  `b6bd681e`
- **system_prompt** feat(system_prompt): two-line conversation clock — anchored start + rebuild-day line (salvages #96224) (#97930)  `11b98a14`
- **prompt** feat(prompt): default identity rewritten as a behavior spec — sizing rule, named prohibitions, anti-sycophancy, earned depth; exploration-thrift line deliberately removed (models under-explore) (#97926)  `f89f0a2e`
- **optional-skills** feat(optional-skills): add decision-questionnaire — turn a blocked decision into an async questionnaire  `b1ff8722`
- **optional-skills** feat(optional-skills): add setup-wizard-generator — bash wizard for human-only setup steps  `7b17d02a`
- **skills** feat(skills): rename grill-me to plan-interrogation, fold in frontier-rounds interview mechanic  `bfeeb502`
- **desktop** feat(desktop): Download button on preview file cards — save any delivered file via the authenticated backend bridge (works local and remote) (#97816)  `3b362acf`
- feat: add grill-me skill — adversarial plan interview before coding  `21f86655`
- **cli** feat(cli): render Ghostty-level pets in the interactive pane  `fac3c623`
- **pet** feat(pet): gate Unicode placeholders to kitty and Ghostty  `d8897585`
- **desktop** feat(desktop): export, import, rename and delete a board from the switcher  `72cf8d1f`
- **desktop** feat(desktop): PluginOs gains native save/open file pickers  `c57f8ad4`
- **kanban** feat(kanban): board export/import REST endpoints  `5e550838`
- **kanban** feat(kanban): export and import a whole board as a portable archive  `3150e444`
- **a2a** feat(a2a): client tools config-gated — disabled unless enabled (−561 tok/call on unconfigured installs) (#97421)  `3340bbbd`
- **skill_manage** feat(skill_manage): operations[] is the call — each op names its skill; atomic with cross-skill rollback (#97295)  `72874b06`
- **agent** feat(agent): context size anchors on provider-reported usage — estimation shrinks to the last turn  `d3a1c465`
- feat: session temp root moves off tmpfs /tmp to ~/.hermes/cache/terminal by default; auto-pruned after 72h  `95cf7dc9`
- feat: expose terminal.temp_dir to redirect session temp root off tmpfs  `d7be3f64`
- **cli/tui** feat(cli/tui): -q now seeds a live interactive session; prompts submit literally  `a5c7eed5`
- **compaction** feat(compaction): rebuild dynamic tool schemas at the compaction commit boundary — forever-sessions finally pick up config changes (#97073)  `c30ac90a`
- **execute_code** feat(execute_code): stdout spillover — truncated output's full text saved to cache/exec (host) or kernel tmpdir (cells), path + read_file recipe in the result (#97043)  `ae8c9760`
- **code-execution** feat(code-execution): remote kernel host — session persistence for docker/ssh/modal backends (closes #96873) (#96991)  `5f75ec19`
- **models** feat(models): qwen3.8-flash now selectable on OpenRouter and Nous portal  `48d25280`
- **desktop** feat(desktop): make tips and guided tours both opt-out (#96835)  `1acd5bb0`
- **desktop** feat(desktop): default the in-app tip rotation on (#96831)  `4bd27933`
- **commands** feat(commands): attach desktop slash metadata to the registry  `b61408e9`
- **desktop** feat(desktop): pace the tip rotation in hours, not minutes  `198a6942`
- **desktop** feat(desktop): make the idle tip rotation opt-in, ungate the tool  `03579826`
- **tools** feat(tools): let Hermes point at one thing with the tip tool  `911c6c50`
- **desktop** feat(desktop): in-app tips  `baaf3049`
- **desktop** feat(desktop): give the app's main surfaces durable handles  `46512ee1`
- **desktop** feat(desktop): add an accent variant to the popover primitive  `50f816ab`
- **desktop** feat(desktop): give a bot's empty chat its own face and name  `e4bd1a0a`
- **desktop** feat(desktop): let a plugin title an empty chat it owns  `45176219`
- **desktop** feat(desktop): widen the plugin SDK to what Bot Mode had to reinvent  `4fcd16e2`
- **tools** feat(tools): session-persistent kernels for execute_code (kernel_mode: session) (#94647)  `b39d76d9`
- **plugins** feat(plugins): wire plugin platform handlers into a2a, buzz, and qqbot adapters  `34393c32`
- **plugins** feat(plugins): generalize native platform handler registration to every gateway platform  `272f4e4a`
- **plugins** feat(plugins): let plugins register Telegram PTB handlers via ctx.register_telegram_handler  `c96f8302`
- **wecom** feat(wecom): native reply streaming (per-turn isolation, dedup-safe delivery, interaction boundaries)  `2ecb5445`
- **gateway** feat(gateway): per-platform streaming config default for WeCom  `81aa4f18`
- **skills** feat(skills): publish-site — versioned website publishing to GitHub/Cloudflare/Netlify Pages  `5c57e775`
- **skills** feat(skills): rewrite AgentMail optional skill CLI-first  `14320d18`

### 缺陷修复（fix，540 条）

- **telegram** fix(telegram): bound stale-client cleanup and add Windows CLOSE-WAIT live probes (#87057)  `7790c8f4`
- **telegram** fix(telegram): prevent Windows long-poll socket reuse deadlock  `b02b7122`
- **telegram** fix(telegram): recover Windows CLOSE-WAIT getUpdates deadlock  `a06c0d0a`
- **agent_init** fix(agent_init): reserve Gemini's default maxOutputTokens in the compressor when max_tokens is unset  `7cefa87e`
- **agent_init** fix(agent_init): clamp compressor window to Ollama num_ctx resolved after construction  `cb71d5f1`
- **update** fix(update): locate PortableGit under the shared root, not profile home  `6cccc2ef`
- **update** fix(update): self-heal broken Git-for-Windows trampoline on Windows  `0bab9ff9`
- **gateway** fix(gateway): keep long turns controllable without blocking Telegram  `0943702c`
- **model_metadata** fix(model_metadata): parse Google's 'supports up to N' context-limit phrasing  `58f5b1e2`
- **agent** fix(agent): cap compaction threshold floor at 85% of the context window  `4252aecc`
- **config** fix(config): greedy literal-key matching + loud phantom-sibling refusal for dotted key names  `a42aee95`
- **cli** fix(cli): support literal dots in config set/unset key paths (#84064)  `89519475`
- **gateway** fix(gateway): gate compute-host interrupt forward on hosted activity  `4396253a`
- **gateway** fix(gateway): relay compute-host clarify state  `3ae74119`
- **desktop** fix(desktop): heal v1 SSH gateway routes into the v2 connections registry  `2e9a39d2`
- **desktop** fix(desktop): bounded auto-restart for no-mux SSH tunnel flaps instead of instant connection death (#96266)  `6e41ab34`
- **state** fix(state): defer corrupt FTS rebuilds past live operations  `18ac3c4f`
- **estop** fix(estop): honor canonical ~/.hermes/ESTOP from profile gateways  `ad08a581`
- **cli** fix(cli): supervised gateway launches skip the sticky active_profile redirect  `b0acc558`
- **gateway** fix(gateway): isolate PID check and credentials per profile (#74872)  `e0abbc4d`
- **gateway** fix(gateway): run MCP shutdown off-loop with a bounded wait on the shutdown path  `11ba76c0`
- **desktop** fix(desktop): prevent venv scan timeout on busy Windows hosts  `4d3e1e4d`
- **desktop** fix(desktop): keep primary SSH session resumes remote  `61534aac`
- **cli** fix(cli): print partial-update hint when chat startup hits a first-party ImportError (#96900)  `fa3471d4`
- **desktop** fix(desktop): resolve the e2e Electron binary per platform and layout  `7a1fca66`
- **redact** fix(redact): keep dotted config-key scans linear past the keyword pre-gate  `fe0cfdf9`
- **desktop** fix(desktop): satisfy import ordering  `c631b483`
- **desktop** fix(desktop): retain session remount polling reset  `1940c23a`
- **desktop** fix(desktop): latch dead runtime recovery across remounts  `48deb73e`
- **compression** fix(compression): dead Codex summary streams fail over in 60s instead of stacking 5-minute waits  `f50b5bb0`
- **desktop** fix(desktop): recover incomplete transcript turns  `f1e01f4d`
- **gateway** fix(gateway): bound signal interrupt grace  `22131283`
- **gateway** fix(gateway): require FTS provenance before transcript rebuild-and-retry  `f680a4dc`
- **state** fix(state): fail closed on unscoped corruption  `96739033`
- **docker** fix(docker): keep forwarded secret values out of world-readable argv  `d10ef89e`
- **state** fix(state): cap read connections per PROCESS and yield when the fd table is tight  `0e9b57d3`
- **state** fix(state): bound state.db read connections per FILE, and stop opening two gateway handles  `e8c41568`
- **models** fix(models): support OpenRouter preset references  `3e912874`
- **profiles** fix(profiles): make_targz writes to a temp file and renames, not the destination directly  `4d4cffd1`
- **compression** fix(compression): count streamed reasoning details as progress  `99d037ee`
- **context** fix(context): fail closed when preflight compression stalls  `de49e1ef`
- **redact** fix(redact): keep lowercase assignment scans linear  `ba0f5839`
- **cli** fix(cli): honour model_aliases api_key, stop cross-provider key leak (#83612)  `3145986c`
- **feishu** fix(feishu): gate approval/update-prompt card clicks on operator allowlist, not group policy  `a89706e4`
- **install** fix(install): never adopt a pre-release Node.js build  `39540a03`
- **state** fix(state): self-heal SessionDB writes after close() races an in-flight worker  `9db48053`
- fix: restore _inactivity_watchdog_loop dropped in rebase conflict resolution  `c74cf233`
- fix: clamp invalid effective_timeout to the 120s wait default instead of unbounded (review follow-up for #94305)  `53e3c14f`
- **terminal** fix(terminal): bound env.execute wait so a wedged poll cannot disable every timer  `85bc25c9`
- **update** fix(update): fingerprint orphan backends from the classification psutil handle  `ce942ab1`
- **windows** fix(windows): compose the taskkill identity guards into one fail-closed class fix  `90e916ef`
- **update** fix(update): refuse gateway ancestor tree-kill on Windows  `c923b539`
- **windows** fix(windows): require process identity before taskkill  `ed6d5fc8`
- **hermes_cli** fix(hermes_cli): fail-closed PID-ownership guard before Windows taskkill  `cdd06352`
- **compression** fix(compression): truncated summaries no longer become compaction checkpoints (port of earendil-works/pi#7048)  `d8f8a07e`
- **desktop** fix(desktop): keep @tanstack/react-query in one runtime chunk (#95560)  `38b93e0a`
- **prompt** fix(prompt): preserve resumed workspace provenance  `da090aa4`
- **prompt** fix(prompt): skip bundled AGENTS.md for desktop launch cwd  `c6ee4e08`
- **cli** fix(cli): answer clarify headless in single-query turns  `db2fd5f5`
- **discord** fix(discord): gate relay-only thread rename kwargs  `808a22ea`
- **xai** fix(xai): request-local alias provenance + collision-safe wire aliasing  `b7ebe645`
- **xai** fix(xai): alias the reserved tool_search bridge name on chat completions  `5e2f8b98`
- **xai** fix(xai): alias the reserved tool_search bridge on the wire (#95003)  `de123be5`
- **cli** fix(cli): stop raw CSI bytes from Shift+Space leaking into buffer (#88071)  `839de43d`
- **config** fix(config): warn for empty platform toolsets  `081030a7`
- **config** fix(config): warn when a platform_toolsets entry is an empty list  `ccd32a9f`
- **curator** fix(curator): remove terminal from the consolidation fork (issue #96962)  `37ae0e1d`
- **curator** fix(curator): restore complete skill packages on ledger rollback (#96962)  `98e2f110`
- **desktop** fix(desktop): pin --publish never in run-electron-builder.mjs (salvaged from #87937)  `3738b880`
- **cli** fix(cli): launch-context-independent Linux desktop-entry Exec (salvaged from #94874)  `6fe933e7`
- **dashboard** fix(dashboard): don't gate Desktop-owned loopback backends on public_url  `54ee290b`
- fix: align config-settings test mock with the settings-scope store on main  `c7f04c99`
- **desktop** fix(desktop): advance the autosave baseline after each accepted save  `ca3961c9`
- **desktop** fix(desktop): stop model_context_length edits from being dropped or wiped  `6d407ca1`
- **desktop** fix(desktop): stop Settings autosave from clobbering out-of-band config edits  `5361867c`
- **buzz** fix(buzz): reconcile media pipeline with landed dispatch + threading contracts  `c816957a`
- **buzz** fix(buzz): route shared attachment sender through redacted receipt errors  `c731500c`
- **buzz** fix(buzz): redact media paths before bounding errors  `a55d66b7`
- **buzz** fix(buzz): complete media-only delivery reporting  `fcd34e57`
- **buzz** fix(buzz): verify live media delivery receipts  `9c257042`
- **buzz** fix(buzz): support media in standalone sends  `37c94399`
- **buzz** fix(buzz): reconcile probe-race contract with shared file-attachment sender  `4c496d3c`
- fix: deliver Buzz media as native attachments  `fafc3ddc`
- **buzz** fix(buzz): deliver local images through native upload  `ebda1fbf`
- **buzz** fix(buzz): merge URL-localization and imeta attachment paths in dispatch  `73071d85`
- **gateway** fix(gateway): require boolean authorization decisions  `36650620`
- **buzz** fix(buzz): gate inbound attachment side effects  `d15cbbcb`
- **buzz** fix(buzz): ingest verified native attachments  `00394acf`
- **buzz** fix(buzz): gate authenticated inbound media on explicit authorization  `aaad0543`
- **buzz** fix(buzz): preserve inbound media captions  `55136adc`
- **buzz** fix(buzz): localize inbound relay media  `bce94cc1`
- **desktop** fix(desktop): confirm before deleting a session in the Command Center  `b811350c`
- **scripts** fix(scripts): align retry recovery documentation  `12116f76`
- **scripts** fix(scripts): preserve update retry fallback  `fd596e24`
- **scripts** fix(scripts): clarify Windows update retry marker semantics  `f10a231e`
- **update** fix(update): resume deferred Windows desktop updates  `fd24ac94`
- **update** fix(update): verify failed restore cleanup  `915ec169`
- **update** fix(update): fail closed on incomplete restore checks  `53cf38c3`
- **update** fix(update): preserve unknown restore cleanup state  `3e4dc5f2`
- **update** fix(update): authenticate import health markers  `8236b518`
- **update** fix(update): reject terminated import probes  `6c608e2f`
- **update** fix(update): capture terminating restored imports  `68f9681a`
- **update** fix(update): compare every restored module failure  `f6c39429`
- **update** fix(update): detect restored import-time failures  `7b958b35`
- **update** fix(update): reject unsafe stash restores  `716b1031`
- **update** fix(update): refuse to mutate a venv containing foreign-owned files (#83529)  `e49df406`
- **packaging** fix(packaging): include wheel in PEP 517 build-system requires  `a300a7fa`
- **compression** fix(compression): pop the tail tags before the anti-growth estimate; count against the final list  `0c24b3a1`
- **state** fix(state): bound the rewind-tail walk at the watermark and rewind concurrent-tail originals too  `f57802c7`
- **state** fix(state): archive carried-forward compaction tail as rewind rows (#86366)  `9d9d9194`
- **install** fix(install): stop a CLI install from building the desktop's node-pty  `cffc8bb2`
- **install** fix(install): clean up a broken managed Node and guard the termux probe  `cb89872c`
- **install** fix(install): report a managed Node that cannot start, and preinstall libatomic1  `8f8351af`
- **install** fix(install): defer the partial clone's checkout so the throttle fallback engages  `0aa6b449`
- **install** fix(install): retry the HTTPS clone and degrade past repo-scoped 429s  `11afd07f`
- **cron** fix(cron): bound local fire-fence waits  `d957e0e4`
- **cron** fix(cron): isolate per-execution working directories  `b7c59bda`
- **cron** fix(cron): stale ticker yields its tick to a fresh gateway  `9a7732b4`
- **cron** fix(cron): isolate lazy imports from stale modules  `fd1d8271`
- **timezone** fix(timezone): make profile-keyed tz cache atomic and add cron persistence regression  `6cc4f391`
- **timezone** fix(timezone): isolate cache by active profile  `9d8a053c`
- **gateway** fix(gateway): recover agent after session reaped so messages are not silently dropped  `99ec7fdf`
- **gateway** fix(gateway): hold inbound gate until turn machinery is warm on fresh boot (#99373)  `fc2421cf`
- **compression** fix(compression): rotation heals stale automatic ended_at stamps instead of wedging (#88197)  `c0667439`
- **memory** fix(memory): tolerate bare-signature v2 providers when forwarding checkpoint requirement  `8b73720f`
- **memory** fix(memory): forward checkpoint requirement to v2 providers  `5db9058c`
- **gateway** fix(gateway): stop hygiene retry livelock after commit-fence cancel (#96953)  `1b089430`
- **tui** fix(tui): show status while idle/auto compaction runs  `3a542bbe`
- **state-db** fix(state-db): report corruption instead of "session not found", detect it early  `ba7743b0`
- **tui** fix(tui): fail prompt.submit loud only on a real store-open failure  `037a73fa`
- **state** fix(state): reject special files in zeroed probe; real schema-bytes decode fixture  `cdd3b84c`
- **state** fix(state): decode errors now reach the heal path and fail loud in TUI (residual #98924 surfaces)  `e17fd0a7`
- **state** fix(state): honor _ensure_fts_cjk_schema's never-raises contract  `47b0e656`
- **state** fix(state): _fts_table_probe catches UnicodeDecodeError (#98924)  `50c3cb72`
- **state** fix(state): serialize startup across zero-byte check, quarantine, connect, and schema commit (#97568)  `69245e65`
- **state** fix(state): contain post-commit FTS maintenance errors + lock-audit the writer conn (salvage #90734)  `22dcbdec`
- **state** fix(state): isolate background reads from writer connection  `94869e5a`
- **buzz** fix(buzz): open fresh WS subscriptions from the beginning and discover conversations on a timer (#78429, #93557, #75107)  `c84c6e23`
- **buzz** fix(buzz): compose #97502's membership-rejection matching into the per-subscription CLOSED handler  `b907b7eb`
- **buzz** fix(buzz): handle restricted CLOSED per-subscription, stop reconnect flood  `d3730a3f`
- **buzz** fix(buzz): resume watched channels from a durable cursor across restarts (#90464)  `d36827b0`
- **buzz** fix(buzz): bound WebSocket read idle time to force reconnect on silent relays  `94d86fa4`
- **browser** fix(browser): lightpanda review follow-ups for #99312  `936b970e`
- **buzz** fix(buzz): resolve @mentions to member pubkeys so agent-to-agent pings work  `a7408043`
- **buzz** fix(buzz): preserve literal mentions and exact UUID targets  `1885a40a`
- **buzz** fix(buzz): acknowledge trusted agent tags without dispatch  `c10c77d5`
- **buzz** fix(buzz): trust explicit DM metadata fallback  `f40edee4`
- **buzz** fix(buzz): require explicit group addressing  `722209bb`
- **buzz** fix(buzz): treat NIP-10 replies to own messages as mentions  `ef2be550`
- **buzz** fix(buzz): dispatch forum-channel kinds instead of chat kind 9 only  `306dc874`
- **browser** fix(browser): log when Chromium-only env flags are stripped for Lightpanda  `a9eb06a6`
- **browser** fix(browser): isolate Lightpanda and Chrome fallback flags  `e3553948`
- **plugins** fix(plugins): doctor temp home can no longer be stranded by a failed staging copy  `ca9952cb`
- **cli** fix(cli): stop plugins doctor from copying a non-plugin directory  `a00ae1d5`
- **gateway** fix(gateway): build reaper exclusion from raw registration records  `9488950a`
- **desktop** fix(desktop): keep the orphan sweep unconditional; guard the probe fix with a mutation-checked test  `c26762d6`
- **desktop** fix(desktop): don't reap the healthy standalone gateway on Windows desktop startup  `1ec4b569`
- **state** fix(state): quarantine 0-byte truncated state.db and record store provenance (#97568)  `a071fc80`
- **terminal** fix(terminal): gate the BUZZ_* terminal carve-out on actual Buzz agent context  `26f178e5`
- **terminal** fix(terminal): let Buzz-managed agents inherit BUZZ CLI credentials in terminal env  `a6192c7a`
- **tools** fix(tools): pass BUZZ_* platform credentials to terminal children  `a4c68212`
- **buzz** fix(buzz): reply in-thread instead of flat channel posts  `66fa6e41`
- **buzz** fix(buzz): reply into the existing thread instead of nesting a new one  `cbeb925f`
- **buzz** fix(buzz): preserve stable thread roots  `09cbce43`
- **buzz** fix(buzz): keep progress messages in thread  `b3af0b68`
- **cron** fix(cron): treat a live multiplexer as gateway-alive for satellite profiles  `e7037175`
- **buzz** fix(buzz): reconcile scoped auth-tag resolution across salvaged fixes  `9113cf24`
- **buzz** fix(buzz): fail closed on multiplex credential discovery  `29ee8230`
- **buzz** fix(buzz): scope owner credentials per profile  `8c09c395`
- **buzz** fix(buzz): load owner auth tag from credentials  `51ffeb05`
- **buzz** fix(buzz): drop unreachable line orphaned by the scoped-secrets refactor  `56fb2b3b`
- **buzz** fix(buzz): let the requirement gate see externally managed secrets  `a684d154`
- **buzz** fix(buzz): normalize npub entries in BUZZ_ALLOWED_USERS to hex  `c83121cf`
- **buzz** fix(buzz): resolve BUZZ_AUTH_TAG through the profile secret scope  `a5e73557`
- **tests** fix(tests): resolve Buzz Platform member by value, not attribute access  `91d4c791`
- **buzz** fix(buzz): secondary multiplex profiles must not inherit the default profile's env  `aaa5f27d`
- **cron** fix(cron): isolate desktop profile persistence  `8edaa257`
- **delegation** fix(delegation): subagent process notifications stay suppressed when the container key collapses  `5a4dbdec`
- **desktop** fix(desktop): a bot roster click no longer opens a stale finished session (#90102)  `714930f2`
- **gateway** fix(gateway): username-based DISCORD_ALLOWED_USERS no longer locks out the operator after one turn  `a0a63a1b`
- **cron** fix(cron): keep SessionDB kwargs-free in the context-preserving worker  `43ca78aa`
- **cli** fix(cli): update _get_service_pids docs for profile-scoped systemd filtering  `9f8557a0`
- **cron** fix(cron): profile isolation — systemd filter + heartbeat guard  `82d7a130`
- **cron** fix(cron): profile_routes rescue for satellite-profile delivery preflight  `d5d06137`
- **cron** fix(cron): preserve profile context during session DB init  `dfa5004a`
- **cron** fix(cron): resolve multiplex home-channel chat id from the owning profile's secret scope  `edd6ad53`
- **cron** fix(cron): reserve shared adapters for the default profile only  `a07370ab`
- **cron** fix(cron): deliver each profile's cron via its own adapter in multiplex  `51e377d5`
- **cron** fix(cron): retain profile secret scope through delivery  `07f6518b`
- **desktop** fix(desktop): fail-open attached shared-remote probe; honest ensure/open (#96493)  `89c28ccf`
- **desktop** fix(desktop): reuse primary WS for named profiles on attached shared remote (#96493)  `3efb514b`
- **state** fix(state): SessionDB derives its own store's profile for unstamped session rows  `5cc3da68`
- **sessions** fix(sessions): stamp launch-profile name on new session rows instead of NULL  `6874b99d`
- **desktop** fix(desktop): scope every session mutation to its owning profile  `18f429a8`
- **openviking** fix(openviking): synchronize setup connection state  `64b96bb5`
- **desktop** fix(desktop): model assignment carries the credential pointer, not a resolved key (#88990, salvage #90484)  `8fd144c5`
- **tui_gateway** fix(tui_gateway): scope config.get/set RPC to params.profile  `fa2dd280`
- **web** fix(web): stop mirroring env-backed provider keys into model.api_key (#88990)  `a90be562`
- **dashboard** fix(dashboard): remove deleted custom env keys  `c8a7c6c3`
- **cli** fix(cli): recognize whitespace around '=' in .env save/remove  `1152d4d3`
- **credentials** fix(credentials): scrub the keyed `providers` schema on rotate/remove  `22f9caf8`
- **credential-pool** fix(credential-pool): materialize pool entry on Desktop PUT /api/env save (#96058)  `82733a3f`
- **desktop** fix(desktop): keep profile scope when reusing primary remote backend  `2f261f99`
- **compression** fix(compression): guard the split-failure cooldown call like sibling strikes  `dc71fb37`
- **compression** fix(compression): refresh lease in-transaction before publish; arm cooldown on split failure  `087cc49a`
- **delegation** fix(delegation): report schema-invalid child results as failed, not completed  `5ce8f715`
- **relay** fix(relay): resolve fresh-final unfurl decision per chat, not per primary identity (#99206)  `1f99a4b2`
- **telegram** fix(telegram): bound polling drain with wall-clock deadline  `82881294`
- **dashboard-auth** fix(dashboard-auth): url-encode the PKCE cookie value so strict proxy hops stop dropping it (#99176)  `a65a517d`
- **desktop** fix(desktop): surface persistent group holds  `a9c783f2`
- **bot-mode** fix(bot-mode): avoid inherited stdin on Windows  `f9908e2e`
- **tools** fix(tools): surface config-level model_not_found notices in delegation batch reports  `8557e0a4`
- **delegation** fix(delegation): report failed children as failed, not completed  `1b6ea1a2`
- **bot-mode** fix(bot-mode): cancel re-routes on worker races instead of failing disband  `5a3edc74`
- **delegation** fix(delegation): pin failure-status edge cases and document exit_reason enum  `b4d51743`
- **delegation** fix(delegation): report provider-failed subagents as failed, not completed/max_iterations  `ec02d517`
- **compression** fix(compression): keep estimate seam positional-compatible for monkeypatched estimators  `64cc87e6`
- **compression** fix(compression): route-aware stale-thinking charge parity between compaction trigger and tail walks (#84371)  `452f6b7d`
- fix: failed subagents now surface a clean error to the user (CLI + gateway)  `5a134383`
- **gateway** fix(gateway): compact the live codex thread instead of no-op mirror rewrites (#73503)  `ff3835a6`
- **compression** fix(compression): scope worker-teardown grace to the total-ceiling path  `ad925a08`
- **compression** fix(compression): transiently-blocked no-op is a soft defer, never exhaustion (#97488)  `19a59e9c`
- **compression** fix(compression): stamp durable backoff rows with strategy and failure kind (#96775 #97488)  `a6549922`
- **compression** fix(compression): tear down cancelled workers with bounded grace and discard superseded attempts (#97488)  `892f756b`
- **compression** fix(compression): persist stall-interrupted backoff on pre-commit cancel (#96775)  `027b339e`
- **compression** fix(compression): report total ceiling expiry accurately  `de4155b1`
- **compression** fix(compression): preserve fallback before worker start  `0bcad451`
- **compression** fix(compression): release idle-timeout lease promptly  `c0787c8e`
- **compression** fix(compression): stop work at the total deadline  `8d567ccd`
- **compression** fix(compression): stamp _DB_PERSISTED_MARKER after in-place batch compaction commit (#98450)  `1f2bd9e7`
- **compression** fix(compression): lean compaction makes exactly one auxiliary request per attempt  `4f225435`
- **skills** fix(skills): skill_view directory file_path + skill_manage categorized name resolution  `70370e08`
- **approval** fix(approval): widen webhook exclusion to all unattended platforms, deny by default  `ef71f2ca`
- **approval** fix(approval): exclude webhook sessions from gateway approval context  `73f8fb74`
- **gateway** fix(gateway): bust agent cache on remaining compaction-routing config keys  `66666f6e`
- **compression** fix(compression): hot-apply native compaction settings  `77f5de62`
- **delegate** fix(delegate): inherit endpoint-scoped capability map only on the parent's exact route  `8a8aa850`
- **gateway** fix(gateway): preserve capabilities on model switches  `f245765a`
- **gateway** fix(gateway): propagate trusted proxy capabilities  `80044bf3`
- **gateway** fix(gateway): preserve native compaction capability on resume  `c9b9b5e6`
- **compaction** fix(compaction): preserve switch compatibility fixtures  `48a4201f`
- **compaction** fix(compaction): clarify runtime capability state  `5247a6f0`
- **compaction** fix(compaction): resolve capability from effective switch URL  `903c36b6`
- **compaction** fix(compaction): preserve native capability across runtime switches  `08c7879c`
- **codex** fix(codex): nudge the second continuation of a compaction-only turn  `80764b6d`
- **native-compaction** fix(native-compaction): retain image-only user content  `532b2d88`
- **compression** fix(compression): keep tool-schema tokens in the unanchored fallback estimate  `be927037`
- **compression** fix(compression): route-aware pruned estimate at remaining pressure sibling sites  `c49e2a49`
- **compression** fix(compression): use the route-aware pruned estimate in the mid-turn pre-API guard  `222fda3d`
- **compression** fix(compression): derive native threshold from local trigger  `a2af8405`
- fix: skill supporting-file listings no longer repeat the absolute path per line  `2a598aad`
- **todo** fix(todo): unversioned tool.start still merges after resume  `58523f28`
- **browser** fix(browser): real-profile browsing runs headless — no focus-stealing window  `d5fd2e93`
- **security** fix(security): widen the exfil substring-suffix fix to the skills-guard sibling patterns  `21e52c1f`
- **tools** fix(tools): reduce false positives in exfil_curl/exfil_wget patterns  `6b290b81`
- **skills-hub** fix(skills-hub): reconcile salvaged install fixes with full-directory fetch  `d041ed7a`
- **skills** fix(skills): review follow-up — revision pinning, canonicalization, case-fold guards  `7e95b67a`
- **skills** fix(skills): fetch explicitly linked same-directory siblings on install (#96310)  `86dda3cd`
- **cli** fix(cli): skip unreachable support files instead of aborting URL skill install  `7d87bab5`
- **compression** fix(compression): retire completed todo snapshots safely  `989e48cc`
- **compression** fix(compression): strip embedded stale todo snapshot from list message content  `1762d378`
- **cron** fix(cron): coerce string repeat values on the UPDATE path too  `52e5e7c0`
- **browser** fix(browser): real-profile snapshot auth files are owner-only (#96729)  `0f7981b8`
- **cron** fix(cron): teach the parse error the corrected bare-duration contract  `609a0b47`
- **cron** fix(cron): bare durations are recurring intervals; coerce repeat string forms  `e8bab87b`
- **desktop** fix(desktop): satisfy perfectionist/sort-imports for mcp-oauth-callback-ipc import  `3528a3bf`
- **skills** fix(skills): impeccable catalog stub meets authoring standards  `4345cd5b`
- **cron** fix(cron): repair mangled schedule field in cronjob tool schema  `0582ae76`
- **cron** fix(cron): accept weekday lists and no-'every' natural schedules (#51975)  `57ad23c5`
- **cron** fix(cron): accept named months/weekdays in cron schedules  `77fd6db4`
- **cron** fix(cron): accept no-'every' natural day/time schedules like 'weekdays at 9am'  `ecdc03c6`
- **cron** fix(cron): accept documented "every <weekday> <time>" schedules  `ab9d8528`
- **telegram** fix(telegram): rank complete menu candidate set  `21b503fb`
- **telegram** fix(telegram): prioritize dynamic skill menu commands  `60a66451`
- **runtime** fix(runtime): key-scoped fallback extra_body re-resolution + request_overrides in switch_model snapshot  `3b3ad958`
- **runtime** fix(runtime): restore request_overrides after transport recovery  `13150122`
- **fallback** fix(fallback): re-resolve extra_body when activating fallback provider (#75091)  `91d60d2f`
- **agent** fix(agent): match switched-to custom provider by model+base_url, not name  `b10b27e6`
- **gateway** fix(gateway): carry request_overrides through /model session overrides  `5d238be2`
- **gateway** fix(gateway): preserve custom-provider request_overrides on agent turns  `fc00e36c`
- **gateway** fix(gateway): merge instead of overwrite agent.request_overrides on reused turns  `2f469d7e`
- **agent** fix(agent): carry request_overrides through in-place /model switch (TUI/CLI)  `d2af9900`
- **model** fix(model): initialize switch request overrides  `a9b696c6`
- fix: preserve named custom provider request_overrides in gateway and /model switches  `863aac90`
- **cron** fix(cron): forward request_overrides into scheduled-job agents  `792dbea7`
- **providers** fix(providers): mirror new Qwen Cloud models onto alibaba-cn  `2215fb0e`
- **providers** fix(providers): add missing Qwen Cloud (alibaba) models — qwen3.8-max, qwen3.6-flash, glm-5.2, deepseek-v4-pro/flash-0731  `04ef14e3`
- **tui** fix(tui): derive resume todo snapshots from already-loaded history  `c0875ba5`
- **todo** fix(todo): live task state via revisioned snapshots and a dedicated todo.updated event  `393af4a3`
- **desktop** fix(desktop): merge todo patches instead of replacing the Tasks list  `cf692532`
- **computer-use** fix(computer-use): stop launching retired browser-grant runtimes  `b2e24b98`
- fix: simplify bad-pin error message (windows-footgun scan tripped on open() inside the string)  `5368598b`
- **browser** fix(browser): real-profile follow-ups — reap launched Chrome, headless display-less Linux, register real_profile_pin default + docs  `f8546c2e`
- **browser** fix(browser): carry source profile identity into the copy Local State  `a50b41f8`
- **browser** fix(browser): real-profile browsing on macOS - launch real binary, kill sqlite hang, normalize profile copy  `8e746668`
- fix: unify status-bar field keys, docs, and tests for salvaged cluster  `9e017428`
- **auth** fix(auth): carry the spent-rotation verdict across processes via a durable sidecar registry  `b4403a94`
- **tests** fix(tests): carry hermetic guards across the anthropic adapter module split  `b095c3d9`
- **auth** fix(auth): keep the borrowed claude_code row out of token authority and carry the spent-rotation verdict through resolution  `b7a9db8b`
- **auth** fix(auth): make the Anthropic refresh commit part of the transaction  `07faed33`
- **auth** fix(auth): close Anthropic OAuth review gaps  `0099f250`
- **auth** fix(auth): harden claude_code refresh lock and remove dashboard Anthropic OAuth  `e1a21065`
- **auth** fix(auth): close Anthropic OAuth CSRF gap, cross-process refresh race, and API-key shadowing  `739dc6d1`
- fix: background review can now read skills before patching — denial storm ended, cache parity intact (#61521, #39996)  `1ee30352`
- **cron** fix(cron): mention bare units in the duration parse error  `260f007c`
- **cron** fix(cron): accept bare duration units like 'hour' in schedule parsing  `1d13fe70`
- **desktop** fix(desktop): make the relay delivery deadline outlive the backend ceiling  `544ad1aa`
- **desktop** fix(desktop): let bot_relay.deliver outlive the generic 30s request deadline  `10f1c307`
- **delegation** fix(delegation): carry provider request_overrides through the base_url path (#65035)  `5cace317`
- fix: detect Brave Origin browsers for CDP connect  `bca0a865`
- **install** fix(install): keep install.ps1 pure ASCII — seed the SOUL text with '--' dashes  `0b10acc5`
- **prompt** fix(prompt): sync DEFAULT_SOUL_MD with the #95681 identity rewrite  `0610291b`
- **telegram** fix(telegram): recover exhausted request pool  `5cd9c456`
- **cli** fix(cli): slow /handoff transfers no longer misreported as "gateway not running"  `e05c91ac`
- **memory** fix(memory): keep Mem0 OSS OpenAI requests direct  `e38cca50`
- **providers** fix(providers): surface Alibaba China in desktop parity  `94aad6dc`
- **providers** fix(providers): fold Token Plan into the alibaba plugin, add runtime-path regressions, document all variants  `695d86f5`
- **providers** fix(providers): register Alibaba China + Token Plan provider profiles (#73265)  `7cf7df02`
- **tools** fix(tools): restore setup_mcp's never-hand-edit instruction  `d6a6d87c`
- **tui** fix(tui): render nested todo subtasks via the parent field  `81424944`
- **models** fix(models): accept live Nous Portal recommendations in /model validation  `0ffad55e`
- **compression** fix(compression): arm the failure cooldown when codex compaction fails  `835a913f`
- **custom** fix(custom): tolerate malformed ports in the Ollama URL heuristic  `c8705898`
- **custom** fix(custom): omit Ollama-only think=false on strict OpenAI-compat endpoints  `31f0336d`
- **relay** fix(relay): route force-on-unfurl streamed finals through fresh chat.postMessage  `cef4c88f`
- fix: drop duplicate hy4-preview context entry — main's 1_048_576 wins  `ac5c8f58`
- fix:update test info  `e74e594a`
- **nebius** fix(nebius): route effort through canonical clamp_effort — hand-rolled map inverted the ladder  `b954547e`
- **nebius** fix(nebius): request verbose model metadata  `49f5b6a9`
- **router** fix(router): pytest guard on caps warmer + debug log in fail-open efforts lookup  `1c5ee581`
- fix: re-derive the live busy text mode after a non-profile /busy change  `0d02f0d1`
- **gateway** fix(gateway): apply busy mode per profile  `8d1d193f`
- fix: route /insights through /hermes on Slack  `ce22b689`
- fix: use event.get_command_args() and add persistence tests  `5b8074da`
- fix: make /busy command available on gateway platforms  `c64feb23`
- **update** fix(update): ignore unrelated transitional SCM services  `d5632392`
- fix: name the preserved snapshot path in the ROLLBACK FAILED payload  `154fd10a`
- **skills** fix(skills): a failed rollback restore keeps the skill and the snapshots  `1315e65a`
- **prompt** fix(prompt): skills-section cleanup — drop '(mandatory)' header, delete hermes-agent paragraph duplicating the help guidance, gate the skill pointer on the skill actually being installed, cut the 'when the two differ' dead clause (#97918)  `5241df3d`
- **skills** fix(skills): restore grill-me name, keep frontier-rounds upgrade  `2c232761`
- **desktop** fix(desktop): reserve space for pane tab close button (#96880)  `447217b4`
- fix: follow-up for salvaged PR #95943  `e2037a6c`
- **opencode** fix(opencode): revalidate keyless opencode-free catalog live against the Zen relay  `d9d6112a`
- **desktop** fix(desktop): ::preview inline frame works on remote/URL connections — read via the mode-aware fs bridge instead of bailing to a card (vestigial gate predated /api/fs) (#97829)  `57746cbb`
- fix: shorten description to 47 chars, reformat to modern outline, add author  `a0590001`
- **desktop** fix(desktop): MEDIA: non-media files get the preview file card, not a degraded 'Open' anchor (#97812)  `fae063fc`
- **gateway** fix(gateway): document turn-hold commit overshoot + route deferred-notice through i18n (#92318 review)  `aff5125f`
- **gateway** fix(gateway): register hygiene_max_turn_hold_seconds + flat retry-after on turn-hold abandonment  `2abf72ad`
- **gateway** fix(gateway): split turn-hold expiry from idle-timeout failure path  `31b974df`
- **gateway** fix(gateway): bound the hygiene-compression turn-hold so a streaming summary cannot freeze the turn  `543c85ac`
- **agent** fix(agent): normalize list-shaped streaming content deltas  `23bae43c`
- **cache** fix(cache): preserve the configured 1h TTL on the OpenCode Go route  `d51d66e8`
- **vertex** fix(vertex): content-digest cache key — stat signature is not credential identity  `913b9104`
- **vertex** fix(vertex): restore ADC->SA retry killed by tuple cache keys (review finding)  `ef4cd77f`
- **vertex** fix(vertex): pick up rotated service-account files — signature-keyed creds cache  `56a26233`
- **prompt-caching** fix(prompt-caching): tool-using sessions no longer 400 behind LiteLLM Anthropic proxies (#89886)  `1d8946b4`
- **skills** fix(skills): drop redundant identical-strings guard and its vacuous tests  `10e93c6a`
- **skills** fix(skills): make skill_manage patch failures recoverable instead of a dead end  `4f4e778d`
- **desktop** fix(desktop): preserve streamed assistant text and unify atomic persistence (#95514)  `24e54b55`
- **desktop** fix(desktop): make gateway file saves failure-atomic so a failed download never destroys an existing file  `a7e7de64`
- **bedrock** fix(bedrock): recover from server-side cachePoint rejections per placement  `88a78ecc`
- **cache** fix(cache): over-length caller prompt_cache_key no longer 400s Chat Completions requests  `3951ead8`
- **caching** fix(caching): prevent whitespace-only text blocks in prompt cache prefix splits  `f0d5f129`
- **desktop** fix(desktop): open HUD links in the system browser  `178c23fb`
- **desktop** fix(desktop): let HUD prompts take clicks on solid X11  `240790af`
- **agent** fix(agent): count only substantive auxiliary progress  `7ff70f17`
- **teams** fix(teams): allowlist-gate BF attachment auth, stream downloads under media cap, lock token refresh  `2f01ec9f`
- **teams** fix(teams): dot-anchor Bot Framework host check, log dropped BF images, tests  `c23d40af`
- **teams** fix(teams): authenticate Bot Framework connector attachment downloads  `0eff6bc2`
- **state** fix(state): close gate blind spots — alias + variable-SQL readers (simplify findings)  `112baae6`
- **cli** fix(cli): keep pet kitty flush off the import-time prompt_toolkit path  `9f90cd43`
- **desktop** fix(desktop): board switcher crashed on every render  `d9d1ee83`
- **tools** fix(tools): narrow MCP OAuth lock scope  `9a1eef7a`
- **skill_manage** fix(skill_manage): batch failure results carry the failing op's teaching payload (file_preview, hints)  `62e8126c`
- **desktop** fix(desktop): stop the project tree strobing while it re-probes an unreadable root  `2a36a715`
- **desktop** fix(desktop): don't claim a stranger's cwd as the selected session's workspace  `0401e088`
- **desktop** fix(desktop): let the HUD drag onto another monitor  `e60983a6`
- **install** fix(install): preserve project config for locked uv sync (#82446)  `6da0ae1c`
- **install** fix(install): Node 24.0–24.10 no longer passes the gates only to die at npm EBADENGINE  `15eb5caf`
- **install** fix(install): tier-0 locked sync no longer trips over UV_NO_CONFIG  `c9fa2bba`
- fix: log swallowed reclaim failures + pin ContextVar dispatch invariant (review follow-up for #91217)  `7d1c9aea`
- **gateway** fix(gateway): handoff is broken on multi-profile installs (wrong DB, wrong key, wrong bot)  `fc5fdb8c`
- **desktop** fix(desktop): fill session-switch backfill in two frames instead of ten  `a792d079`
- **desktop** fix(desktop): keep the session loader up while known history is empty  `d2296485`
- **desktop** fix(desktop): hold unproven warm transcripts off the view  `b6eb17d0`
- **update** fix(update): report when the official repo was not checked on the up-to-date path  `be284cf5`
- **update** fix(update): gate the fork-upstream prompt for --yes and non-tty runs  `b33fa127`
- **bots** fix(bots): scope a freshly created bot chat to the bots workspace  `ebb20910`
- fix: make positional prune variant-aware; add replayed-call regression tests  `93f4dc75`
- fix: prune positionally unanswered tool_calls before API send  `c7761573`
- **agent** fix(agent): 413 recovery measures bytes, not token estimates  `b855f86b`
- **gateway** fix(gateway): stop blocking the event loop — off-loop hot sites + ASYNC lint ratchet  `c0ff25a1`
- **desktop** fix(desktop): keep This-device Default on the local source (#97038)  `76da7ff0`
- **desktop** fix(desktop): route the MCP health sweep and command palette through getServers  `9f2ab334`
- **desktop** fix(desktop): drop malformed mcp_servers entries instead of crashing  `13afe9e9`
- **desktop** fix(desktop): a 'This device' Capabilities pick reaches the local machine again under a remote registry primary  `fe576ba4`
- **sanitizer** fix(sanitizer): drop duplicated legacy _classify_tool_call_orphans left by cherry-pick auto-merge  `225fa13b`
- **agent** fix(agent): drop stale api_content sidecar and unpaired tool results  `f0ac2c8f`
- **compression** fix(compression): strip whitespace from tool_call_id in _sanitize_tool_pairs  `e024bf75`
- **compressor** fix(compressor): widen compaction-time image aging to first-message and envelope shapes  `0dce46fe`
- **compressor** fix(compressor): age out stale tool-result images during compaction  `b81b599d`
- **paths** fix(paths): display_hermes_home renders POSIX separators on Windows — kills ~/AppData\Local\hermes chimeras in tool schemas and user-facing messages (#97137)  `a641644f`
- **profiles** fix(profiles): anchor named-profile detection to real Hermes homes  `35328345`
- **profiles** fix(profiles): honor tombstones in exists/backfill and tighten named-home detection  `af2dc685`
- **profiles** fix(profiles): tombstone deleted named profiles so logging cannot resurrect them  `7e345224`
- **sanitize** fix(sanitize): preserve assistant messages with tool_calls when stripping images  `cb8027af`
- **agent** fix(agent): drop the api_content sidecar when stripping images from history  `e1762bd3`
- **install** fix(install): name the supported Node lines in the system-npm gate warning  `ad4adbbf`
- **install** fix(install): reject prerelease Node toolchains  `4d08f515`
- **dashboard** fix(dashboard): harden Node engine alignment checks  `bb06a8d4`
- **scripts** fix(scripts): report unsupported Node lines accurately  `56409af4`
- **dashboard** fix(dashboard): align supported Node engine lines  `4a7df1d0`
- **bots** fix(bots): restore the #97008 session contracts on the rebuilt modules  `d22e8e40`
- **install** fix(install): align npm gate with manifest range  `902cd051`
- **install** fix(install): preserve Node PATH readiness guard  `4572dbf0`
- **install** fix(install): reject incompatible system npm  `3e162900`
- **desktop** fix(desktop): drop legacy tiles missing connectionId and guard partial routes  `108783b4`
- **desktop** fix(desktop): scope tile drops to the deleting connection and normalize route identity  `e3c56f7d`
- **desktop** fix(desktop): drop persisted tiles of deleted profiles so bots cannot resurrect  `ae6d3880`
- **tui** fix(tui): harden failed build recovery handoff  `4e860c09`
- **tui** fix(tui): close failed resume recovery races  `258d0283`
- **tui** fix(tui): recover model switch after failed resume  `dbb98545`
- **vision** fix(vision): degrade image validation gracefully when Pillow is missing  `4029a24f`
- fix: validate PNGs at shared image resolver  `765142d9`
- **vision** fix(vision): reject truncated images before embedding  `ad0e8306`
- **codex** fix(codex): preserve assistant image slots in replay  `b80b9d82`
- **codex** fix(codex): drop assistant images from Responses replay  `8de45940`
- **agent** fix(agent): classify "media exceeds size limit" as image_too_large  `b3f4f507`
- **vision** fix(vision): recover from generic image content rejection  `98a84783`
- **browser** fix(browser): bind CDP binary exemptions to exact method result paths  `628a414d`
- **browser** fix(browser): scope the CDP binary-payload exemption to typed fields (#94138)  `b2a17bfe`
- **browser** fix(browser): keep CDP binary payloads byte-identical through redaction (#94138)  `a5688549`
- **gateway** fix(gateway): drop stale model/provider keys in session model_config  `9ddc6fb2`
- fix: retry text-only on Codex invalid image data errors  `02416190`
- **agent** fix(agent): strip images on Kimi/Moonshot 'failed to decode image' 400  `cd72689e`
- **agent** fix(agent): classify xAI's downloaded-response wording as a corrupt image  `56411357`
- **agent** fix(agent): keep canonical history intact during image-corrupt retry  `a3177d05`
- **agent** fix(agent): narrow #69078 image-corrupt recovery to the classifier route  `d61411d1`
- **agent** fix(agent): un-brick sessions on non-retryable 400s that carry image parts  `8aeb3f6e`
- **skills-guard** fix(skills-guard): exempt all os.environ.get() reads from the env-dump pattern; os.getenv secret reads score medium  `d6a21bc4`
- **skills-guard** fix(skills-guard): handle inline-comment and docstring false positives for os.environ  `54909d41`
- **skills-guard** fix(skills-guard): reduce false-positive CRITICAL/HIGH on benign skill patterns  `42e61494`
- **skills** fix(skills): catch sed flag variants; exempt content-contract prose in plugin code  `8c098e9e`
- **skills** fix(skills): close shell-write and prose-bypass gaps in agent-config tiers  `f2f61e0a`
- **skills** fix(skills): stop agent-config persistence patterns from blocking meta-skills (#92021)  `e22b8b66`
- **execute_code** fix(execute_code): limits line teaches spillover instead of a bare 50KB cap (#97048)  `58572312`
- **bot-mode** fix(bot-mode): backfill follow-profile contract for legacy canonical Bot Chats  `af53d029`
- **bot-mode** fix(bot-mode): canonical bot DMs always follow the profile's current config  `84e17db0`
- **bot-mode** fix(bot-mode): room plumbing sessions always follow the profile's current config  `316e51ae`
- **tui-gateway** fix(tui-gateway): heal or fall back when a resumed session's provider is stale  `99a68520`
- **tests** fix(tests): runtime_provider no longer permanently captures a mocked load_config  `31e41eed`
- **cron** fix(cron): harden _is_named_profile_path against symlinked profile homes  `84d29488`
- **cron** fix(cron): widen deleted-profile protection to all cron mkdir sites  `0dc93671`
- **cron** fix(cron): keep deleted profiles from returning  `000d22b9`
- **compression** fix(compression): don't force a wire cap for explicit caller max_tokens  `1564a974`
- **compression** fix(compression): propagate timing hooks to the protected-call worker  `d24e6a34`
- **compression** fix(compression): close the restore TOCTOU; fold review findings  `e078b2fe`
- **compression** fix(compression): attempt-generation ownership for overlapping stall-fallback attempts  `61cd299c`
- **compression** fix(compression): reject boolean fast caps  `35819834`
- **compression** fix(compression): contain drifted fast controls  `7568dd55`
- **compression** fix(compression): certify the effective fast route  `372c4cdf`
- **desktop** fix(desktop): mount every chat.empty contributor, not just the first  `832ec82f`
- **desktop** fix(desktop): subscribe the bot-chat flag to every store it reads  `0f4d4d4d`
- **desktop** fix(desktop): staleness-probe the adopt-on-conflict canonical open  `8ab34a76`
- **cron** fix(cron): transient run prompt survives the relay-fronted gateway forward  `31579f78`
- **desktop** fix(desktop): a bot row click returns to its open tabs instead of re-opening a closed Bot Chat  `008bc186`
- **macos** fix(macos): harden anchor alias failures — warn, unique staging, marker-last  `0976ceaa`
- **macos** fix(macos): scrub gate env, refuse EACCES, normalize marker paths  `37bccf34`
- **macos** fix(macos): re-land dylib-complete TCC interpreter anchor  `aa72df4b`
- **desktop** fix(desktop): a bot row click returns to its open tabs instead of re-opening a closed Bot Chat  `7c910793`
- **commands** fix(commands): put desktop slash metadata on the CommandDef  `595ee922`
- **desktop** fix(desktop): resolve slash commands from the catalog  `60f58249`
- **desktop** fix(desktop): don't let slash Space steal a leftover highlight  `e870d3fd`
- **cron** fix(cron): resolve api_server host for the manual-run forward (bind parity)  `5cc47c99`
- **cron** fix(cron): don't reference nonexistent 'hermes cron trigger' in relay-fronted errors  `8e811268`
- **cron** fix(cron): forward manual run to the gateway for relay-fronted delivery (NS-773)  `ad0e5223`
- **cron** fix(cron): accurate error for relay-fronted delivery with no live gateway (NS-773)  `2d1d65de`
- **desktop** fix(desktop): three latent bugs in the bot rail, and the dead declarations  `d7f6ef8a`
- **desktop** fix(desktop): bound the two bot-rail caches that grew for the window's life  `71656453`
- **desktop** fix(desktop): refetch Bot Chat on roster reopen instead of idle snapshot  `6ac193e0`
- **desktop** fix(desktop): prevent Bots home flash during chat switch  `6f8be615`
- **agent** fix(agent): count native Responses preflight against pruned wire  `e6b4f375`
- **desktop** fix(desktop): /new inside a bot chat compared against a property that does not exist  `32ca343c`
- **cli** fix(cli): give a profile created without a clone a usable model block  `01a3e9a4`
- **desktop** fix(desktop): bot chats share core's unread and drop the branch rail  `67854b50`
- **desktop** fix(desktop): stop the main zone vanishing behind Bot Mode  `35b53af1`
- **cli** fix(cli): keep journey labels readable  `4956ff0c`
- **compression** fix(compression): dedupe current-turn rows when rotation splits the session mid-turn  `80ab7d2b`
- **compression** fix(compression): surface an unpublished stall-fallback fence at WARNING  `6151e59d`
- **compression** fix(compression): retry a stalled summary on the fallback chain (#78981)  `2c6938dc`
- **bot-mode** fix(bot-mode): keep delivery runner on host backend  `dd401e0f`
- **desktop** fix(desktop): keep bot chat focused when clicking the Bots pane (#96062)  `253b9d78`
- **state** fix(state): journal-mode probe/restore go through _connect_repair_durable  `db63afb9`
- **state** fix(state): guest durability barriers also apply configured database.synchronous  `4882184e`
- **delegation** fix(delegation): expose state durability barriers  `7e6eda7b`
- **delegation** fix(delegation): restore ledger durability barriers  `6548177e`
- **delegation** fix(delegation): preserve state database journal mode  `4a8b4d43`
- **state** fix(state): route the post-repair journal-mode restore through the canonical path  `e40f1be7`
- **state** fix(state): re-apply the configured journal mode after corruption repair  `786e65bf`
- **hermes-bots** fix(hermes-bots): keep the Cronjobs tile registered while it holds focus in Bot Mode  `dbca7a4f`
- **desktop** fix(desktop): keep a restore tab when a pane or strip collapses (#91223)  `584f3a74`
- fix: harden _is_recoverable_error_job against schedule=None  `939dec13`
- **cron** fix(cron): make a recurring job stuck in state=error recoverable again  `ba4c2d52`
- **desktop** fix(desktop): gate transcript budget cap so Show earlier works  `a24c12d1`
- **dashboard** fix(dashboard): trust configured reverse proxies (#94126)  `0dfba37b`
- **tui-gateway** fix(tui-gateway): spare durable rows while a sibling backend holds them  `39f1e188`
- **cli** fix(cli): keep Desktop liveness leases when the session cap is off  `51e67bab`
- **gateway** fix(gateway): disarm the heartbeat writer in _stop_loop_liveness_guards  `8a32baaf`
- **gateway** fix(gateway): a single tick-socket miss must not authorize the wedge kill  `ca4a9ec6`
- **gateway** fix(gateway): interlock the stale-heartbeat wedge verdict with a loop-scheduling witness  `a1c83ef9`
- **gateway** fix(gateway): the loop watchdog's own heartbeat can freeze the loop it watches  `f39931af`
- **state.db** fix(state.db): cross-backend heartbeat gates orphan sweep  `cae58be1`
- **model** fix(model): coerce YAML integer provider names before picker/CRUD  `d83dcb4c`
- **desktop** fix(desktop): unwrap Mistral Voxtral JSON in client-direct STT  `bc737576`
- **desktop** fix(desktop): retain remote owner after session resume  `f54d0154`
- **desktop** fix(desktop): recover cloud auth through portal (#96170)  `46f091b9`
- **mcp** fix(mcp): signal reconnect from the mid-call fast-fail site too + regression tests  `8aae2ea5`
- **mcp** fix(mcp): correct inverted liveness check in _stdio_children_dead  `2663117f`
- **update** fix(update): valid --ignored=matching mode; rename-only path split; shared preserve constant  `f3cbb262`
- **update** fix(update): gitignored user files also block the ZIP overlay  `e64db769`
- **gemini** fix(gemini): embed images in Gemini 3.x functionResponse.parts for multimodal tool results  `2673d5f5`
- **cron** fix(cron): verify a persisted final assistant message before booking complete  `23f597a8`
- **cron** fix(cron): preserve recurring manual run intent  `7e64a483`
- **gateway** fix(gateway): size systemd TimeoutStopSec from the full stop budget  `a3f1cc00`
- **state** fix(state): make state.db synchronous configurable on every platform  `ef29fc63`
- **state** fix(state): warn when an existing database's journal_mode is flipped to WAL  `d5d42b96`
- **state** fix(state): warn when configured journal_mode=delete is overridden by on-disk WAL  `9aeb582e`
- **tui-gateway** fix(tui-gateway): claim disconnect sessions before teardown  `c7601439`
- fix: keep original entry object on same-id recovery — preserve live state (review follow-up)  `726f0ce1`
- **gateway** fix(gateway): keep sessions.json entry when startup recovery succeeds with same session id  `ff3f25e0`
- fix: verify launchd replacement PID before trusting KeepAlive (review follow-up)  `8872cd13`
- **gateway** fix(gateway): use SIGUSR1 graceful restart on launchd, not bare SIGTERM  `7a76046a`
- **gateway** fix(gateway): rebase launchd --replace removal onto main  `1348e65e`
- fix: scope /approve-/deny direct-send confirmations to native-streaming adapters; drop leftover debug log; refresh WeCom docs  `7105657f`
- **wecom** fix(wecom): eliminate duplicate + split bubbles in native streaming  `9faa953c`
- **send_message** fix(send_message): cross-loop dispatch to live WeCom adapter  `42dc0dea`
- **sessions** fix(sessions): don't let the empty-session sweep delete an archived transcript  `0bfe715e`
- **cron** fix(cron): open the session store only after wake-gate and validation early-returns  `3113f605`
- **kanban** fix(kanban): close half-open tracked connection when busy_timeout PRAGMA fails  `a71be985`
- **computer-use** fix(computer-use): accept current notarised CUA Driver  `6662b361`

### 性能（perf，3 条）

- **state** perf(state): route 39 pure-read SessionDB methods off the writer lock + gate  `0534f103`
- perf: skip dict copy for non-compression auxiliary calls  `699bfcd0`
- **compression** perf(compression): add guarded fast summary lane  `213ae08e`

### 回退（revert，1 条）

- **lint** revert(lint): keep the shared eslint configs out of this branch  `531a8cd9`

### 撞特性补丁面（手维护补丁，逐条核对）

**`conversation-cost-panel.patch`**（补丁面 15 文件）：33 个提交撞面

- fix(gateway): gate compute-host interrupt forward on hosted activity  `4396253a`
  - 撞：`tui_gateway/server.py`
- fix(gateway): relay compute-host clarify state  `3ae74119`
  - 撞：`tui_gateway/server.py`
- fix(prompt): preserve resumed workspace provenance  `da090aa4`
  - 撞：`tui_gateway/server.py`
- fix(prompt): skip bundled AGENTS.md for desktop launch cwd  `c6ee4e08`
  - 撞：`tui_gateway/server.py`
- fix(tui): show status while idle/auto compaction runs  `3a542bbe`
  - 撞：`tui_gateway/server.py`
- fix(tui): fail prompt.submit loud only on a real store-open failure  `037a73fa`
  - 撞：`tui_gateway/server.py`
- fix(state): decode errors now reach the heal path and fail loud in TUI (residual #98924 surfaces)  `e17fd0a7`
  - 撞：`tui_gateway/server.py`
- fix(sessions): stamp launch-profile name on new session rows instead of NULL  `6874b99d`
  - 撞：`tui_gateway/server.py`
- fix(tui_gateway): scope config.get/set RPC to params.profile  `fa2dd280`
  - 撞：`tui_gateway/server.py`
- feat(bot-mode): run same-gateway Group Chats without Desktop  `93c7089f`
  - 撞：`tui_gateway/server.py`
- fix(compression): hot-apply native compaction settings  `77f5de62`
  - 撞：`tui_gateway/server.py`
- fix(compaction): preserve switch compatibility fixtures  `48a4201f`
  - 撞：`tui_gateway/server.py`
- fix(compaction): preserve native capability across runtime switches  `08c7879c`
  - 撞：`tui_gateway/server.py`
- fix(todo): unversioned tool.start still merges after resume  `58523f28`
  - 撞：`tui_gateway/server.py`
- feat(tui): status rule shows cache-hit %, latency, t/s and honors display.status_bar.fields  `86a2fdc6`
  - 撞：`tui_gateway/server.py`
- feat(desktop): real-profile browsing toggle in Capabilities → Tools → Browser  `6cb6aeb1`
  - 撞：`apps/desktop/src/i18n/en.ts`、`apps/desktop/src/i18n/ja.ts`、`apps/desktop/src/i18n/types.ts`、`apps/desktop/src/i18n/zh-hant.ts`、`apps/desktop/src/i18n/zh.ts`
- fix(tui): derive resume todo snapshots from already-loaded history  `c0875ba5`
  - 撞：`tui_gateway/server.py`
- fix(todo): live task state via revisioned snapshots and a dedicated todo.updated event  `393af4a3`
  - 撞：`apps/desktop/src/types/hermes.ts`、`tui_gateway/server.py`
- refactor(desktop): menu labels are bare verbs in sentence case  `4054d549`
  - 撞：`apps/desktop/src/i18n/ar.ts`、`apps/desktop/src/i18n/en.ts`、`apps/desktop/src/i18n/ja.ts`、`apps/desktop/src/i18n/types.ts`、`apps/desktop/src/i18n/zh-hant.ts`、`apps/desktop/src/i18n/zh.ts`
- fix(tui): harden failed build recovery handoff  `4e860c09`
  - 撞：`tui_gateway/server.py`
- fix(tui): close failed resume recovery races  `258d0283`
  - 撞：`tui_gateway/server.py`
- fix(tui): recover model switch after failed resume  `dbb98545`
  - 撞：`tui_gateway/server.py`
- fix(gateway): drop stale model/provider keys in session model_config  `9ddc6fb2`
  - 撞：`tui_gateway/server.py`
- fix(bot-mode): backfill follow-profile contract for legacy canonical Bot Chats  `af53d029`
  - 撞：`tui_gateway/server.py`
- fix(bot-mode): canonical bot DMs always follow the profile's current config  `84e17db0`
  - 撞：`tui_gateway/server.py`
- fix(bot-mode): room plumbing sessions always follow the profile's current config  `316e51ae`
  - 撞：`tui_gateway/server.py`
- fix(tui-gateway): heal or fall back when a resumed session's provider is stale  `99a68520`
  - 撞：`tui_gateway/server.py`
- feat(desktop): make tips and guided tours both opt-out (#96835)  `1acd5bb0`
  - 撞：`apps/desktop/src/i18n/ar.ts`、`apps/desktop/src/i18n/en.ts`、`apps/desktop/src/i18n/ja.ts`、`apps/desktop/src/i18n/types.ts`、`apps/desktop/src/i18n/zh-hant.ts`、`apps/desktop/src/i18n/zh.ts`
- feat(desktop): make the idle tip rotation opt-in, ungate the tool  `03579826`
  - 撞：`apps/desktop/src/i18n/ar.ts`、`apps/desktop/src/i18n/en.ts`、`apps/desktop/src/i18n/ja.ts`、`apps/desktop/src/i18n/zh-hant.ts`、`apps/desktop/src/i18n/zh.ts`
- feat(desktop): in-app tips  `baaf3049`
  - 撞：`apps/desktop/src/i18n/ar.ts`、`apps/desktop/src/i18n/en.ts`、`apps/desktop/src/i18n/ja.ts`、`apps/desktop/src/i18n/types.ts`、`apps/desktop/src/i18n/zh-hant.ts`、`apps/desktop/src/i18n/zh.ts`
- fix(tui-gateway): spare durable rows while a sibling backend holds them  `39f1e188`
  - 撞：`tui_gateway/server.py`
- fix(state.db): cross-backend heartbeat gates orphan sweep  `cae58be1`
  - 撞：`tui_gateway/server.py`
- fix(tui-gateway): claim disconnect sessions before teardown  `c7601439`
  - 撞：`tui_gateway/server.py`

### 撞品牌换装覆盖面（542 个提交 / 覆盖面 910 文件）

品牌补丁由 `build/rebrand.py` 规则引擎整张重出，撞面**不需要人工重放**——这里列出只为一件事：上游若改了规则锚点的上下文，替换会无声 no-op，由 `test_hermes_charter.py` 的哨兵负责报红。改动最密的文件：

- `gateway/run.py` —— 47 次改动
- `plugins/platforms/buzz/adapter.py` —— 43 次改动
- `agent/conversation_compression.py` —— 29 次改动
- `hermes_cli/update_cmd.py` —— 22 次改动
- `hermes_cli/config_defaults.py` —— 22 次改动
- `agent/context_compressor.py` —— 19 次改动
- `hermes_cli/gateway.py` —— 19 次改动
- `agent/auxiliary_client.py` —— 17 次改动
- `agent/agent_runtime_helpers.py` —— 17 次改动
- `agent/conversation_loop.py` —— 17 次改动


## 三、下载

| 版别 | 资产 | 链接 |
|------|------|------|
| 私有版（内网日常用） | `black-pool-win64.zip` | [直接下载](https://github.com/lightproud/biav-sc-code/releases/download/black-pool-bundle/black-pool-win64.zip) |
| Release 页（含 SHA-256 digest） | — | [black-pool-bundle](https://github.com/lightproud/biav-sc-code/releases/tag/black-pool-bundle) |

> 链接**恒定**、内容滚动——每次周更由组装线覆盖同一资产名。要核对拿到的是不是这一版，
> 解压后看包内 `BUILD.md` 的「上游 pin」行是否为 `v2026.8.31`。
> 公版 `black-pool-public-win64.zip` 不随周更出包，按需手动触发 `assemble-black-pool-public.yml`。

## 四、BPA 更新指南（内网 bpa-dev 车间）

**推荐路径——双击一键更新**：车间根 `bpa-dev\deploy\update.cmd`。六步流水线自动跑完
① 银芯克隆 `git pull --ff-only` → ② 车间 `svn update` → ③ 下载最新整包进 `releases\`
（SHA-256 比对 Release 官方 digest）→ ④ `assemble.cmd` 组装（按 `config\assembly.txt`
拼内网补丁 / 插件 / 技能 / 配置）→ ⑤ `deploy.cmd` 部署（旧 `home\` 用户数据增量并入，
旧版让位 `.old` 回滚位）→ ⑥ 拉起部署位。日志落 `车间根\update.log`。

**手动路径**（下载失败或要挑版本时）：

1. 从上表下载 zip 进 `bpa-dev\releases\`，比对 Release 页 digest 后登记进 `CHECKSUMS.txt`
2. `assemble.cmd black-pool-win64.zip` —— 出 `staging\BlackPool\` + 装配清单 `ASSEMBLY.md`
3. `deploy.cmd` —— 成品上位，旧版进 `.old`
4. 双击部署位 `Black Pool.lnk` 或 `launcher.cmd` 验收

**验收三看**：包内 `BUILD.md` 上游 pin = `v2026.8.31` · 关于页出身行 = 「基于 Hermes Agent
0.21.0 定制」· 内网补丁在 `ASSEMBLY.md` 里逐张有名有增删行数。

**出事回滚**：`rollback.cmd <部署目录>` 一键回切 `.old`，问题版留 `.failed-*` 供取证。

**纪律提醒**：换包**必经组装**——直接解压 zip 进部署位会丢掉全部内网补丁与配置；
整包不载测试套件（出厂清场已裁），跑 `scripts\run_tests.sh` 会明说原因并指路。
详见 `projects/black-pool-agent/deploy/RUNBOOK.md`。

## 五、需要守密人注意的

**特性补丁**：三张补丁（`conversation-cost-panel.patch` 等）本次全部 `git apply --check` 干净
落位，无一处真冲突需要人工重放；「撞特性补丁面」表里的 33 条只是上下文相邻，不是冲突。

**品牌换装规则**：撞到一处需要人工重锚——上游本次新增的 `data.identity.test.ts` 「重命名不能
顶替内建 @句柄」用例里，裸词换装规则把测试夹具的探针字符串 `'Hermes'`（该处测的是内部技术
句柄 `hermes` 的保留位，与品牌显示名无关）连带扫成了 `'Black Pool'`，导致断言与实现的保留表
对不上、换装后回归网首次跑红（退出码 4）。已在 `build/rebrand.py` 补两条 `BRAND_POST_RULES`
把该测试夹具与其说明注释改回原样（同类先例见文件里 find-in-page 案例），闭环重跑全绿。另有
两处纯文案性错配（`test_hermes_charter.py` 自身断言过期，非换装遗漏）：TUI 提示语上游把
"running in" 精简成 "in"，断言随文案同步；WebUI 提示语上游整条删除（判定为死代码——从未有
代码路径产生 `platform="webui"`，源码注明「do not resurrect this text」），断言随之退役而非
补回假文本。

**引擎版本**：0.20.6 → 0.21.0，小版本跳动，未撞停手清单「引擎主版本号跳变」一条，例程按裁定
自动直推 main（提交 `b4369209`）。

**组装线**：私有版组装 run #28（<https://github.com/lightproud/biav-sc-code/actions/runs/34046015873>）
已回查确认三件全绿——① run 结论 `success`（两个 job：桌面回归网 + win64 装配均绿）；
② Release 资产 `black-pool-win64.zip` 更新时间 `2026-09-06T16:55:47Z`，落在本次 run 窗口内
（非上一版残留）；③ 包内 `BUILD.md` 的上游 pin 行读自本次装配所在 commit `b4369209` 的
`UPSTREAM.md`，该提交已是 `v2026.8.31`（build 日志里 `hermes-agent==0.21.0` 依赖解析结果
交叉印证引擎版本对得上）。zip 直链已可下载最新版。

**gaps.md**：本次无需挂账的漏缝——两处接手均在“测试对齐规则重锚”范畴内解决，没有丢弃任何
补丁或功能。
