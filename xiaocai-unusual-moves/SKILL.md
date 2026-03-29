---
name: xiaocai-unusual-moves
description: A股异动股分析工具。选出10个交易日内成交量翻倍且今天涨停的股票，按概念分组推送。
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

# 异动股分析 — 选出10个交易日内成交量翻倍且今天涨停的股票

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

1. **10个交易日内成交量翻倍**：10日前成交量 × 2 ≤ 当前成交量
2. **今日涨停**：pct_chg >= 9.9%
3. 排除ST股票
4. 股价 3-500元

## SQL查询

```sql
-- 变量: @trade_date = '2026-02-13', @date_10d_ago = '2026-02-03'
SELECT 
    s.stock_code,
    s.stock_name,
    s.close as current_close,
    ROUND(s.pct_chg, 2) as pct_chg,
    s.volume as current_vol,
    s10.volume as vol_10d_ago,
    ROUND(s.volume / s10.volume, 2) as vol_ratio,
    cs.concepts
FROM t_stock s
INNER JOIN (
    SELECT stock_code, volume
    FROM t_stock
    WHERE trade_date = @date_10d_ago
) s10 ON s.stock_code = s10.stock_code
LEFT JOIN (
    SELECT stock_code, GROUP_CONCAT(DISTINCT concept_name SEPARATOR ',') as concepts
    FROM t_concept_stock 
    GROUP BY stock_code
) cs ON s.stock_code = cs.stock_code
WHERE s.trade_date = @trade_date
  AND s.stock_name NOT LIKE 'ST%'
  AND s.stock_name NOT LIKE '*ST%'
  AND s.close > 3
  AND s.close < 500
  AND s.pct_chg >= 9.9
  AND s.volume >= s10.volume * 2
ORDER BY s.volume DESC;
```

## 输出格式

按概念分组展示：

### 📈 芯片概念 (X只)
| 代码 | 名称 | 收盘价 | 涨幅 | 成交量倍数 |
|:---|:---|:---:|:---:|:---:|
| 000001 | 某股票 | 10.50 | 10.02% | 2.35x |

### 📈 新能源概念 (X只)
...

## 注意事项

1. 成交量翻倍 = 当前成交量 >= 10日前成交量 × 2
2. 今日涨停 = 涨幅 >= 9.9%
3. 交易日期自动取数据库最新日期，自动跳过节假日
4. 按概念分组推送，每个概念下列出相关股票
5. 成交量单位需确认（手或元）
6. 放量涨停可能是资金短期炒作，注意追高风险
