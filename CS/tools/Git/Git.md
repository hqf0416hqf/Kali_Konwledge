# Git
## 本地
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