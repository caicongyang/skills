#!/usr/bin/env python3
"""
放量股分析：选出10个交易日内存在成交量翻倍且今日成交量翻倍的股票
"""
import mysql.connector
import sys
import os
from collections import defaultdict

VOLUME_RATIO_THRESHOLD = 2
LOOKBACK_DAYS = 10
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


def fetch_volume_data_all_days(cursor, dates):
    """获取指定日期范围内所有股票的成交量数据"""
    placeholders = ",".join(["%s"] * len(dates))
    cursor.execute(f"""
        SELECT stock_code, trade_date, volume, close, pct_chg 
        FROM t_stock 
        WHERE trade_date IN ({placeholders}) AND volume > 0
        ORDER BY stock_code, trade_date
    """, dates)

    data = defaultdict(dict)
    for code, date, vol, close, pct in cursor.fetchall():
        data[code][date] = {"volume": vol, "close": close, "pct_chg": pct}

    return data


def filter_volume_stocks(data, dates, threshold=VOLUME_RATIO_THRESHOLD):
    """
    筛选条件：
    1. 今日成交量 >= 2倍昨日成交量（今日翻倍）
    2. 过去10个交易日内，任意相邻两天存在成交量翻倍（历史翻倍）
    """
    today = dates[0]
    yesterday = dates[1]

    # dates 是按时间倒序的，取最近 LOOKBACK_DAYS+1 天用于比较相邻日
    lookback_dates = list(reversed(dates[:LOOKBACK_DAYS + 1]))

    results = []
    for code, daily in data.items():
        if today not in daily or yesterday not in daily:
            continue

        vol_today = daily[today]["volume"]
        vol_yesterday = daily[yesterday]["volume"]
        if not vol_today or not vol_yesterday:
            continue

        # 条件1：今日成交量翻倍
        ratio_today = vol_today / vol_yesterday
        if ratio_today < threshold:
            continue

        # 条件2：过去10个交易日内存在相邻两天成交量翻倍（不含今日vs昨日，已在条件1判断）
        has_historical_doubling = False
        historical_detail = None
        for i in range(1, len(lookback_dates)):
            prev_date = lookback_dates[i - 1]
            curr_date = lookback_dates[i]
            if curr_date == today:
                continue
            if prev_date in daily and curr_date in daily:
                prev_vol = daily[prev_date]["volume"]
                curr_vol = daily[curr_date]["volume"]
                if prev_vol and curr_vol and curr_vol >= prev_vol * threshold:
                    has_historical_doubling = True
                    historical_detail = {
                        "date": curr_date,
                        "ratio": curr_vol / prev_vol,
                    }
                    break

        if not has_historical_doubling:
            continue

        results.append({
            "code": code,
            "close": daily[today]["close"],
            "pct_chg": daily[today]["pct_chg"],
            "ratio_today": ratio_today,
            "hist_date": historical_detail["date"],
            "hist_ratio": historical_detail["ratio"],
        })

    results.sort(key=lambda x: x["ratio_today"], reverse=True)
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
    print("\n" + "=" * 70)
    print(f"📊 放量股分析 {latest_date} — 10个交易日内存在成交量翻倍且今日成交量翻倍")
    print("=" * 70)

    total = 0
    for concept, stocks in grouped.items():
        if concept == "其他" and total >= 15:
            continue
        print(f"\n### {concept} ({len(stocks)}只)")
        print("| 代码 | 名称 | 收盘价 | 涨幅 | 今日倍数 | 历史翻倍日 | 历史倍数 |")
        print("|:---|:---|:---:|:---:|:---:|:---:|:---:|")
        for s in stocks[:MAX_STOCKS_PER_CONCEPT]:
            pct_str = f"+{s['pct_chg']:.2f}%" if s["pct_chg"] >= 0 else f"{s['pct_chg']:.2f}%"
            print(
                f"| {s['code']} | {s['name']} | {s['close']:.2f} "
                f"| {pct_str} | {s['ratio_today']:.2f}x "
                f"| {s['hist_date']} | {s['hist_ratio']:.2f}x |"
            )
        total += len(stocks)

    print("\n" + "=" * 70)
    print("⚠️ 风险提示：放量可能是资金短期炒作，注意追高风险！")
    print("=" * 70)


def main():
    config = get_db_config()

    db = mysql.connector.connect(**config)
    cur = db.cursor()

    try:
        cur.execute("SELECT MAX(trade_date) FROM t_stock WHERE volume > 0")
        latest_date = cur.fetchone()[0]
        print(f"最新交易日期: {latest_date}")

        # 取近 LOOKBACK_DAYS+1 个交易日（多取1天用于相邻比较）
        all_dates = get_trading_dates(cur, latest_date, LOOKBACK_DAYS + 2)
        today = all_dates[0]
        yesterday = all_dates[1] if len(all_dates) > 1 else None
        print(f"今日={today}, 昨日={yesterday}, 回看至={all_dates[-1] if all_dates else '?'}")

        if not yesterday or len(all_dates) < LOOKBACK_DAYS + 1:
            print("无法获取足够的交易日数据")
            sys.exit(1)

        data = fetch_volume_data_all_days(cur, all_dates)
        results = filter_volume_stocks(data, all_dates)
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
