---
name: xiaocai-unusual-moves
description: A股异动股分析工具。选出10个交易日内出现过相邻两天成交量翻倍且今天涨停的股票，按概念分组推送。
metadata:
  {
    "openclaw":
      {
        "emoji": "📈",
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

# 异动股分析 — 选出10个交易日内出现过成交量翻倍且今天涨停的股票

## 触发场景

用户询问以下问题时使用此 skill：
- "成交量翻倍股票"
- "放量涨停股票"
- "异动股推荐"
- "近期放量的涨停股票"
- "哪些股票最近成交量放大且涨停"

## 数据源

MySQL 数据库，通过环境变量配置连接信息。

关键表：
- `t_stock` — 股票日行情（含 volume 成交量字段）
- `t_concept_stock` — 概念板块成分股

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

## 执行

```bash
python3 skills/xiaocai-unusual-moves/analyze.py
```

脚本自动完成：筛选 → 去重 → 概念分组 → 格式化输出。

## 筛选条件

两个条件同时满足：

1. **10个交易日内出现过成交量翻倍**：过去10个交易日中，任意相邻两天出现过成交量翻倍（day-over-day doubling）
2. **今日涨停**：pct_chg >= 9.9%
3. 排除ST股票
4. 股价 3-500元

## 输出格式

标题：`📈 异动股分析 {日期} — 10个交易日内出现过成交量翻倍且今天涨停`

按概念板块分组展示，每组最多5只，每只股票只出现一次：

### 📈 芯片概念 (3只)
| 代码 | 名称 | 收盘价 | 涨幅 | 翻倍日期 | 成交量倍数 |
|:---|:---|:---:|:---:|:---:|:---:|
| 000001 | 某股票 | 10.50 | +10.02% | 2026-03-25 | 2.35x |

### 📈 新能源概念 (2只)
| 代码 | 名称 | 收盘价 | 涨幅 | 翻倍日期 | 成交量倍数 |
|:---|:---|:---:|:---:|:---:|:---:|
| 000002 | 某股票 | 8.30 | +9.95% | 2026-03-24 | 3.10x |

## 注意事项

1. 成交量翻倍 = 过去10个交易日内任意相邻两天，后一天成交量 >= 前一天 × 2
2. 每只股票只保留倍数最大的那次翻倍事件，避免重复
3. 今日涨停 = 涨幅 >= 9.9%
4. 交易日期自动取数据库最新日期，自动跳过节假日
5. 按概念分组输出，概念按包含股票数量降序排列
6. 放量涨停可能是资金短期炒作，注意追高风险
