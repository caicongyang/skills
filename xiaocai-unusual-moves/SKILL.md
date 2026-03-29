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

## 筛选条件

两个条件同时满足：

1. **10个交易日内出现过成交量翻倍**：过去10个交易日中，任意相邻两天出现过成交量翻倍（day-over-day doubling）
2. **今日涨停**：pct_chg >= 9.9%
3. 排除ST股票
4. 股价 3-500元

## SQL查询

分两步执行：

**Step 1：获取近11个交易日（多取1天用于相邻比较）**

```sql
SELECT DISTINCT trade_date FROM t_stock
WHERE volume > 0
ORDER BY trade_date DESC
LIMIT 11;
-- 结果存为 @dates 列表，@trade_date = 最新日期
```

**Step 2：找出10日内有相邻成交量翻倍 + 今日涨停的股票**

```sql
SELECT 
    today.stock_code,
    today.stock_name,
    today.close,
    ROUND(today.pct_chg, 2) as pct_chg,
    doubles.double_date,
    doubles.vol_ratio,
    cs.concepts
FROM t_stock today
INNER JOIN (
    -- 10个交易日内，任意相邻两天成交量翻倍
    SELECT curr.stock_code,
           curr.trade_date as double_date,
           ROUND(curr.volume / prev.volume, 2) as vol_ratio
    FROM t_stock curr
    INNER JOIN t_stock prev 
        ON curr.stock_code = prev.stock_code
    WHERE curr.trade_date IN (@dates)
      AND prev.trade_date IN (@dates)
      -- prev 是 curr 的前一个交易日
      AND prev.trade_date = (
          SELECT MAX(t.trade_date) FROM t_stock t
          WHERE t.stock_code = curr.stock_code
            AND t.trade_date < curr.trade_date
            AND t.trade_date IN (@dates)
            AND t.volume > 0
      )
      AND curr.volume >= prev.volume * 2
      AND curr.volume > 0 AND prev.volume > 0
) doubles ON today.stock_code = doubles.stock_code
LEFT JOIN (
    SELECT stock_code, GROUP_CONCAT(DISTINCT concept_name SEPARATOR ',') as concepts
    FROM t_concept_stock 
    GROUP BY stock_code
) cs ON today.stock_code = cs.stock_code
WHERE today.trade_date = @trade_date
  AND today.stock_name NOT LIKE 'ST%'
  AND today.stock_name NOT LIKE '*ST%'
  AND today.close > 3
  AND today.close < 500
  AND today.pct_chg >= 9.9
ORDER BY doubles.vol_ratio DESC;
```

## 输出格式

标题：`📈 异动股分析 {日期} — 10个交易日内出现过成交量翻倍且今天涨停`

按概念分组展示：

### 📈 芯片概念 (X只)
| 代码 | 名称 | 收盘价 | 涨幅 | 翻倍日期 | 成交量倍数 |
|:---|:---|:---:|:---:|:---:|:---:|
| 000001 | 某股票 | 10.50 | 10.02% | 2026-03-25 | 2.35x |

### 📈 新能源概念 (X只)
...

## 注意事项

1. 成交量翻倍 = 过去10个交易日内任意相邻两天，后一天成交量 >= 前一天 × 2
2. 今日涨停 = 涨幅 >= 9.9%
3. 交易日期自动取数据库最新日期，自动跳过节假日
4. 按概念分组推送，每个概念下列出相关股票
5. 输出中展示具体哪天发生了成交量翻倍及倍数
6. 放量涨停可能是资金短期炒作，注意追高风险
