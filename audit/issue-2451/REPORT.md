# Superpowers #2451：完成报告证据核验

本地候选只在 SDD 和 executing-plans 的 Finish 阶段引入共享的逐要求证据契约，未引入服务、依赖或状态管理框架。它是可供审阅的候选改动，不代表原 Issue 已被证明修复。最终配对轮每组15次：虚假功能完成声明均为0，缺口识别均9/9；严格证据完整率从6/30提升到30/30，平均耗时约增加7%。完整统计以 [EVALUATION.md](EVALUATION.md) 为准。

## 问题、复现范围与根因

[原 Issue #2451](https://github.com/obra/superpowers/issues/2451) 描述了两个不同层次的偏差：把目标顺序当作实际顺序，以及把读取较宽松的 schema 当作核验全部服务器约束。当前 `dev` 虽然已有任务完成契约、review package、最终代码审查和 verification-before-completion，但最终总结仍没有必须填入的逐要求证据字段。计划、ledger和review判定容易成为摘要依据；代码存在变化或测试绿灯又容易被扩展解释为所有要求均完成。

这不是“完全没有行为规则”：verification-before-completion已有逐行checklist要求。缺的是执行入口到最终报告的显式交付契约，以及将每个声明连接到正确范围的证据。最终review审核代码，并不自动审核随后自由撰写的总结。仅增加“要诚实”“先验证”等重复警告不提供可检查的报告结构。

本次在隔离Git项目真实搭建了A/B错误实现、C陈旧交付物、D无diff正常实现和E缺少staging验证条件。独立oracle能稳定发现所有种植缺陷；没有将fixture里的错误实现改成正确后再冒充完成报告测试。

实际供试Agent主要识别出了A/B/C的缺口。这意味着**成功复现了问题状态和报告证据缺口，但没有在该模型上复现原文两种虚假功能完成声明**。不能从Baseline和Patched都识别缺陷，推出补丁降低了功能误报率。

## 本地改动

仅三个生产文档：

1. `skills/subagent-driven-development/references/final-review.md`：在Finish、清理workspace之前读取共享契约。
2. `skills/executing-plans/SKILL.md`：同样接入Finish，避免两个执行路径行为不同。
3. `skills/verification-before-completion/references/completion-evidence.md`：每个要求独立记录状态、实现位置、实际diff或已有实现、运行检查及结果、证据范围。报告从映射生成，而非从计划目标生成。

四种状态为 `implemented_and_verified`、`implemented_but_unverified`、`not_implemented`、`not_applicable`。已有代码满足要求时允许无diff；条件不成立时明确N/A；无法验证时显式保留未知；不能用局部测试或schema读取推出整个路径已验证；生成器和实际交付文件分别检查。清理临时目录前保留报告及所引证据，防止最终链接指向已删除的日志。

没有修改原有Red Flags、rationalization表、“human partner”措辞、review次数、分支集成选项或运行时逻辑。`audit/issue-2451/` 中的脚本、夹具和报告是独立研究材料，不建议原封不动捆绑进核心PR。

第一版让输出有了证据表，但仍常用“Python check passed”概括实际命令。第二版补充了一个可检查的字段要求：内联检查给出可执行主体，命令与结果来自已完成的工具执行；代码阅读和测试执行分别表述。

## LLM与确定性验证的分工

| 工作 | 更合适的责任方 | 边界 |
|---|---|---|
| 分解计划、理解验收目标、选择相关验证层、判定检查是否充分 | LLM + 人类复核 | 不能仅凭字段齐全判定语义正确 |
| 检查commit存在、diff范围、未提交文件、路径/行号、交付文件是否存在 | Git/脚本/runtime | 非空diff不证明功能正确；零diff不证明没做 |
| 执行命令、保留退出码/输出、关联文件状态与运行时间 | runtime | 由模型填写“exit 0”仍只是声明；需要真实事件 |
| 已知业务条件的验收、边界输入、实际CSV内容 | 项目自己的可执行oracle | 覆盖范围有限，不能自动穷尽未知系统 |
| 把完整语义要求映射到最终报告、列出剩余工作 | LLM | 由reviewer或用户核查证据与结论是否匹配 |

本候选保持Skill层改动。没有声称其能提供Runtime级保证。若未来需要硬门禁，最小可行方向是由现有Runtime绑定实际执行事件与revision、验证引用可解析性；不要为了此Issue创建新的集中服务或自定义项目状态数据库。

## 实验与记录质量

按仓库writing-skills规则先运行Baseline，再冻结候选；五次微测试验证输出形态；留出C/D不用于修改措辞。最终配对轮同模型、同reasoning、同夹具、同报告阶段任务、同只读限制，两组都保存原始工具记录。没有把按关键字命中等同于行为成功，也没有要求Baseline使用新状态的精确拼写；语义等价的status同样计分。

一次重要的自我纠正：早期CLI `--json`中缺少部分Python调用，初步怀疑报告声称了不存在的执行。随后通过新建的synthetic nonce诊断和原始rollout核对，发现嵌套`functions.exec`调用可在原始工具记录中出现、却在CLI的command_execution事件中缺失。该怀疑被撤回。最终实验补采原始调用，早期不完整记录不能用来证明“伪造执行”。纠正过程保留在 `logs/red-observation.md`；没有伪造补充日志，也没有把后来运行的oracle冒充Agent当时运行的检查。

## 测试与可复现性

详见 [REPRODUCTION.md](REPRODUCTION.md)、[EVIDENCE_MATRIX.md](EVIDENCE_MATRIX.md) 和 `logs/`。确定性测试覆盖真实HTML顺序、实际handler双层约束、CSV交付内容、执行生成器、已有无diff实现、修复后正向对照、空文件/错误值对抗变体及无法证明staging的边界。

上游脚本测试中，Skill大小、工作区管理、executing-plans脚本、Codex manifest通过。找到bundled Node后启动钩子测试通过。打包时间戳在Asia/Shanghai下失败，上游和本候选一致；`TZ=UTC`后两组通过。Claude Code完整skill suite因CLI缺失未运行，官方Quorum也未运行。本地测试不替代跨模型、跨平台、完整工作流验证。

## 社区与下一步

已检索的相邻PR和贡献限制见 [PRIOR_ART.md](PRIOR_ART.md)。未创建PR、未推送上游。没有得到维护者邀请或真人完整diff审阅。

本地材料足以让维护者讨论“最终报告契约”是否值得进一步评估，尚不足以宣布已修复原模型上的问题。正式贡献前需要维护者明确邀请、真人审核完整diff并撰写要求的人工摘要，以及补充原环境/更易暴露假完成声明的自然长任务评测。应优先验证效果，而非只扩大强制措辞。


## 公开版本说明

生产补丁 commit 为 `968c13faadad3de0a492580fe75db3f91620ad25`（3 文件、61 新增行）。此仓库是独立实验材料，不是上游发行版。最终30次对照完整保留；探索轮数量作为历史方法记录，探索轮原始日志留在本地，不与主比较混算。公开副本做路径脱敏，详见 [PUBLICATION.md](PUBLICATION.md)。未获得维护者邀请或真人完整diff审阅，也未创建上游PR。
