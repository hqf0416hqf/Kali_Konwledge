# Bug 排错：Codex TUI 启动超时——代理环境与共享后台

> 排查时间：2026-10-19 至 2026-10-20（Asia/Shanghai）。
> 整理时间：2026-10-20。
> 状态：指定 CLI 入口已恢复启动；采用代理配置与独立后台绕开原共享后台的网络问题。
> 证据来源：本次会话中的实际排查及本地报告。本文记录当次结果，本次整理没有重新进行网络或 TUI 测试。

## 1. 问题现象

### 1.1 预期与实际行为

预期：执行 `/home/kali/.local/bin/codex` 后完成账号初始化，进入终端交互界面（TUI）。

实际：程序已经启动，但在 TUI bootstrap（界面初始化）阶段退出：

```text
Error: account/read failed during TUI bootstrap: account/read failed:,
workspace routing discovery timed out (code -32603)
```

错误链从外到内为：界面初始化失败 → `account/read` 失败 → workspace routing discovery 超时。`-32603` 是 JSON-RPC 的内部错误码，不能单凭它确定网络、账号或版本中的哪一层出错。

### 1.2 当时的环境

| 项目 | 实际情况 |
|---|---|
| 系统 | Linux x86_64，用户目录 `/home/kali` |
| 入口 | `/home/kali/.local/bin/codex` |
| 安装方式 | standalone 独立安装 |
| 版本 | `codex-cli 0.163.0` |
| 原入口类型 | 符号链接，指向 `~/.codex/packages/standalone/current/bin/codex` |
| 身份认证 | `codex login status` 显示 ChatGPT 登录 |
| 本机代理 | `127.0.0.1:7897`；存在 Clash Verge / Mihomo 进程 |
| 后台 | 已有 0.163.0 的 managed app-server，默认 TUI 会复用它 |

`--version` 能运行，说明程序可以被启动；`login status` 显示已登录，只能作为本地认证状态证据。它们都不能替代在线账号请求与 TUI 初始化验收。

## 2. 排查思路

### 2.1 先定位失败阶段，再选择实验

错误已经发生在应用层账号初始化，因此优先检查安装身份、在线请求、代理和后台环境。采用控制变量法：尽量保持版本、账号、配置一致，只改变代理环境或后台连接方式。

| 步骤 | 为什么检查 | 实际观察 | 能得出的结论 |
|---|---|---|---|
| 核对入口、版本与登录状态 | 排除路径混淆，确定真正执行的程序 | 目标为 standalone 0.163.0；本地已登录 | 明确后续实验对象，尚不能判断联网是否成功 |
| 运行 `codex doctor` | 一次区分安装、配置与网络问题 | 安装一致、数据库健康；无代理变量；HTTP 不可达、WebSocket 超时 | 重点转向联网链路 |
| 比较直连与本机代理 | 检验代理是否改变可达性 | 沙箱外直连约 2.70 秒超时；代理能收到 HTTP 响应 | 故障不只由工具沙箱造成，代理路径值得继续验证 |
| 独立 app-server 发送 `account/read` | HTTP 首页响应不能证明账号业务成功 | 无代理 15.004 秒返回原错误；显式代理 1.437 秒返回成功 | 相同账号凭据可用，代理能消除独立进程的账号请求超时 |
| 仅给启动入口补代理 | 检查最小修复是否覆盖真实启动路径 | 默认 TUI 仍然报原错误 | 独立 RPC 成功不等于实际 TUI 已修复 |
| 检查实际后台进程 | 找出真正发起网络请求的进程 | 已有共享后台未设置 HTTP/HTTPS/ALL_PROXY；控制接口确认其运行中 | 前台新环境没有改变旧后台 |
| 用 `--no-daemon` 对照 | 让账号请求由继承代理的新后台处理 | 完成初始化，出现模型名、输入提示和 idle 状态 | 共享后台复用是第二个关键变量 |
| 最终入口重新启动 | 验证用户实际使用方式 | 不手动添加修复参数也可正常启动 | 默认入口修复有效 |

