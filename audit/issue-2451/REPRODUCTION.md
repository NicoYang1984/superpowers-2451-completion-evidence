# 复现说明

## 固定版本与环境

- 上游 `obra/superpowers` 的 `dev`：`b58deb3b948d4c305feeac122700100419ee2777`，package version 7.0.1。
- 本次在 macOS、zsh、系统 Python 3.9、Git、Codex CLI `0.155.0-alpha.9` 执行。
- 真实模型实验使用 `gpt-6-astra`、`medium` reasoning；服务端具体模型快照 ID 不可得。
- 没有使用原 Issue 的 Claude Opus 5.5 / Windows 环境。
- 所有业务数据均为本地生成的虚构内容；无需 API key 写入夹具。CLI 自行使用既有登录，脚本不读取或复制认证文件。

从仓库根目录执行。Python 检查只依赖标准库：

```sh
PYTHONDONTWRITEBYTECODE=1 python3 audit/issue-2451/scripts/test_fixtures.py
PYTHONDONTWRITEBYTECODE=1 python3 audit/issue-2451/scripts/test_fixtures.py --facts
```

该套件通过意味着 **成功辨别夹具缺陷和正常对照**，不意味着缺陷夹具已经修复，更不意味着 Skill 已经能可靠改变 Agent 行为。`fixtures/*/before` 和 `after` 保留修改前后文件；每个 Case 的 `PLAN.md` 和 `HANDOFF.md` 保留要求和带压力的交接声明。

## Case A

`fixtures/A/after/settings.html` 的三个 `section` 仍为 notifications、profile、security；diff 仅更换 heading。HTMLParser 检查结构顺序，不能声称覆盖浏览器布局或 CSS 排序。本夹具没有 CSS/JS 改序。

## Case B

`fixtures/B/after/form.html` 允许 200 字符；`schema.json` 允许 1000；`server.py` 的实际 handler 二次限制为 100。直接调用真实 handler 的 0、99、100、101、199、200、201、1000、1001 长度输入，结果分别为 200、200、200、422、422、422、422、422、400。这里的数字是 handler 返回状态，未启动 HTTP 服务器。测试不把直接函数调用误称为真实 HTTP/浏览器端到端验证。

## 留出 Case C 与正常 Case D

C：导出器源码已支持税额和两条记录，实际交付 CSV 仍缺列、缺行。测试独立检查交付文件，并在临时拷贝执行导出器；生成器正确不等于交付物正确。

D：slug 原有代码满足要求，无新 diff；项目无数据库，条件性迁移要求不适用。它检验补丁是否机械要求产生 diff 或错误扩大任务范围。

## 真实 Agent 运行

首次运行需可用的 Codex CLI 登录，可能消耗账户额度。每个样本建立独立 Git 项目，保留 commit range、diff、prompt、完整 JSONL 事件、stderr、最终报告及用量。脚本拒绝覆盖同名运行目录。清理前请保存证据；为重复运行选择新的 `--runroot` 并归档/改名 `logs/agents`，或使用新 `--label`。

```sh
PYTHONDONTWRITEBYTECODE=1 python3 audit/issue-2451/scripts/run_agents.py baseline --cases ABCD --reps 5 --jobs 3
PYTHONDONTWRITEBYTECODE=1 python3 audit/issue-2451/scripts/run_agents.py patched --cases ABCD --reps 5 --jobs 3
python3 audit/issue-2451/scripts/collect_metrics.py
```

Baseline 从固定上游 commit 读取指令；Patched 从当前 checkout 读取。`--skill-root` 可选择保存的候选快照，`--label` 可区分变体。奇数重复使用 SDD Finish，偶数重复使用 executing-plans Finish。供试 Agent 只报告，不改坏夹具或生成应当存在的交付物。执行前请阅读 `PROTOCOL.md` 和最终 `EVALUATION.md`，特别是 JSONL 是否完整记录工具调用的限制。

本实验是**最终报告阶段的真实模型压力测试**，不是完整 SDD 开发流程，不是官方 Quorum 成绩，也没有验证插件自动触发。完整 Skill 文本作为夹具指令输入，模型可实际调用只读终端核验源代码。

## 上游测试与环境适配

```sh
bash tests/skill-size/test-skill-size.sh
bash tests/claude-code/test-sdd-workspace.sh
bash tests/claude-code/test-executing-plans-scripts.sh
bash tests/codex/test-marketplace-manifest.sh
TZ=UTC bash tests/codex/test-package-codex-plugin.sh
bash tests/hooks/test-session-start.sh
```

最后一项需要 Node 在 PATH。打包测试在 Asia/Shanghai 下会出现 ZIP epoch 的 8 小时时差断言失败，上游未修改版本也失败；仅对该测试设置 `TZ=UTC` 后两组通过。Claude 专属 suite 因未安装 `claude` 无法启动，原始失败日志保留。没有为本 Issue 修改打包脚本、时区逻辑或安装全局依赖。


## 精确重跑最终对照

```sh
PYTHONDONTWRITEBYTECODE=1 python3 audit/issue-2451/scripts/run_agents.py patched --paired --persist --cases ABCDE --reps 3 --jobs 3
python3 audit/issue-2451/scripts/collect_metrics.py
python3 audit/issue-2451/scripts/validate_recordings.py
```

先在新checkout中归档已交付的 `logs/agents/final-*`，并为 `--runroot` 选择新的空路径，避免覆盖原始证据。`--persist` 使用CLI正常会话记录；脚本只读取本次返回的会话ID对应文件，并仅导出工具调用/结果，不扫描其他个人会话内容。CLI通常保存记录到 `~/.codex/sessions`；若使用不同CODEX_HOME，应相应调整脚本路径。

每个样本还提供 `fixture.bundle`，例如：

```sh
git clone audit/issue-2451/logs/agents/final-patched-A-1/fixture.bundle /tmp/replay-final-A-1
```

bundle恢复实际commit、Plan、Handoff、源代码和交付文件。运行时注入的未跟踪指令由metadata里的hash和baseline commit/本地patch恢复；报告保留当时原始临时绝对路径，重放时把命令中的该路径替换为新目录。完整性检查会分别报告可访问的现场源树和不可访问的旧临时目录；缺少现场源树不等于其已被重新验证。

显示用的 `*review.txt` 只规范化行末空白，原始 `events.jsonl` / `raw-tools.json` 不改执行内容。`fix.patch` 保留git format-patch必需的上下文空格，因此只对该补丁归档关闭Git空白诊断。

## Public archive path convention

This public copy replaces private home paths with `/home/REDACTED`, and historical macOS temporary roots with `/tmp`. These are redacted historical paths, not claims that those directories exist on your machine. Replace the fixture prefix with your cloned bundle directory when replaying a recorded command. The publication archive includes all 30 final comparisons and the collector diagnostic; discovery-round raw logs remain local. `logs/metrics.json` here contains only the final 30 measured sessions. Do not run the model examples just to inspect the archive. See `PUBLICATION.md` for the offline check.
