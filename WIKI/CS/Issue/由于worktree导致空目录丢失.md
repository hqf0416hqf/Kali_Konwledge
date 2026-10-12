让Codex/Copilot整理笔记时，他为了执行任务自动创建了一个 Git worktree，然后把工作区迁移/整合成了一个新的工作树：  
Git 只记录文件，不记录空目录；  
只创建过目录、但里面还没有文件的路径，不在 Git 里；  
worktree 重建时，这些目录不会被复制；  
所以看到的结果就是：写过文件的目录还在，很多仅用于分类的目录突然消失。  

 # 本次目录消失问题排错记录

  ## 一、问题现象

  本次问题表现为：

  - 知识库中大量目录突然消失；
  - 只剩下一些曾经写过文件的目录；
  - Git 仓库仍然可以打开；
  - 已经提交过的 Markdown 文件仍然存在；
  - 部分未提交但有实际文件内容的目录也仍然存在；
  - 许多原本用于分类、但暂时为空的目录消失；
  - 系统回收站中没有这些目录；
  - Git 历史中没有明显的批量删除提交；
  - 用户感觉像是整个目录树被“自动整合”或重新生成了。

  当前工作区中仍然存在的文件包括：

  CS/Issue/中文乱码.md
  CS/tools/CMake/CMake.md
  CS/tools/Git/Git.md
  CS/tools/Makedown/Makedown.md
  CS/tools/Regex/Regex.md
  CS/tools/Shell/Shells.md
  Math/Probability‑And‑Statistics/Probability.md
  Math/Probability‑And‑Statistics/Statistics.md
  CS/fundamention/Computer_Organization/Computer_Organization.md
  CS/tools/Embedded/Embedded.md
  Fish/Fish.md
  Fish/image/鳙鱼.webp

  而以下目录存在但已经没有内容，或者目录本身已经不再完整：

  CS/Programming_Language
  CS/Programming_Language/pro_language
  CS/fundamention/Data
  CS/fundamention/network
  CS/fundamention/structure
  fish
    .....
  ## 二、排查思路

  ### 1. 先检查当前工作区

  首先确认当前所在目录：

  pwd

  结果：

  /home/kali/Kali/Kali_knowldge

  然后查看当前文件：

  rg --files

  发现当前工作区确实只剩少量文件，但仍有一些未跟踪文件存在。

  接着查看 Git 状态：

  git status --short --branch

  结果显示：

  ## master...origin/master
  ?? CS/fundamention/
  ?? CS/tools/Embedded/
  ?? Fish/

  这说明：

  - 已提交文件没有被 Git 标记为删除；
  - CS/fundamention、CS/tools/Embedded、Fish 是未跟踪目录；
  - 当前工作区不是简单的“全部文件被 Git 删除”。

  ### 2. 查看 Git 当前提交包含哪些文件

  使用：

  git ls-tree -r --name-only HEAD

  结果表明当前 master 提交只包含 8 个文件。

  这说明大量消失的目录并不是在当前 Git 提交中被删除的，而是根本没有被 Git 记录。

  ### 3. 查看提交历史和删除记录

  检查最近提交：

  git log --oneline --decorate -8

  检查是否存在删除提交：

  git log --all --diff-filter=D --summary

  结果没有发现包含大量删除操作的提交。

  同时检查分支：

  git branch -avv

  当前主要分支为：

  master
  origin/master
  copilot/worktree-2026-09-23T12-52-09

  ### 4. 查看 Git reflog

  使用：

  git reflog --all --date=iso

  发现了关键记录：

  2026-09-23 20:52:10 reset: moving to HEAD
  2026-09-23 20:52:09 branch: Created from HEAD
  2026-09-23 20:52:21 commit: Refactor code structure for improved readability and maintainability

  同时发现创建了一个 Copilot worktree：

  /home/kali/Kali/Kali_knowldge.worktrees/copilot-worktree-2026-09-23T12-52-09

  ### 5. 查看 Copilot worktree

  检查该 worktree：

  rg --files /home/kali/Kali/Kali_knowldge.worktrees/copilot-worktree-2026-09-23T12-52-09

  发现这个 worktree 中也只包含有文件的目录，没有那些空目录。

  该 worktree 后续还产生了提交：

  6a5915d Refactor code structure for improved readability and maintainability

  提交内容主要是添加以下文件：

  CS/fundamention/Computer_Organization/Computer_Organization.md
  CS/tools/Embedded/Embedded.md
  Fish/Fish.md
  Fish/image/鳙鱼.webp

  这说明 Copilot worktree 在创建和整合时，确实按照“Git 文件树”重新建立了工作目录。

  ### 6. 检查 Git 不可达对象

  使用：

  git fsck --full --no-reflogs --unreachable

  发现了几个不可达提交：

  1674ca8590a77c4244ecdf02bee11c0cc2ed4c8a
  1365d5cb2d344515a8cc5356c1c342850415a949
  bc18781ab1074519e7b9fa4106130b33382ec4e1

  进一步检查发现：

  - 1674ca8 是当前提交的临时索引；
  - 1365d5c 只是保存了 4 个未跟踪文件；
  - bc18781 是 worktree 迁移过程中的临时提交；
  - 这些提交都没有包含消失的空目录。

  因此，Git 对象库中没有完整的旧目录结构备份。

  ### 7. 检查回收站

  检查：

  find /home/kali/.local/share/Trash -maxdepth 3 -type f

  回收站中没有知识库目录或相关文件。

  这说明问题不是通过文件管理器删除产生的。文件管理器删除通常会将内容移入回收站，而 Git/worktree 操作不会经过回收站。

  ### 8. 检查文件系统

  使用：

  findmnt -T /home/kali/Kali/Kali_knowldge

  得到：

  /dev/nvme0n1p7
  ext4

  这说明底层文件系统是 ext4，理论上可以尝试文件系统恢复，但恢复主要针对已经存在过的文件内容，对“只有空目录、没有文件”的目录恢复能力非常有限。

  ### 9. 检查 VS Code 历史

  发现 VS Code 本地历史目录存在：

  /home/kali/.config/Code/User/History

  其中保存的是曾经在 VS Code 中打开或编辑过的文件历史。

  但 VS Code Local History 只能恢复文件内容，无法恢复纯空目录，因为空目录没有文件版本可供保存。

  ## 三、涉及的知识体系

  本次问题涉及多个知识点。

  ### 1. Git 的对象模型

  Git 实际上记录的是：

  - 文件内容；
  - 文件路径；
  - 文件权限；
  - 目录层级关系。

  Git 并不单独保存空目录。

  例如：

  project/
  ├── CS/
  │   └── tools/
  │       └── Git/

  如果 Git 目录里面没有任何文件，Git 不会把这个目录单独记录下来。

  只有目录中存在文件，例如：

  CS/tools/Git/Git.md

  Git 才能通过文件路径间接保存目录结构。

  ### 2. Git worktree

  git worktree 允许同一个 Git 仓库同时存在多个工作目录。

  每个 worktree 通常根据 Git 的提交树建立文件系统：

  Git commit tree
          |
          v
  worktree filesystem

  它会创建提交中存在的文件和目录，但不会恢复 Git 不认识的空目录。

  ### 3. 未跟踪文件

  Git 状态中的：

  ?? directory/

  表示目录中有未跟踪内容。

  未跟踪文件没有进入提交前：

  - 不受 Git 版本控制；
  - 不一定会被 worktree 完整保留；
  - 不能通过 git log 找回；
  - 不能保证在 reset、迁移或自动整合后继续存在。

  ### 4. Git reset 和 worktree 迁移

  git reset、worktree 创建和自动迁移可能会重新整理工作目录。

  如果原来的目录中包含：

  - 空目录；
  - 没有提交的文件；
  - 未被迁移工具复制的临时内容；

  那么重新生成目录结构时，这些内容可能不会出现在新工作区中。

  ### 5. 回收站机制

  文件管理器删除通常会进入：

  ~/.local/share/Trash/files

  但是 Git、脚本、同步工具、worktree 或文件系统层面的操作通常不会使用回收站。

  因此：

  回收站为空

  并不能证明文件没有被删除，只能说明它们不是通过常规桌面删除操作移除的。

  ### 6. ext4 文件恢复

  当前分区是：

  /dev/nvme0n1p7
  ext4

  如果文件曾经存在但被删除，可以尝试：

  - TestDisk；
  - extundelete；
  - debugfs；
  - PhotoRec；
  - 从磁盘镜像中恢复。

  但要注意：

  - 空目录本身没有文件内容；
  - PhotoRec 主要恢复文件内容，不擅长恢复目录树；
  - 后续磁盘写入会覆盖被删除的数据；
  - 不应该直接在原分区上运行高风险修复命令。

  ## 四、最终确定的问题

  最终判断是：

  > 本次目录消失主要是 Git/Copilot worktree 自动创建和整合工作区时，只根据 Git 记录和实际文件重新生成目录树，导致没有文件、没有被 Git 跟踪的空目录结构没有被保留。

  具体过程大致是：

  原始工作区
      |
      | 存在大量空目录或未纳入 Git 的目录结构
      v
  Copilot 创建 worktree
      |
      | 根据 Git 提交树和可见文件建立新工作区
      v
  执行 reset / worktree 迁移
      |
      | Git 不知道空目录
      v
  空目录没有被创建

  这不是典型的：

  git rm

  也不是典型的：

  git reset --hard

  删除了大量已提交文件。

  更准确地说，是：

  未被 Git 记录的目录结构在 worktree 迁移时没有被带过去

  这也解释了为什么：

  - 写过文件的目录还在；
  - 已提交文件还在；
  - 空目录消失；
  - 回收站为空；
  - Git 没有删除记录；
  - worktree 中也不存在这些空目录。

  ## 五、当前可行的解决方案

  ### 方案一：从 VS Code Local History 恢复文件

  检查：

  /home/kali/.config/Code/User/History

  查看某个历史目录：

  cd /home/kali/.config/Code/User/History/5da5d375
  ls -la
  cat entries.json

  注意：

  cd entries.json

  是错误的，因为 entries.json 是文件，不是目录。

  应该使用：

  cat entries.json

  或者：

  less entries.json

  可以搜索知识库相关历史：

  rg -i -n \
    -g 'entries.json' \
    'Kali_knowldge|Programming_Language|fundamention|Fish/|CS/|Math/' \
    /home/kali/.config/Code/User/History

  如果找到历史文件，先恢复到临时目录：

  cp 历史版本文件 /tmp/recovered.md

  确认内容后再放回知识库。

  ### 方案二：重新创建目录结构

  对于纯空目录，只能根据记忆、截图、编辑器工作区记录或旧笔记重新创建：

  mkdir -p \
    CS/Programming_Language/pro_language \
    CS/fundamention/Data \
    CS/fundamention/network \
    CS/fundamention/structure \
    fish

  ### 方案三：使用 .gitkeep 保存空目录

  Git 不记录空目录，因此需要放置占位文件：

  touch CS/Programming_Language/.gitkeep
  touch CS/Programming_Language/pro_language/.gitkeep
  touch CS/fundamention/Data/.gitkeep
  touch CS/fundamention/network/.gitkeep
  touch CS/fundamention/structure/.gitkeep
  touch fish/.gitkeep

  然后提交：

  git add .
  git commit -m "保存知识库目录结构"
  git push

  这样以后 worktree、分支切换和重新克隆都会保留这些目录。

  ### 方案四：尝试 ext4 文件恢复

  如果确认目录中原本有实际文件，而不是纯空目录，应立即：

  - 停止继续写入该分区；
  - 不执行 git clean；
  - 不执行 git reset --hard；
  - 不执行 fsck；
  - 不重新克隆覆盖原目录；
  - 先制作 /dev/nvme0n1p7 的磁盘镜像；
  - 再对镜像运行 TestDisk 或 extundelete。

  恢复操作不建议直接在当前挂载分区上进行。

  ## 六、当前无法恢复的部分

  目前没有发现以下可用备份：

  - Git 提交；
  - Git stash；
  - Git reflog 中的旧目录树；
  - Git 不可达对象中的完整目录结构；
  - 系统回收站；
  - Copilot worktree 中的旧空目录；
  - 明确的磁盘快照。

  因此，以下内容如果曾经只是空目录，目前无法从 Git 中恢复：

  目录名称
  目录层级
  目录排序
  目录分类关系

  除非这些信息还存在于：

  - 文件管理器最近访问记录；
  - VS Code 工作区配置；
  - Obsidian 或其他笔记软件配置；
  - 云同步历史；
  - 磁盘快照；
  - 文件系统 journal；
  - 手写记录、截图或备份。

  ## 七、后续防止再次发生

  以后建议采用以下方式保存目录结构。

  ### 每个分类目录放 .gitkeep

  例如：

  CS/
  ├── Programming_Language/
  │   ├── .gitkeep
  │   └── pro_language/
  │       └── .gitkeep

  ### 及时提交

  不要积累大量未提交内容：

  git add .
  git commit -m "更新知识库目录结构"
  git push

  ### 定期打包备份

  可以定期创建完整压缩备份：

  tar -czf \
    /home/kali/Kali_knowldge-backup-$(date +%Y%m%d-%H%M%S).tar.gz \
    /home/kali/Kali/Kali_knowldge

  ### 使用 Git 前先确认状态

  执行高风险操作前先看：

  git status --short
  git branch -avv
  git worktree list

  ### 不要让自动化工具直接迁移重要工作区

  对于重要知识库，建议：

  - 先提交当前更改；
  - 再创建 worktree；
  - 使用独立的临时仓库副本进行 AI 操作；
  - 不让自动化工具直接操作主工作目录。 

  ## 八、总结

  本次问题的核心不是“Git 把所有文件删掉了”，而是：

  > 空目录和未被 Git 记录的目录结构，在 Copilot/Git worktree 自动重建工作区时没有被保留。

  已经提交的文件没有发现批量删除证据，未跟踪但实际存在的 4 个文件也仍然在当前工作区。真正消失的主要是：

  - 空目录；
  - 未纳入 Git 的目录结构；
  - 或者未提交且没有进入 VS Code 历史的文件。

  目前最现实的处理顺序是：

  1. 暂停对该分区的大量写入；
  2. 检查 VS Code Local History；
  3. 根据记忆重新创建目录；
  4. 为目录添加 .gitkeep；
  5. 提交并推送 Git；
  6. 对真正丢失且有文件内容的部分，再考虑 ext4 镜像恢复。
 