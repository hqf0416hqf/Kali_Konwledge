# Git
## 推荐学习链接
 [Learn Git Branching学习网站](https://learngitbranching.js.org)
## 本地
一工作区域
工作区--git add-->暂存区--git commit-->本地仓库

二状态
"Untract"----"Unmodified"<--git checkout--"Modified"<--git reset--"Staged"

三命令
git init
git add
git commit
git log
git reflog
git status
git reset       --soft	        版本id	
		--hard		HEAD^  #这个表示上一个版本			
		--mixed			
git diff	默认工作区/暂存区
		HEAD
		--cached
		版本id1	版本id2/版本id1 HEAD/...   
四“file work”
.git
.gitnore


五
Git
│
├── ① 仓库基础
│   ├── git init
│   ├── .git
│   ├── .gitignore
│   └── git status
│
├── ② 本地版本管理
│   ├── 工作区
│   ├── 暂存区
│   ├── git add
│   ├── git commit
│   ├── git log
│   └── git diff
│
├── ③ 远程仓库
│   ├── remote
│   ├── git remote
│   ├── git fetch
│   ├── git pull
│   └── git push
│
├── ④ 分支
│   ├── main
│   ├── branch
│   ├── switch
│   ├── checkout
│   ├── merge
│   └── conflict
│
├── ⑤ 版本回退/修改历史
│   ├── restore
│   ├── reset
│   ├── revert
│   └── reflog
│
└── ⑥ GitHub 协作
    ├── SSH / Token
    ├── Pull Request
    ├── Fork
    ├── Code Review
    ├── 权限
    └── Issues


gitcommit
* 指向当前分支
- 创建分支  
    - git branch <分支名>
- 切换分支
    - git checkout <分支名>
- 分支融合
    - git rebase  <分支x>  //将当前HEAD指向分支移到分支x      //Rebase 优势：提交历史更线性
    - git merge <分支x>  //将融合当前分支和分支x
- HEAD 指向当前分支上最近一次提交记录
    - git checkout 分支名/版本名/对应哈希值 //分离HEAD，使得指向具体版本，而不是某个分支
- `^`和`分支名~x`
- 撤销变更
    - git reset
    - git revert
- git cherry-pick
- git rebase -i c1 c2 c3!!(好用，交互式调整未上传的版本)

- git restore
- git add
- .gitnore 
- git checkout
- git branch -f <移动分支名> <目标哈希>

## 远程
## 问题
- **如何绑定远程仓库**
    1. 准备:github上建立仓库（并复制仓库链接） 和 本地初始化`git init`
    2. 绑定:`git remote add origin  [远程仓库地址](https://github.com/hqf0416hqf/Kali_Konwledge.git)`
    3. 验证:`git remote -v `（如果出现fetch和push两条地址代表绑定成功）
- **如何回到上一个提交版本**
    - hard退回`git reset --hard HEAD~1` 慎用，直接删除本地所有未提交改动
    - soft退回`git reset --soft HEAD~1` 保留修改，代码不变，仅撤销commit
- 
- 
- 



、、草稿、、、、、、、、、、、、、、、、、、、、、、、、、、、
git branch -av
git log --oneline --decorate --graph --all -n 20