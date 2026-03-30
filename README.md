# FunctionFinance (Ei Agent)

[English](#english) | [中文](#chinese)

<a name="english"></a>

FunctionFinance is a financial analysis agent built on large language models (LLM), codenamed "Ei". It wires together quantitative data (prices, ratios, filings) and text sources (news, posts) for queries, summaries, and scripted workflows—not a substitute for professional advice.

## Core features

*   **Trend forecast**: Price-direction style outputs using technical-style inputs and simple behavioral-finance framing where implemented.
*   **Report-style analysis**: Chains that produce macro / sector / single-name writeups from retrieved data; task graphs can chain multiple tools.
*   **Data acquisition**: Crawlers and connectors for Chinese financial sites (e.g. Eastmoney-class sources), plus historical series where available.
*   **Stock selection**: Portfolio-style suggestions driven by multi-role or debate-style prompts over the same data layer.
*   **Long-term memory**: FAISS-backed storage for user-related embeddings and past turns so follow-up questions can reuse context.

## Tech stack

*   **Orchestration**: [LangChain](https://github.com/langchain-ai/langchain), [LangGraph](https://github.com/langchain-ai/langgraph)
*   **LLM**: OpenAI GPT-4o / GPT-3.5 by default; other providers (e.g. Claude, Llama) via config if you wire them in.
*   **Vectors**: FAISS
*   **Data**: In-repo crawlers and parsers aimed at Chinese market sources.

## Quick start

### 1. Clone the project

```bash
git clone https://github.com/yourusername/FunctionFinance.git
cd FunctionFinance
```

### 2. Install dependencies

Python 3.9+ is recommended.

```bash
pip install -r requirements.txt
```

If `requirements.txt` is missing or incomplete, install from imports (e.g. `langchain`, `langchain-openai`, `langgraph`, `faiss-cpu`, `colorama`).

### 3. Configure API keys

Do not commit real secrets. If the repo ships `config.ini.example`, copy it; otherwise create `config.ini` in the project root:

```bash
cp config.ini.example config.ini   # when the example file exists
```

```ini
[OPENAI]
API_KEY = sk-xxxxxx
...
```

### 4. Run the agent

```bash
python app.py
```

Enter a username at the prompt to start a session.

## Project layout

*   `app.py`: Entry point; agent graph and tool registration.
*   `scheduler/`: Tool implementations and scheduling.
*   `crawler/`: Scrapers and fetch helpers.
*   `config.ini`: Local secrets (gitignored in normal setups).
*   `data_connection/`: Data paths and glue scripts.

## Disclaimer

*   For learning and research only; not investment advice.
*   Keep API keys out of public repos.

## License

[MIT](LICENSE)

---

<a name="chinese"></a>

## 中文介绍

FunctionFinance 是基于大语言模型 (LLM) 的金融分析 Agent，代号 Ei。项目把行情/财报等结构化数据和新闻、帖子等文本源接进同一套工具链，用于查询、摘要和可编排的任务流程；输出需自行核验，不能当作投资建议。

## 核心功能

*   **趋势预测**：在已有指标与简单行为金融表述上，生成方向性/解释性输出（实现以代码为准）。
*   **研报类分析**：通过 LangChain/LangGraph 等链接工具，生成宏观、行业或个股类文字稿；支持多步任务编排。
*   **数据获取**：自研爬虫与连接器，面向东方财富等中文财经源，并可在部分模块中拉取历史序列数据。
*   **选股 / 组合建议**：用多角色或辩论式提示在同一数据层上给出组合向建议，属于实验性能力。
*   **长期记忆**：使用 FAISS 存向量化的用户相关片段与历史对话，便于多轮追问沿用上下文。

## 技术架构

*   **编排**: [LangChain](https://github.com/langchain-ai/langchain), [LangGraph](https://github.com/langchain-ai/langgraph)
*   **模型**: 默认 OpenAI GPT-4o / GPT-3.5；可按配置接入 Claude、Llama 等（需自行对接）。
*   **向量库**: FAISS
*   **数据**: 仓库内爬虫与解析，主要面向 A 股/中文财经站点。

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/yourusername/FunctionFinance.git
cd FunctionFinance
```

### 2. 安装依赖

建议使用 Python 3.9+。

```bash
pip install -r requirements.txt
```

若缺少 `requirements.txt` 或依赖不全，请根据代码中的 `import` 手动安装，例如 `langchain`、`langchain-openai`、`langgraph`、`faiss-cpu`、`colorama` 等。

### 3. 配置 API Key

勿把真实密钥提交到仓库。若仓库提供 `config.ini.example` 可复制为 `config.ini`，否则在项目根新建 `config.ini`：

```bash
cp config.ini.example config.ini   # 存在示例文件时
```

```ini
[OPENAI]
API_KEY = sk-xxxxxx
...
```

### 4. 运行 Agent

```bash
python app.py
```

启动后在命令行输入用户名即可开始会话。

## 项目结构

*   `app.py`: 入口；Agent 图与工具注册。
*   `scheduler/`: 调度与各 Tool 实现。
*   `crawler/`: 爬虫与抓取相关代码。
*   `config.ini`: 本地配置（通常应被 git 忽略）。
*   `data_connection/`: 数据路径与连接脚本。

## 注意事项

*   仅供学习与研究，不构成投资建议。
*   妥善保管 API Key，勿上传到公共代码库。

## License

[MIT](LICENSE)
