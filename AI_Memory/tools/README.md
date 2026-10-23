# 本地检索与上下文工具

适用：Python 3.10+、UTF-8 Markdown；仅使用标准库，无安装依赖、联网或模型费用。保留原有 `ai_study_lab_01` 教学包，本目录提供阶段 1、2 的可运行版本。

## 日常使用

在仓库根目录执行（其他目录执行时可提供脚本绝对路径；默认根目录由脚本位置确定）：

```bash
python3 AI_Memory/tools/study.py search pwd --scope WIKI
python3 AI_Memory/tools/study.py search HEAD 分支 --scope WIKI RAW --limit 5 --json
python3 AI_Memory/tools/study.py context 'Linux 目录操作该从哪里接续？' --terms Linux pwd cd --budget 12000
python3 AI_Memory/tools/study.py check
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s AI_Memory/tools/tests -v
```

`search` 输出相对路径、章节、原文行号、正文、文件 SHA-256。多个词按 OR 匹配，按命中词种类、标题与文件名、匹配行数排序。大小写不敏感；中文使用子串匹配。参数 `--context` 控制知识片段前后行数；学习记忆保留完整章节以免漏掉证据限制。

`context` 将问题、画像、断点、相关记忆和知识正文组成 Markdown，默认最多 12000 个 Unicode 字符（不是模型 token）。每类有预算，省略数量明确输出。输出可人工选取后交给聊天入口；例如末尾加 `> /tmp/study-context.md` 保存本轮临时包。资料只作为引用，不作为命令执行。

问题用于展示，`--terms` 才是实际检索词。不会自动将“查看 USB”推断成 `lsusb`，宽泛词可能带入不相关结果，需要人工审阅、换词。未匹配与缺目录分别报告；文件读取失败输出警告。当前仓库 WIKI 中 `lsusb` 无匹配，不能复用旧实验预期。

## 索引与数据流

Markdown 始终为权威数据源。现阶段采用每次扫描、按 Markdown 章节分块的内存检索，不维护持久索引；新增、移动、修改、删除在下次查询立即反映，避免缓存漂移。来源哈希用于发现引用后内容变化，不代表内容正确。

流程：显式关键词 → 允许目录中的 Markdown → 章节匹配与排序 → 带来源片段 → 按类别及字符预算组装。Profile 与断点固定加载，学习状态和知识按需选择。目录导航见 [记忆入口](../README.md)。

工具跳过符号链接及隐藏子目录，并排除 AI_Memory 内的 `tools/`、`History/`；WIKI 的 `CS/tools/` 正常参与检索。只读取 WIKI、RAW、AI_Memory、AI_Profile；不会执行笔记代码、自动遍历浏览器或发送上下文。

## 学习状态更新、纠错和恢复

按 [证据约定](../README.md) 由人或 AI 先审阅判断与证据，准备完整 Markdown 候选文件（建议放 `/tmp`）。更新工具只验证格式、路径及版本，不自动判定掌握程度。

```bash
sha256sum AI_Memory/CS/学习状态.md
python3 AI_Memory/tools/study.py update AI_Memory/CS/学习状态.md \
  --content-file /tmp/state-candidate.md --expected-sha 当前完整SHA256 \
  --source '会话链接或原文件路径、章节、行号' \
  --reason '说明证据变化、纠错或撤回原因' --date 2026-10-22
```

默认只预览元数据，不写文件。先用 `diff -u AI_Memory/CS/学习状态.md /tmp/state-candidate.md` 审阅正文差异；确认候选内容后，对同一命令追加 `--apply` 才写入。新文件使用 `--expected-sha NEW`。日期是证据日期，未知日期请在正文明确说明并采用本次核验日期。

写入仅限两个记忆目录的 Markdown 正文，拒绝 WIKI、RAW、tools、History、路径逃逸及符号链接。旧文件哈希不符时拒绝覆盖。先在 `AI_Memory/History/change-*/` 保存 `before.md`、`after.md`、来源和原因，再原子替换目标正文；归档不参与检索。此机制适合单写入者；不是多进程锁或操作系统权限隔离，不要并发写同一文件。

- 纠错或撤回：在原条目修正当前判断，注明旧判断已失效及原因，再更新引用处；不要只追加一个冲突结论。
- 恢复：检查归档 `change.json` 的目标路径，使用 `before.md` 作为候选，配合目标的当前 SHA-256 按上述流程预览、恢复。新增文件的旧版为空，撤销新增需明确授权后人工删除。
- 删除：明确删除范围后人工删除目标内容和相关引用，再运行 `check`。归档、Git 历史和已导出副本可能仍保留原内容，隐私删除需分别处理，不声称一次操作清除了所有副本。
- 归档写入成功而后续失败时，可能留下未应用的候选；以目标文件哈希和 `applied` 字段共同核对。归档是本机恢复记录，不是异地备份。

## 验证与边界

自动测试使用临时仓库，包含搜索来源、范围隔离、文件变化、编码错误、符号链接、上下文预算、更新预览、版本冲突、越界拒绝、归档恢复及链接检查。真实笔记的实测见 [阶段验收](../Projects/阶段1-2验收.md)。

`check` 核验记忆正文中的相对文件链接，不校验外链、Obsidian 渲染、章节锚点或事实真实性。尚无自动自然语言检索、语义索引、自动能力评级、模型回答、聊天同步和后台任务。无需为了使用阶段 1、2 而配置 API。
