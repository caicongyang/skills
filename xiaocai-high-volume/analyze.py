#!/usr/bin/env python3
"""
放量股分析：找出10个交易日内成交量翻倍且今日放量的股票
"""
import mysql.connector
import sys
import os
from collections import defaultdict

VOLUME_RATIO_THRESHOLD = 2
MAX_STOCKS_PER_CONCEPT = 5
MAX_TOTAL_DISPLAY = 50


def get_db_config():
    """从环境变量读取数据库配置，缺失时给出明确提示"""
    required = {
        "STOCK_DB_HOST": "host",
        "STOCK_DB_PORT": "port",
        "STOCK_DB_USER": "user",
        "STOCK_DB_PASSWORD": "password",
        "STOCK_DB_NAME": "database",
    }
    config = {}
    missing = []
    for env_key, config_key in required.items():
        val = os.environ.get(env_key)
        if not val:
            missing.append(env_key)
        else:
            config[config_key] = int(val) if config_key == "port" else val

    if missing:
        print(f"错误：缺少环境变量 {', '.join(missing)}")
        print("请配置后重试，例如：")
        print('  export STOCK_DB_HOST="your_host"')
        print('  export STOCK_DB_PORT="3306"')
        print('  export STOCK_DB_USER="your_user"')
        print('  export STOCK_DB_PASSWORD="your_password"')
        print('  export STOCK_DB_NAME="stock"')
        sys.exit(1)

    return config


def get_trading_dates(cursor, latest_date, count=20):
    cursor.execute("""
        SELECT DISTINCT trade_date FROM t_stock 
        WHERE trade_date <= %s AND volume > 0 
        ORDER BY trade_date DESC 
        LIMIT %s
    """, (latest_date, count))
    return [row[0] for row in cursor.fetchall()]


def fetch_volume_data(cursor, today, yesterday, ten_days_ago):
    cursor.execute("""
        SELECT stock_code, trade_date, volume, close, pct_chg 
        FROM t_stock 
        WHERE trade_date IN (%s, %s, %s) AND volume > 0
        ORDER BY stock_code, trade_date
    """, (today, yesterday, ten_days_ago))

    data = {}
    for code, date, vol, close, pct in cursor.fetchall():
        if code not in data:
            data[code] = {
                "close": None, "pct_chg": None,
                "vol_today": None, "vol_yesterday": None, "vol_10d": None,
            }
        if date == today:
            data[code].update(vol_today=vol, close=close, pct_chg=pct)
        elif date == yesterday:
            data[code]["vol_yesterday"] = vol
        elif date == ten_days_ago:
            data[code]["vol_10d"] = vol

    return data


def filter_volume_stocks(data, threshold=VOLUME_RATIO_THRESHOLD):
    results = []
    for code, d in data.items():
        if not all([d["vol_today"], d["vol_yesterday"], d["vol_10d"]]):
            continue
        ratio_vs_yesterday = d["vol_today"] / d["vol_yesterday"]
        ratio_vs_10d = d["vol_today"] / d["vol_10d"]
        if ratio_vs_10d >= threshold and ratio_vs_yesterday >= threshold:
            results.append({
                "code": code,
                "close": d["close"],
                "pct_chg": d["pct_chg"],
                "ratio_today_yesterday": ratio_vs_yesterday,
                "ratio_today_10d": ratio_vs_10d,
            })

    results.sort(key=lambda x: x["ratio_today_10d"], reverse=True)
    return results


def fetch_stock_names(cursor, codes):
    if not codes:
        return {}
    placeholders = ",".join(["%s"] * len(codes))
    cursor.execute(
        f"SELECT stock_code, MAX(stock_name) as stock_name "
        f"FROM t_stock WHERE stock_code IN ({placeholders}) GROUP BY stock_code",
        codes,
    )
    return {row[0]: row[1] for row in cursor.fetchall()}


