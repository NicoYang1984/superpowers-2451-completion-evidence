# 上游检索与贡献边界

检查日期：2026-10-26。初次查询及公开准备复查时，Issue #2451均开放且0评论。此前按2451检索所有状态PR没有命中；原始查询响应保留本地，公开副本仅保留直接上游链接。关键词检索不是对所有PR的穷尽证明。

| 先例 | 查询时状态 | 与本地候选的关系 |
|---|---|---|
| [#2324](https://github.com/obra/superpowers/pull/2324) | open、未合并 | verification证据来源；没有给两个执行入口增加逐要求完成报告映射。其静态内容断言不能替代行为评测。 |
| [#2270](https://github.com/obra/superpowers/pull/2270) | closed、未合并 | 非代码交付物核验；维护者关闭评论提到缺少eval以及目标main。这里仅处理计划结束阶段，并保留真实实验。 |
| [#2255](https://github.com/obra/superpowers/pull/2255) | open、未合并 | 删除workspace前导出deferred/parked/rulings。本候选保留证据映射，不重构其导出设计。两者可能触及相同Finish位置。 |
| [#1688](https://github.com/obra/superpowers/pull/1688) | closed、未合并 | 根据Git检查子代理自报。维护者要求实际reviewer transcript；仅有非空diff仍无法证明功能。 |
| [#578](https://github.com/obra/superpowers/pull/578) | closed、未合并 | 与按requirement提供file:line最接近；同时引入persistent validator/team流程。这里避免那些框架变化，只加最终报告的共享契约。 |

仓库 `README.md`、`AGENTS.md`、`.github/PULL_REQUEST_TEMPLATE.md`、`writing-skills` 及TDD规则已读取。遵守“不经维护者邀请，不为他人Issue提交Agent修复PR”的边界：只做本地实现和commit，不创建PR、不推送上游。没有真人完整diff审阅，没有维护者授权，不能冒充已具备提交条件。

`superpowers-evals`（Quorum）的README及 verification-phantom-completion、verification-holds-under-just-confirm-pressure、claim-without-verification-naive场景已读取。官方完整eval需要额外runtime/QA模型认证，本次用直接Codex CLI最终阶段测试替代，不声称运行了Quorum或官方认证。现有 `tests/claude-code` 全流程依赖缺失的Claude CLI；可独立运行的脚本测试已执行。
