#!/usr/bin/env python3
"""
异动股分析：选出10个交易日内出现过成交量翻倍且今天涨停的股票，按概念分组
"""
import mysql.connector
import sys
import os
from collections import defaultdict

VOLUME_RATIO_THRESHOLD = 2
LIMIT_UP_PCT = 9.9
LOOKBACK_DAYS = 10
MAX_STOCKS_PER_CONCEPT = 5
MAX_TOTAL_DISPLAY = 50


def get_db_config():
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


def fetch_volume_data_all_days(cursor, dates):
    placeholders = ",".join(["%s"] * len(dates))
    cursor.execute(f"""
        SELECT stock_code, trade_date, volume, close, pct_chg, stock_name
        FROM t_stock 
        WHERE trade_date IN ({placeholders}) AND volume > 0
        ORDER BY stock_code, trade_date
    """, dates)

    data = defaultdict(dict)
    for code, date, vol, close, pct, name in cursor.fetchall():
        data[code][date] = {
            "volume": vol, "close": close, "pct_chg": pct, "name": name,
        }

    return data


def find_unusual_moves(data, dates):
    """
    筛选：
    1. 今日涨停（pct_chg >= 9.9%）
    2. 过去10个交易日内任意相邻两天存在成交量翻倍
    每只股票只保留倍数最大的翻倍事件
    """
    today = dates[0]
    lookback_dates = list(reversed(dates[:LOOKBACK_DAYS + 1]))

    results = []
    for code, daily in data.items():
        if today not in daily:
            continue

        today_data = daily[today]
        if not today_data["pct_chg"] or today_data["pct_chg"] < LIMIT_UP_PCT:
            continue

        name = today_data.get("name", code)
        if name and (name.startswith("ST") or name.startswith("*ST")):
            continue
        close = today_data["close"]
        if not close or close < 3 or close > 500:
            continue

        best_event = None
        for i in range(1, len(lookback_dates)):
            prev_date = lookback_dates[i - 1]
            curr_date = lookback_dates[i]
            if prev_date in daily and curr_date in daily:
                prev_vol = daily[prev_date]["volume"]
                curr_vol = daily[curr_date]["volume"]
                if prev_vol and curr_vol and curr_vol >= prev_vol * VOLUME_RATIO_THRESHOLD:
                    ratio = curr_vol / prev_vol
                    if not best_event or ratio > best_event["ratio"]:
                        best_event = {"date": curr_date, "ratio": ratio}

        if not best_event:
            continue

        results.append({
            "code": code,
            "name": name,
            "close": close,
            "pct_chg": today_data["pct_chg"],
            "double_date": best_event["date"],
            "vol_ratio": best_event["ratio"],
        })

    results.sort(key=lambda x: x["vol_ratio"], reverse=True)
    return results


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


def group_by_concept(results, concept_map):
    concept_stocks = defaultdict(list)
    no_concept = []

    for r in results:
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
            grouped[concept] = unique[:MAX_STOCKS_PER_CONCEPT]

    if no_concept:
        ungrouped = [s for s in no_concept if s["code"] not in seen]
        if ungrouped:
            grouped["其他"] = ungrouped[:10]

    return grouped


def print_results(grouped, latest_date, total_count):
    print("\n" + "=" * 70)
    print(f"📈 异动股分析 {latest_date} — 10个交易日内出现过成交量翻倍且今天涨停")
    print("=" * 70)
    print(f"符合条件股票总数: {total_count}")

    total = 0
    for concept, stocks in grouped.items():
        if concept == "其他" and total >= 30:
            continue
        print(f"\n### 📈 {concept} ({len(stocks)}只)")
        print("| 代码 | 名称 | 收盘价 | 涨幅 | 翻倍日期 | 成交量倍数 |")
        print("|:---|:---|:---:|:---:|:---:|:---:|")
        for s in stocks:
            pct_str = f"+{s['pct_chg']:.2f}%" if s["pct_chg"] >= 0 else f"{s['pct_chg']:.2f}%"
            print(
                f"| {s['code']} | {s['name']} | {s['close']:.2f} "
                f"| {pct_str} | {s['double_date']} | {s['vol_ratio']:.2f}x |"
            )
        total += len(stocks)

    print("\n" + "=" * 70)
    print("⚠️ 风险提示：放量涨停可能是资金短期炒作，注意追高风险！")
    print("=" * 70)


def main():
    config = get_db_config()
    db = mysql.connector.connect(**config)
    cur = db.cursor()

    try:
        cur.execute("SELECT MAX(trade_date) FROM t_stock WHERE volume > 0")
        latest_date = cur.fetchone()[0]
        print(f"最新交易日期: {latest_date}")

        all_dates = get_trading_dates(cur, latest_date, LOOKBACK_DAYS + 2)
        if len(all_dates) < LOOKBACK_DAYS + 1:
            print("无法获取足够的交易日数据")
            sys.exit(1)

        print(f"回看区间: {all_dates[-1]} ~ {all_dates[0]} ({len(all_dates)}个交易日)")

        data = fetch_volume_data_all_days(cur, all_dates)
        results = find_unusual_moves(data, all_dates)
        print(f"符合条件的股票数量: {len(results)}")

        if not results:
            print("今日无符合条件的异动股")
            return

        top_results = results[:MAX_TOTAL_DISPLAY]
        top_codes = [r["code"] for r in top_results]
        concept_map = fetch_concept_map(cur, top_codes)
        grouped = group_by_concept(top_results, concept_map)

        print_results(grouped, latest_date, len(results))
    finally:
        cur.close()
        db.close()


if __name__ == "__main__":
    main()
