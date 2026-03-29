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

## 重要：必须执行 Python 脚本

**不要自行编写 SQL 或手动查询数据库。** 必须运行以下脚本，脚本已内置完整的筛选、去重、概念分组逻辑：

```bash
python3 skills/xiaocai-unusual-moves/analyze.py
```

直接将脚本输出原样返回给用户即可，不要修改输出格式。

## 触发场景

用户询问以下问题时使用此 skill：
- "成交量翻倍股票"
- "放量涨停股票"
- "异动股推荐"
- "近期放量的涨停股票"
- "哪些股票最近成交量放大且涨停"

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

## 筛选条件（脚本内置，无需手动实现）

1. **10个交易日内出现过成交量翻倍**：过去10个交易日中，任意相邻两天出现过成交量翻倍
2. **今日涨停**：pct_chg >= 9.9%
3. 排除ST股票，股价 3-500元
4. 每只股票只保留倍数最大的翻倍事件
5. 按概念板块分组输出，概念按包含股票数量降序排列
