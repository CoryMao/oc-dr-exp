# OpenClaw 科研 Agent 现场展示 — 最小可运行版本

## 功能

给定一篇 PDF 论文 + 一个研究课题，Agent 自动完成：

1. 阅读 PDF → 基于 citation-standard 生成结构化科研报告
2. 用 arxiv MCP + web_search 检索 5 篇补充论文
3. 调用 refchecker MCP 核查引用
4. 生成 REPAIRED_REPORT

## 一键流程

```bash
# 第一步：配置环境（只需一次）
bash demo/setup.sh

# 第二步：运行
bash demo/run.sh --pdf /path/to/paper.pdf --topic "你的研究课题"
```

## 参数

| 参数 | 必填 | 说明 |
|------|:---:|------|
| `--pdf` | ✅ | PDF 文件路径 |
| `--topic` | ✅ | 研究课题（中文或英文） |
| `--timeout` | | 超时秒数，默认 1800（30 分钟） |
| `--thinking` | | thinking level，默认 `high` |

## 示例

```bash
bash demo/run.sh \
  --pdf ~/Desktop/paper.pdf \
  --topic "大语言模型在软件工程任务中的工具增强效果" \
  --timeout 1200
```

## 输出

运行结束后，`demo/outputs/<timestamp>/` 目录下：

```
output.raw.txt    # Agent 完整输出（含四个部分）
  ├─ # ORIGINAL_REPORT
  ├─ # REFCHECKER_REPAIR_LOG
  ├─ # REPAIRED_REPORT
  └─ # RUN_SUMMARY
prompt.md         # 发送给 Agent 的完整 prompt
run.log           # 运行日志
stderr.log        # 错误日志
```

## 启用的工具

| 工具 | 用途 |
|------|------|
| `citation-standard` | 引用格式标准化 |
| `pdf` | 阅读 PDF 论文 |
| `arxiv-mcp` | arXiv 论文检索 |
| `refchecker` | 引用核查与修复 |
| `web_search` | 网络搜索；默认使用 Brave provider |
| deepseek-v4-pro | LLM 模型 |

## 禁用的功能

- **Memory**：关闭跨会话记忆（每次运行独立）

## 环境变量（可选）

`demo/run.sh` 会在检测到本机 `127.0.0.1:7897` 可用时自动设置代理。也可以手动覆盖：

```bash
export HTTPS_PROXY=http://127.0.0.1:7897
export HTTP_PROXY=http://127.0.0.1:7897
export NO_PROXY=api.deepseek.com,arxiv.org,export.arxiv.org,localhost,127.0.0.1
```

如有代理，在运行前 export 上述变量以确保 arxiv MCP 连接稳定，同时让 DeepSeek API 直连，避免本地代理 CONNECT 后超时。

默认 search provider 是 `brave`；`demo/setup.sh` 会优先复用本机已安装的 Brave plugin。若课堂网络下 Brave 不可用，可以临时回退到内置 DuckDuckGo：

```bash
OPENCLAW_DEMO_SEARCH_PROVIDER=duckduckgo bash demo/setup.sh
```

完整 PDF + 检索 + refchecker repair 通常需要较长时间；课堂演示建议使用默认 1800 秒或显式提高。仓库不再跟踪大型 demo PDF，请使用自己的 PDF，或使用 `case paper/` 下已经跟踪的测试论文：

```bash
bash demo/run.sh --pdf "case paper/case1/A Self-Improving Coding Agent.pdf" \
  --topic "大模型思维及其同质化" \
  --timeout 2400
```
