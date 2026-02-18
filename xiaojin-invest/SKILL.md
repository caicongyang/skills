---
name: xiaojin-invest
description: 小金价值投资分析工具。基于基本面分析寻找15倍股（15-bagger）机会。支持多数据源股票扫描、定时监控、案例分析。适用于用户询问股票估值分析、投资机会筛选、基本面驱动选股等问题。
---

# 小金投资 - 基本面价值分析

## 核心理念

**15-bagger 特征**：
1. 基本面驱动（AI需求 → 业绩增长）
2. EPS 预测大幅上调（>50%）
3. 估值合理（P/E < 30）
4. 上涨空间 > 30%
5. 分析师强烈推荐

## 案例分析

- [SNDK 闪迪案例](references/case-studies.md) - 存储行业15-bagger
- [NVDA 英伟达案例](references/nvda-case.md) - AI芯片龙头对比

## API Key 配置（必需）

### 1. Financial Modeling Prep
- **官网**: https://site.financialmodelingprep.com/
- **免费额度**: 250次/天

### 2. Alpha Vantage
- **官网**: https://www.alphavantage.co/
- **免费额度**: 500次/天

### 3. Finnhub
- **官网**: https://finnhub.io/
- **免费额度**: 60次/分钟

### 配置方法
```bash
nano /root/.openclaw/workspace/skills/xiaojin-invest/config/keys.json
```

## 常用命令

```bash
# 扫描股票（需要先配置 API Key）
python3 /root/.openclaw/workspace/skills/xiaojin-invest/scripts/multi_source_scan.py
```

## 定时任务

- **工作日 9:00**: 板块监控（已设置）

## 参考资料

- [估值指标详解](references/metrics.md)
- [SNDK 案例](references/case-studies.md)
- [NVDA 案例](references/nvda-case.md)