当时的网络对照命令如下。这里不携带认证信息，只用于检查连通性：

```bash
# 直连对照需要确保进程没有继承代理变量。
curl -sS -o /dev/null --connect-timeout 5 --max-time 10 \
  -w 'direct http=%{http_code} elapsed=%{time_total}\n' \
  https://chatgpt.com/

curl -sS -o /dev/null --proxy http://127.0.0.1:7897 \
  --connect-timeout 5 --max-time 10 \
  -w 'proxy http=%{http_code} elapsed=%{time_total}\n' \
  https://chatgpt.com/
```

注意：`http=000` 是 curl 没有获得 HTTP 状态码时的输出，不是服务器返回的 HTTP 状态。代理下出现 403/404，只说明能够收到对应服务器的 HTTP 响应，不能据此宣告账号可用。后续成功的 `account/read` 才是业务层证据。

### 2.2 涉及的知识体系

| 知识点 | 本次如何发挥作用 |
|---|---|
| Shell、PATH 与符号链接 | 命令名可能对应不同安装；绝对路径和真实链接目标用于固定实验对象 |
| 进程环境变量 | 新进程可以继承父进程传入的代理变量；已运行进程不会自动同步之后的 shell 环境修改 |
| 客户端与后台分离 | 终端显示界面的进程，可能只是通过本地 Socket 调用另一个后台进程 |
| TCP/TLS/HTTP 与业务接口 | 收到 HTTP 响应、认证成功、界面初始化完成，是不同层次的成功 |
| JSON-RPC | `account/read` 是请求方法，`-32603` 是错误分类；还要结合 message 定位具体失败 |
| 对照实验 | 同账号、同版本下只改代理，再只改后台模式，逐步缩小原因范围 |

关键调用关系可以表示为：

```text
只修前台代理：
Shell（有代理）→ 新 TUI → 既存共享后台（无代理）→ 路由发现超时

本次最终修复：
启动包装器（补代理）→ TUI --no-daemon → 新独立后台（继承代理）
                                           ↓
                                  127.0.0.1:7897 → 在线接口
```

### 2.3 排查工具自身也可能出错

独立 RPC 测试曾出现一次 45 秒的“测试器超时”。原因是诊断脚本混用了文本流缓冲和 `select`：数据可能已进入 Python 的用户态缓冲区，但底层文件描述符不再显示可读。

改为 `os.read` 配合显式行缓冲后，得到 1.437 秒的成功结果。因此，45 秒结果没有被计入 Codex 超时证据。这也是为什么不能把所有探针超时都直接归因于被测程序。

## 3. 最终确定问题

### 3.1 现象、直接原因与根因

- **现象：** TUI 在 bootstrap 阶段退出，显示 `account/read failed`。
- **直接原因：** 账号读取依赖的 workspace routing discovery 在约 15 秒内未完成，后台返回 `-32603`。
- **已验证的环境原因之一：** 测试环境直连 ChatGPT 超时，本机代理路径可完成同一账号请求；无代理的独立进程能复现原错误。
- **已验证的环境原因之二：** 默认 TUI 复用无代理配置的既存共享后台。前台补代理没有更新旧后台环境，独立后台模式则成功。

这两层原因解释了“为什么独立账号测试成功，默认 TUI 仍然失败”。

### 3.2 结论边界

本次没有通过抓包或逐跳分析确定底层连接阻断位置，不能进一步断言是某个 ISP、DNS、防火墙或远端服务造成的。也没有做相同条件下的多版本回归测试，不能认定为 0.163.0 的版本回归。

相同凭据在代理路径成功，说明本次故障无需通过重新登录才能解决；这不是对所有账号错误的通用判断。

## 4. 解决方案

### 4.1 已落地的修改

将 `/home/kali/.local/bin/codex` 从符号链接替换为 shell 包装器，仍执行原来的 `standalone/current/bin/codex`。包装器只为本次 Codex 启动及其继承环境的进程补充代理，并默认使用 `--no-daemon`。

以下为修复时保存的实际脚本：

