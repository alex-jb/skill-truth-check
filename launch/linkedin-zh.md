# LinkedIn - 中文版

> 发布时间:LinkedIn EN 发出后 24h。

我写了 skill-truth-check,一个针对 SKILL.md 的 Brier 风格"可信度审核"工具。

过去 6 周三份独立的 skills 审计相继出来:Trail of Bits 6 月 3 日的供应链分析、Snyk 的 ToxicSkills 论文(13.4% 的 skill 有严重安全问题)、SkillScan 学术论文(26.1% 有漏洞)。三份都指出同一个盲区:

*扫描器能查 skill 是不是恶意的,但没办法验证 skill 的自然语言描述跟它实际跑出来的行为对得上。*

这是"做不做得到"的问题,不是"安不安全"的问题。Snyk 和 Trail of Bits 覆盖恶意,没人覆盖诚实。skills.sh 上 ~669K 个 skill,零审核,这道缝是真的存在。

skill-truth-check 的 pipeline 是我能想到的最小可行实现:

1. 从 SKILL.md 的 YAML frontmatter 解析 `name` + `description`。
2. 用 Haiku 生成 5-10 条针对声明能力的合成 user prompt。
3. 模拟 skill 回答每条 prompt。
4. 用 Sonnet 4.6 当 judge 打 1-5 分,看回答是否符合声明。
5. 把分数映射成确定性的 Brier 分(0 完美 / 1 最差)+ 一句话 verdict:truthful / mostly / partially / unreliable。

关键性质:Brier 那一步是**确定性的、可复现的**。把每条 prompt 的打分存下来,任何人都能重新算出 verdict,不用再花一次 API 钱。Snyk 的审计格式没有这个性质。

v0.1.0。20 条 pytest 测试绿。尚未跑过 skills.sh 真实 corpus(README 已经写明)。单次审核建议当成方向性参考,N>=30 才有稳定信号。

对应 Karpathy 在 Sequoia 讲的 Software 3.0:synth 是 spec,simulator 是行为,judge + Brier 是 verification loop。

MIT,Python,只依赖 stdlib + anthropic SDK。

https://github.com/alex-jb/skill-truth-check
