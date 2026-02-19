---
name: xiaocai-异动
description: A股异动股分析工具。选出10个交易日内成交量翻倍且今天涨停的股票，按概念分组推送。
---

# 小菜异动股分析

## 触发场景

用户询问以下问题时使用此skill：
- "成交量翻倍股票"
- "放量涨停股票"
- "异动股推荐"
- "近期放量的涨停股票"
- "哪些股票最近成交量放大且涨停"

## 数据源

数据库配置见 `TOOLS.md` 中的 MySQL 配置。

关键表：
- `t_stock` - 股票日行情（含 volume 成交量字段）
- `t_concept_stock` - 概念板块成分股

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
3. 需要获取10个交易日前的日期（注意：可能需要往前找更多天以跳过节假日）
4. 按概念分组推送，每个概念下列出相关股票
5. 成交量单位需确认（手或元）
6. 强调风险：放量涨停可能是资金短期炒作，注意追高风险
