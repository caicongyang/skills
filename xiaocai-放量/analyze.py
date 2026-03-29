#!/usr/bin/env python3
"""
放量股分析：找出10个交易日内成交量翻倍且今日放量的股票
"""
import mysql.connector
import sys
import json
import os
from datetime import datetime, timedelta
from collections import defaultdict

# Get config path (support both skill directory and workspace)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATHS = [
    os.path.join(SCRIPT_DIR, "config", "database.json"),
    os.path.join(SCRIPT_DIR, "..", "..", "TOOLS.md")  # fallback to workspace
]

def load_db_config():
    """Load database config from JSON file"""
    for config_path in CONFIG_PATHS:
        if os.path.exists(config_path) and config_path.endswith(".json"):
            with open(config_path, "r") as f:
                return json.load(f)
    raise FileNotFoundError("database.json config file not found")

# Load config and connect
config = load_db_config()
db = mysql.connector.connect(
    host=config["host"],
    port=config["port"],
    user=config["user"],
    password=config["password"],
    database=config["database"]
)
cursor = db.cursor()

# Get the latest trading date (today)
cursor.execute("SELECT MAX(trade_date) FROM t_stock WHERE volume > 0")
latest_date = cursor.fetchone()[0]
print(f"最新交易日期: {latest_date}")

# Get trading dates for comparison
cursor.execute("""
    SELECT DISTINCT trade_date FROM t_stock 
    WHERE trade_date <= %s AND volume > 0 
    ORDER BY trade_date DESC 
    LIMIT 20
""", (latest_date,))
all_dates = [row[0] for row in cursor.fetchall()]

today = latest_date
yesterday = all_dates[1] if len(all_dates) > 1 else None
ten_days_ago = all_dates[9] if len(all_dates) > 9 else None

print(f"对比日期: 今日={today}, 昨日={yesterday}, 10日前={ten_days_ago}")

if not yesterday or not ten_days_ago:
    print("无法获取足够的交易日数据")
    sys.exit(1)

# Query volume data for all stocks
cursor.execute("""
    SELECT stock_code, trade_date, volume, close, pct_chg 
    FROM t_stock 
    WHERE trade_date IN (%s, %s, %s) AND volume > 0
    ORDER BY stock_code, trade_date
""", (today, yesterday, ten_days_ago))

data = {}
for row in cursor.fetchall():
    code, date, vol, close, pct = row
    if code not in data:
        data[code] = {'close': None, 'pct_chg': None, 'vol_today': None, 'vol_yesterday': None, 'vol_10d': None}
    if date == today:
        data[code]['vol_today'] = vol
        data[code]['close'] = close
        data[code]['pct_chg'] = pct
    elif date == yesterday:
        data[code]['vol_yesterday'] = vol
    elif date == ten_days_ago:
        data[code]['vol_10d'] = vol

# Filter stocks meeting criteria: volume >= 2x both 10 days ago AND today
results = []
for code, d in data.items():
    if d['vol_today'] and d['vol_yesterday'] and d['vol_10d']:
        ratio_today_vs_yesterday = d['vol_today'] / d['vol_yesterday']
        ratio_today_vs_10d = d['vol_today'] / d['vol_10d']
        # 10日内成交量翻倍: 今日/10日前 >= 2
        # 今日放量: 今日/昨日 >= 2
        if ratio_today_vs_10d >= 2 and ratio_today_vs_yesterday >= 2:
            results.append({
                'code': code,
                'close': d['close'],
                'pct_chg': d['pct_chg'],
                'ratio_today_yesterday': ratio_today_vs_yesterday,
                'ratio_today_10d': ratio_today_vs_10d
            })

# Sort by ratio_today_10d descending
results.sort(key=lambda x: x['ratio_today_10d'], reverse=True)

print(f"\n符合条件的股票数量: {len(results)}")

# Get stock names
codes = [r['code'] for r in results[:30]]  # Top 30 for name lookup
if codes:
    placeholders = ','.join(['%s'] * len(codes))
    cursor.execute(f"SELECT stock_code, MAX(stock_name) as stock_name FROM t_stock WHERE stock_code IN ({placeholders}) GROUP BY stock_code", codes)
    names = {row[0]: row[1] for row in cursor.fetchall()}
else:
    names = {}

# Get concepts for these stocks
top_codes = [r['code'] for r in results[:50]]
concept_map = defaultdict(list)
if top_codes:
    placeholders = ','.join(['%s'] * len(top_codes))
    cursor.execute(f"""
        SELECT s.stock_code, c.concept_name 
        FROM t_concept_stock s 
        JOIN t_concept c ON s.concept_code = c.concept_code 
        WHERE s.stock_code IN ({placeholders})
    """, top_codes)
    for stock_code, concept_name in cursor.fetchall():
        concept_map[stock_code].append(concept_name)

# Organize by concept
concept_stocks = defaultdict(list)
no_concept = []
for r in results[:50]:
    code = r['code']
    name = names.get(code, code)
    concepts = concept_map.get(code, [])
    r['name'] = name
    if concepts:
        for c in concepts:
            concept_stocks[c].append(r)
    else:
        no_concept.append(r)

# Remove duplicate stocks within concepts (keep first occurrence = highest ratio)
seen = set()
grouped = {}
for concept, stocks in sorted(concept_stocks.items(), key=lambda x: -len(x[1])):
    unique = []
    for s in stocks:
        if s['code'] not in seen:
            seen.add(s['code'])
            unique.append(s)
    if unique:
        grouped[concept] = unique[:5]  # Max 5 per concept

# Other/Uncategorized
if no_concept:
    grouped['其他'] = no_concept[:10]

# Print results
print("\n" + "="*60)
print(f"📊 放量股分析 {latest_date} (10日翻倍 + 今日放量)")
print("="*60)

total = 0
for concept, stocks in grouped.items():
    if concept == '其他' and total >= 15:
        continue
    print(f"\n### {concept} ({len(stocks)}只)")
    print("| 代码 | 名称 | 收盘价 | 涨幅 | 今日/昨日 | 今日/10日前 |")
    print("|:---|:---|:---:|:---:|:---:|:---:|")
    for s in stocks[:5]:
        pct_str = f"+{s['pct_chg']:.2f}%" if s['pct_chg'] >= 0 else f"{s['pct_chg']:.2f}%"
        print(f"| {s['code']} | {s['name']} | {s['close']:.2f} | {pct_str} | {s['ratio_today_yesterday']:.2f}x | {s['ratio_today_10d']:.2f}x |")
    total += len(stocks)

print("\n" + "="*60)
print(f"⚠️ 风险提示：放量可能是资金短期炒作，注意追高风险！")
print("="*60)

cursor.close()
db.close()
