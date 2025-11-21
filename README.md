# FunctionFinance (Ei Agent) 💸

[English](#english) | [中文](#chinese)

<a name="english"></a>

FunctionFinance is an intelligent financial analysis Agent based on Large Language Models (LLM), codenamed "Ei". It aims to provide users with in-depth financial analysis, trend forecasting, and investment advice by combining quantitative financial data with qualitative market information.

## ✨ Core Features

Ei Agent possesses the following core capabilities:

*   **📈 Trend Forecast**:
    *   Multi-dimensional prediction of stock price trends combining technical analysis indicators and behavioral finance models.
*   **📊 Report Analysis**:
    *   Automatically generates in-depth analysis reports on macroeconomics, specific industries, or individual stocks.
    *   Supports automatic task orchestration for comprehensive market scanning.
*   **📰 Data Acquisition**:
    *   Real-time acquisition of the latest financial news and market dynamics.
    *   Queries historical financial data (e.g., stock prices, P/E ratios, financial report data).
*   **🧠 Stock Selection**:
    *   Investment portfolio optimization suggestions based on a multi-expert debate mechanism.
    *   Simulates decision-making by experts with different investment styles.
*   **💾 Long-term Memory**:
    *   Uses FAISS vector database to store user profiles and historical conversations, providing a personalized service experience.

## 🛠️ Tech Stack

This project is built on the following technology stack:

*   **Core Framework**: [LangChain](https://github.com/langchain-ai/langchain), [LangGraph](https://github.com/langchain-ai/langgraph)
*   **LLM**: OpenAI GPT-4o, GPT-3.5 (Supports extension to Claude, Llama 3, etc., via configuration)
*   **Vector Database**: FAISS
*   **Data Collection**: Self-developed crawler system (targeting Chinese financial sources like Eastmoney)

## 🚀 Quick Start

### 1. Clone the Project

```bash
git clone https://github.com/yourusername/FunctionFinance.git
cd FunctionFinance
```

### 2. Install Dependencies

Python 3.9+ environment is recommended.

```bash
pip install -r requirements.txt
```
*(Note: If there is no requirements.txt in the project, please manually install dependencies based on code imports, such as `langchain`, `langchain-openai`, `langgraph`, `faiss-cpu`, `colorama`, etc.)*

### 3. Configure API Key

This project relies on APIs from multiple AI services. For security, **do not directly modify `config.ini`**.

1.  Copy the example configuration file:
    ```bash
    cp config.ini.example config.ini
    ```
2.  Edit `config.ini` and fill in your API Key:
    ```ini
    [OPENAI]
    API_KEY = sk-xxxxxx
    ...
    ```

### 4. Run the Agent

```bash
python app.py
```

After startup, enter your username in the command line to start conversing with Ei.

## 📂 Project Structure

*   `app.py`: Program entry point, defining Agent workflow and tools.
*   `scheduler/`: Core scheduling logic, containing specific implementations of each Tool.
*   `crawler/`: Financial data crawler module.
*   `config.ini`: Configuration file (Do not upload).
*   `data_connection/`: Data storage path.

## ⚠️ Disclaimer

*   This project is for learning and research purposes only and does not constitute any investment advice.
*   Please keep your API Keys safe and do not upload them to public code repositories.

## 📝 License

[MIT](LICENSE)

---

<a name="chinese"></a>

## 中文介绍

FunctionFinance 是一个基于大语言模型 (LLM) 的智能金融分析 Agent，代号 "Ei"。它旨在通过结合定量财务数据和定性市场信息，为用户提供深度的金融分析、趋势预测和投资建议。

## ✨ 核心功能

Ei Agent 具备以下核心能力：

*   **📈 趋势预测 (Trend Forecast)**: 
    *   结合技术分析指标和行为金融学模型，对股票价格趋势进行多维度预测。
*   **📊 研报分析 (Report Analysis)**: 
    *   自动生成宏观经济、特定行业或个股的深度分析报告。
    *   支持自动编排任务，进行全方位的市场扫描。
*   **📰 数据获取 (Data Acquisition)**: 
    *   实时获取最新的财经新闻、市场动态。
    *   查询历史财务数据（如股价、市盈率、财报数据）。
*   **🧠 智能选股 (Stock Selection)**: 
    *   基于多专家辩论机制 (Debate) 的投资组合优化建议。
    *   模拟不同投资风格的专家进行决策。
*   **💾 长期记忆 (Long-term Memory)**: 
    *   利用 FAISS 向量数据库存储用户画像和历史对话，提供个性化的服务体验。

## 🛠️ 技术架构

本项目基于以下技术栈构建：

*   **核心框架**: [LangChain](https://github.com/langchain-ai/langchain), [LangGraph](https://github.com/langchain-ai/langgraph)
*   **大语言模型**: OpenAI GPT-4o, GPT-3.5 (支持通过配置扩展至 Claude, Llama 3 等)
*   **向量数据库**: FAISS
*   **数据采集**: 自研爬虫系统 (针对东方财富等中文财经源)

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/yourusername/FunctionFinance.git
cd FunctionFinance
```

### 2. 安装依赖

建议使用 Python 3.9+ 环境。

```bash
pip install -r requirements.txt
```
*(注意：如果项目中没有 requirements.txt，请根据代码 import 手动安装依赖，如 `langchain`, `langchain-openai`, `langgraph`, `faiss-cpu`, `colorama` 等)*

### 3. 配置 API Key

本项目依赖多个 AI 服务的 API。为了安全起见，**不要直接修改 `config.ini`**。

1.  复制示例配置文件：
    ```bash
    cp config.ini.example config.ini
    ```
2.  编辑 `config.ini`，填入你的 API Key：
    ```ini
    [OPENAI]
    API_KEY = sk-xxxxxx
    ...
    ```

### 4. 运行 Agent

```bash
python app.py
```

启动后，在命令行输入你的用户名，即可开始与 Ei 进行对话。

## 📂 项目结构

*   `app.py`: 程序入口，定义 Agent 工作流和工具。
*   `scheduler/`: 核心调度逻辑，包含各个 Tool 的具体实现。
*   `crawler/`: 金融数据爬虫模块。
*   `config.ini`: 配置文件 (请勿上传)。
*   `data_connection/`: 数据存储路径。

## ⚠️ 注意事项

*   本项目仅供学习和研究使用，不构成任何投资建议。
*   请妥善保管您的 API Key，不要将其上传到公共代码库。

## 📝 License

[MIT](LICENSE)
