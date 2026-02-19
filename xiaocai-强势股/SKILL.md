---
name: xiaocai-强势股
description: A股强势股分析工具。基于超超大大单净流入(1日+5日)分析全市场最有可能继续上涨的股票。支持强烈推荐和激进型两种分类推荐。
---

# 小菜强势股分析

## 触发场景

用户询问以下问题时使用此skill：
- "分析全市场最有可能继续涨的股票"
- "帮我看看哪些股票会涨"
- "强势股推荐"
- "推荐股票"
- 任何关于A股股票分析、选股的问题

## 数据源

使用MySQL数据库：
- Host: 43.133.13.36
- Port: 3333
- Database: stock

关键表：
- `t_stock` - 股票日行情
- `t_stock_net_inflow` - 资金流向(超超大大单净流入)
- `t_concept_stock` - 概念板块成分股
- `t_stock_higher` - 涨停记录

## 分析因子

| 因子 | 权重 | 说明 |
|:---|:---:|:---|
| **超超大大单净流入(1日)** | 45% | 当日净流入(亿元)，反映今日主力资金动向 |
| **超超大大单净流入(5日)** | 55% | 5日累计净流入(亿元)，反映中长期主力资金态度 |

## 筛选条件

- 今日涨幅 > 0
- 股价 3-500元(排除ST和极端价格)
- 超超大大单5日净流入 > 0

## SQL查询

```sql
-- 变量: @trade_date = '2026-02-13'
SELECT 
    s.stock_code,
    s.stock_name,
    s.close,
    s.pct_chg,
    ROUND(n.super_super_net_1d_亿, 2) as super_super_1d_亿,
    ROUND(n.super_super_net_5d_亿, 2) as super_super_5d_亿,
    cs.main_concepts,
    ROUND(
        n.super_super_net_1d_亿 * 0.45 + 
        n.super_super_net_5d_亿 * 0.55
    , 2) as total_score
FROM t_stock s
LEFT JOIN (
    SELECT stock_code, 
        SUM(CASE WHEN trade_date = @trade_date THEN super_super_large_net_amount_1d ELSE 0 END)/100000000 as super_super_net_1d_亿,
        SUM(super_super_large_net_amount_5d)/100000000 as super_super_net_5d_亿
    FROM t_stock_net_inflow 
    WHERE trade_date >= DATE_SUB(@trade_date, INTERVAL 5 DAY)
    GROUP BY stock_code
) n ON s.stock_code = n.stock_code
LEFT JOIN (
    SELECT stock_code, GROUP_CONCAT(DISTINCT concept_name SEPARATOR ',') as main_concepts
    FROM t_concept_stock 
    GROUP BY stock_code
) cs ON s.stock_code = cs.stock_code
WHERE s.trade_date = @trade_date
  AND s.stock_name NOT LIKE 'ST%'
  AND s.stock_name NOT LIKE '*ST%'
  AND s.close > 3
  AND s.close < 500
  AND s.pct_chg > 0
  AND n.super_super_net_5d_亿 > 0
ORDER BY total_score DESC
LIMIT 20;
```

## 输出格式

### 强烈推荐 (资金持续流入、趋势稳健)

特征：超超大单净流入高(5日)、涨幅适中(0-5%)、趋势稳健

### 激进型 (涨幅猛、股性活跃)

特征：今日涨幅大(>5%甚至涨停)、股性活跃、波动大

每只股票给出：
- 代码、名称、收盘价、涨幅
- 超超大单1日净流入(亿)
- 超超大单5日净流入(亿)
- 核心概念
- 推荐逻辑(为什么看好)

## 注意事项

1. 超超大大单净流入字段：
   - `super_super_large_net_amount_1d` (1日当日)
   - `super_super_large_net_amount_5d` (5日累计)
2. 综合评分权重：1日净流入45% + 5日净流入55%
3. 今日日期用 @trade_date 变量或手动指定
4. 筛选条件：今日涨幅 > 0 (只选上涨股票)
5. 排除ST股票
6. 按照综合评分降序排列