```sh
#!/bin/sh
# Codex-only proxy defaults, verified on 2026-10-20.
# Keep caller-provided proxy configuration. Set CODEX_DIRECT=1 to opt out.
if [ "${CODEX_DIRECT:-0}" != "1" ] &&
   [ -z "${HTTPS_PROXY:-}${https_proxy:-}${ALL_PROXY:-}${all_proxy:-}${HTTP_PROXY:-}${http_proxy:-}" ]; then
    export HTTPS_PROXY="http://127.0.0.1:7897"
    export HTTP_PROXY="$HTTPS_PROXY"
    if [ -z "${NO_PROXY:-}${no_proxy:-}" ]; then
        export NO_PROXY="localhost,127.0.0.1,::1"
    fi
fi
# Existing shared daemons keep their original environment. Use a fresh local
# backend so the proxy above applies without restarting other active sessions.
# Opt in to a separately repaired shared daemon with CODEX_USE_SHARED_DAEMON=1.
if [ "${CODEX_USE_SHARED_DAEMON:-0}" != "1" ]; then
    set -- --no-daemon "$@"
fi
exec /home/kali/.codex/packages/standalone/current/bin/codex "$@"
```

这些语句分别解决什么问题：

- 检查已有代理变量：优先尊重调用方配置；已有代理配置的正确性仍由调用方保证。
- `NO_PROXY`：让 localhost、127.0.0.1、::1 的本地通信绕过代理。
- `set -- --no-daemon "$@"`：加入独立后台参数，同时保留原参数边界。
- `exec`：让 shell 被实际 Codex 程序替换，避免额外保留一层等待进程。
- 调用 `current/bin/codex`：跟随安装目录的 current 指针，不把 0.163.0 的具体版本目录写死在包装器中。

正常使用：

```bash
/home/kali/.local/bin/codex
```

### 4.2 行为变化和维护条件

**这是指定入口的有效修复，同时也是对原共享后台问题的绕开。原共享后台本身没有修复或重启。** 当前 TUI 默认使用独立后台，不再按原默认行为复用共享后台；这样无需中断可能正在使用旧后台的其他会话。

| 条件或选项 | 含义 |
|---|---|
| 本机代理监听 7897 | 默认代理路径工作的前提；端口改变时需要同步配置 |
| `CODEX_DIRECT=1` | 不自动补代理；不会清除调用方已有的代理变量 |
| `CODEX_USE_SHARED_DAEMON=1` | 不自动增加 `--no-daemon`；仅应在共享后台环境另行修复后使用 |
| 升级或重装 | current 指针可跟随新版本，但安装器可能重建入口并覆盖包装器；这一行为没有实测 |

另一种可能方案是在确保现有任务可安全停止后，让共享后台带正确代理重新启动。本次没有采用或验证此方案，因此不能把旧后台记为“已修复”。

### 4.3 回滚资料

原入口备份、包装器快照、哈希记录及回滚脚本位于：

```text
/home/kali/codex-routing-report-20261020-012945/
├── report.md
├── codex.original-symlink
├── codex.wrapper.sh
├── change.json
└── rollback.py
```

只读检查命令，已在修复时执行通过：

```bash
python3 /home/kali/codex-routing-report-20261020-012945/rollback.py --check
```

仅在明确需要撤销本次修复时执行；本次未执行恢复：

```bash
python3 /home/kali/codex-routing-report-20261020-012945/rollback.py --apply
```

脚本核对入口 SHA-256，仅在入口仍为本次包装器时恢复原符号链接，避免覆盖后续修改。回滚并不会解决原来的网络问题。

## 5. 验证结果

### 5.1 修复时已完成的验收

| 项目 | 结果 |
|---|---|
| 包装器 `sh -n` | 语法检查通过 |
| 包装器调用 `--version` | 正常返回 `codex-cli 0.163.0` |
| 独立账号请求 | 代理条件下 `account/read` 成功，1.437 秒 |
| 最终默认入口启动 | 未手动添加代理或 `--no-daemon`，完成 TUI 初始化 |
| 运行状态 | 显示 GPT-6-Astra high、输入提示及 idle 状态 |
| 退出 | 测试会话通过 Ctrl+C 正常退出，退出码 0 |
| HTTP / WebSocket | HTTP 可达；WebSocket 返回 101 Switching Protocols |
| 回滚校验 | 只读哈希校验通过，未执行回滚 |

