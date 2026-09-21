# SHELL

## 脚本解释器（shell）
常用shell ：bash ,zsh ,rbash ......  
`cat etc/shells` 查看系统中所有的shell版本


## 脚本类型
- 普通bash脚本：`xxx.sh` 文件。启动方式: 手动输入  `./xxx.sh`  或者  `bash xxx.sh`  ，用来做自动化批量操作。  
    ***(注意运行前要 `chmod` 加权限)***
- `.bashrc` `.profile` 属于（当前用户）自动加载的特殊脚本，每次打开交互式终端（新开终端窗口、ssh登录），系统会自动读取并执行里面所有代码，不用你手动运行
- `/etc/profile.d/*.sh`  属于（全局）自动加载的特殊脚本  


## 基本脚本格式（举例）

```bash
#!/bin/bash   
# 说明选择的脚本
echo "你好，$1,欢迎来到$2"  

name=$1
channel=$2
echo "你好，$name,欢迎来到$channel"
```

## 常用脚本变量
- `$1` 第一个输入命令参数
- `$2` 第二个输入命令参数
- `$HOME` 家目录
- `$PATH` 系统命令的查找路径
    - 作用: 可执行文件放在  PATH  包含的任意目录中，无论当前处于哪个工作目录，直接输入文件名就能执行.  
            如果程序所在目录不在 PATH 内：只能切换到对应目录，用  ./程序名 ,运行或者写文件完整绝对路径运行
    - 添加命令查找路径 （环境变量）
        - 临时 export PATH="$HOME/mytools:$PATH"
        - 永久
            - 方法一
            ```bash
                vim ~/.bashrc
                # 添加内容 export PATH="$HOME/mytools:$PATH"
                source ~/.bashrc
                #重新加载
            ```
            - 方法二 （不建议）
             修改 `etc/environment ` 将程序（命令）所在目录写入PATH变量。
- `$SHELL` 系统的默认使用的shell路径
- `$0` 当前正在执行的脚本名称
- `$USER` 当前登录用户
- `$LANG` 系统语言编码

## 常用语法1
- `echo`
- `read`
    - 用法举例
    - `read name`
- `source`
- `export`
- 
- 
- 
## 常用语法2
- `shuf`
    - 用法举例
    - `shuf -i 1-10 -n 1`