def fetch_concept_map(cursor, codes):
    if not codes:
        return {}
    placeholders = ",".join(["%s"] * len(codes))
    cursor.execute(f"""
        SELECT s.stock_code, c.concept_name 
        FROM t_concept_stock s 
        JOIN t_concept c ON s.concept_code = c.concept_code 
        WHERE s.stock_code IN ({placeholders})
    """, codes)

    concept_map = defaultdict(list)
    for stock_code, concept_name in cursor.fetchall():
        concept_map[stock_code].append(concept_name)
    return concept_map


def group_by_concept(results, concept_map, names, max_per_concept=MAX_STOCKS_PER_CONCEPT):
    concept_stocks = defaultdict(list)
    no_concept = []

    for r in results:
        r["name"] = names.get(r["code"], r["code"])
        concepts = concept_map.get(r["code"], [])
        if concepts:
            for c in concepts:
                concept_stocks[c].append(r)
        else:
            no_concept.append(r)

    seen = set()
    grouped = {}
    for concept, stocks in sorted(concept_stocks.items(), key=lambda x: -len(x[1])):
        unique = [s for s in stocks if s["code"] not in seen]
        for s in unique:
            seen.add(s["code"])
        if unique:
            grouped[concept] = unique[:max_per_concept]

    if no_concept:
        grouped["其他"] = no_concept[:10]

    return grouped


def print_results(grouped, latest_date):
    print("\n" + "=" * 60)
    print(f"📊 放量股分析 {latest_date} (10日翻倍 + 今日放量)")
    print("=" * 60)

    total = 0
    for concept, stocks in grouped.items():
        if concept == "其他" and total >= 15:
            continue
        print(f"\n### {concept} ({len(stocks)}只)")
        print("| 代码 | 名称 | 收盘价 | 涨幅 | 今日/昨日 | 今日/10日前 |")
        print("|:---|:---|:---:|:---:|:---:|:---:|")
        for s in stocks[:MAX_STOCKS_PER_CONCEPT]:
            pct_str = f"+{s['pct_chg']:.2f}%" if s["pct_chg"] >= 0 else f"{s['pct_chg']:.2f}%"
            print(
                f"| {s['code']} | {s['name']} | {s['close']:.2f} "
                f"| {pct_str} | {s['ratio_today_yesterday']:.2f}x "
                f"| {s['ratio_today_10d']:.2f}x |"
            )
        total += len(stocks)

    print("\n" + "=" * 60)
    print("⚠️ 风险提示：放量可能是资金短期炒作，注意追高风险！")
    print("=" * 60)


def main():
    config = get_db_config()

    db = mysql.connector.connect(**config)
    cur = db.cursor()

    try:
        cur.execute("SELECT MAX(trade_date) FROM t_stock WHERE volume > 0")
        latest_date = cur.fetchone()[0]
        print(f"最新交易日期: {latest_date}")

        all_dates = get_trading_dates(cur, latest_date)
        today = latest_date
        yesterday = all_dates[1] if len(all_dates) > 1 else None
        ten_days_ago = all_dates[9] if len(all_dates) > 9 else None
        print(f"对比日期: 今日={today}, 昨日={yesterday}, 10日前={ten_days_ago}")

        if not yesterday or not ten_days_ago:
            print("无法获取足够的交易日数据")
            sys.exit(1)

        data = fetch_volume_data(cur, today, yesterday, ten_days_ago)
        results = filter_volume_stocks(data)
        print(f"\n符合条件的股票数量: {len(results)}")

        top_results = results[:MAX_TOTAL_DISPLAY]
        top_codes = [r["code"] for r in top_results]
        names = fetch_stock_names(cur, top_codes[:30])
        concept_map = fetch_concept_map(cur, top_codes)
        grouped = group_by_concept(top_results, concept_map, names)

        print_results(grouped, latest_date)
    finally:
        cur.close()
        db.close()


if __name__ == "__main__":
    main()