实际 TUI 验收命令：

```bash
env TERM=xterm-256color /home/kali/.local/bin/codex --no-alt-screen
```

这里的 `--no-alt-screen` 用于保留终端输出；代理与独立后台参数由包装器提供。单独出现 loading 或初始输入框不算验收完成，本次继续观察到了完整初始化后的模型状态和 idle 状态。

最终诊断摘要：

```text
[ok] install      consistent
[ok] auth         auth is configured
[ok] websocket    connected (HTTP 101 Switching Protocols)
[ok] reachability active provider endpoints are reachable over HTTP
18 ok | 4 notes | 3 warn | 0 fail degraded
```

### 5.2 尚存提示与未验证范围

- `disable_response_storage` 不被 0.163.0 识别，TUI 明确提示该配置被忽略。
- doctor 提示历史线程的索引/rollout 清单不一致，以及非交互检查的 `TERM=dumb` 等事项。
- “0 fail”不代表所有警告已清除；上述事项不属于本次启动超时修复范围。
- 已验证启动、退出及独立进程重新运行；没有重启操作系统验证。
- 未提交模型问答，未验证推理响应、全部 MCP 功能或全部后台管理子命令。
- 本文是排查记录和知识整理，不代表相关知识已经由用户独立练习并掌握。

## 6. 总结

### 6.1 可以迁移的排错方法

1. **固定实验对象。** 先明确执行入口、真实二进制和版本，再比较结果，避免把 PATH 或安装差异误判成软件回归。
2. **按层验证成功。** 本地已登录、网络有响应、业务接口成功、完整启动成功，是四种不同证据。
3. **关注真正处理请求的进程。** 代理设置在前台，不代表共享后台能看到；客户端与后台分离时，要检查后者的环境。
4. **一次只改变关键变量。** 先比较直连与代理，再比较共享与独立后台，才能解释每个结果。
5. **对探针保持怀疑。** 诊断脚本的超时也可能来自缓冲、协议或读取方式，而不是应用服务。
6. **报告修复边界。** 记录绕开了什么、实际改了什么、还有什么没测，并保留可校验的回滚路径。

### 6.2 类似问题的快速定位顺序

```text
确认入口与版本
    ↓
判断失败发生在本地初始化、联网还是业务处理
    ↓
诊断与直连/代理对照
    ↓
用同一业务接口验证，而非只检查首页
    ↓
检查真正处理请求的后台及其环境
    ↓
最小修改 → 实际启动验收 → 记录剩余问题与回滚方法
```

最值得记住的结论是：**环境变量是进程启动时传入的配置，不是自动同步到所有程序的全局开关。** 对共享后台架构，修复新启动的前台环境可能只完成了一半工作。

### 6.3 来源与延伸阅读

- 本次会话：2026-10-19 至 2026-10-20 的实测命令输出、修复与 TUI 验收。
- 原始本地报告：`/home/kali/codex-routing-report-20261020-012945/report.md`；属于本机取证资料，不随知识库自动迁移。
- [Codex App Server 官方文档](https://learn.chatgpt.com/docs/app-server)：用于确认 `account/read` 接口及认证语义；根因来自本机实验。
- [Codex Authentication 官方文档](https://learn.chatgpt.com/docs/auth)：认证方式与本地认证资料说明。
- 本机 0.163.0 的 `codex --help`：确认 `--no-daemon` 表示不使用共享后台，即使后台已运行。
- [Linux CLI 与网络故障排查：从零建立思路](../tools/Linux/Linux_CLI与网络故障排查_从零建立思路_含Codex案例.md)：相关基础知识与扩展学习；本次故障的最终事实边界以本文验证记录为准。
