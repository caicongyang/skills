---
name: xiaocai-high-volume
description: A股放量股分析工具。选出10个交易日内成交量翻倍且今日放量的股票，按概念板块分组展示。
metadata:
  {
    "openclaw":
      {
        "emoji": "📊",
        "requires":
          {
            "env":
              [
                "STOCK_DB_HOST",
                "STOCK_DB_PORT",
                "STOCK_DB_USER",
                "STOCK_DB_PASSWORD",
                "STOCK_DB_NAME",
              ],
          },
        "primaryEnv": "STOCK_DB_HOST",
      },
  }
---

# 10个交易日内成交量翻倍且今日翻倍 — 放量股分析

## 触发场景

用户询问以下问题时使用此 skill：
- "今天有哪些放量股"
- "放量股分析"
- "成交量翻倍的股票"
- "今日放量股票"
- "哪些股票今天放量了"

## 数据源

MySQL 数据库，通过环境变量配置连接信息。

关键表：
- `t_stock` — 股票日行情（含 volume 成交量字段）
- `t_concept_stock` — 概念板块成分股
- `t_concept` — 概念板块信息

## Setup

配置以下环境变量，三种方式任选（按优先级从高到低）：

**方式一：项目根目录 `.env` 文件（推荐）**

```bash
# .env
STOCK_DB_HOST=your_host
STOCK_DB_PORT=3306
STOCK_DB_USER=your_user
STOCK_DB_PASSWORD=your_password
STOCK_DB_NAME=stock
```

**方式二：全局 `~/.openclaw/.env`（适合多项目共用）**

```bash
# ~/.openclaw/.env
STOCK_DB_HOST=your_host
STOCK_DB_PORT=3306
STOCK_DB_USER=your_user
STOCK_DB_PASSWORD=your_password
STOCK_DB_NAME=stock
```

**方式三：Shell 环境变量**

```bash
export STOCK_DB_HOST="your_host"
export STOCK_DB_PORT="3306"
export STOCK_DB_USER="your_user"
export STOCK_DB_PASSWORD="your_password"
export STOCK_DB_NAME="stock"
```

确保已安装 Python 依赖：

```bash
pip3 install mysql-connector-python
```

## 执行

```bash
python3 skills/xiaocai-high-volume/analyze.py
```

## 筛选条件

两个条件同时满足才算放量股：

1. **今日成交量 ≥ 2倍昨日成交量** — 今日放量
2. **今日成交量 ≥ 2倍10日前成交量** — 10日内成交量翻倍

## 输出格式

按概念板块分组展示，每组最多5只：

### 📊 芯片概念 (X只)
| 代码 | 名称 | 收盘价 | 涨幅 | 今日/昨日 | 今日/10日前 |
|:---|:---|:---:|:---:|:---:|:---:|
| 000001 | 某股票 | 10.50 | +5.20% | 2.35x | 3.10x |

## 注意事项

1. 交易日期自动取数据库最新日期，无需手动指定
2. 10个交易日指实际交易日，已自动跳过节假日
3. 结果按今日/10日前成交量比率降序排列
4. 放量可能是资金短期炒作，注意追高风险
