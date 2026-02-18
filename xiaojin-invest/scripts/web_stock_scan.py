#!/usr/bin/env python3
"""
基于 Web 的股票数据获取
使用 TradingView API 获取实时数据
"""
import requests
import json
import time
from datetime import datetime

# TradingView API
def get_stock_data(symbols):
    """从 TradingView 获取股票数据"""
    url = "https://scanner.tradingview.com/america/scan"
    
    # 简化：只获取价格
    results = {}
    
    for symbol in symbols:
        try:
            # 使用 Yahoo Finance API (移动端)
            yahoo_url = f"https://query1.finance.yahoo.com/v7/finance/quote?symbols={symbol}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            resp = requests.get(yahoo_url, headers=headers, timeout=10)
            data = resp.json()
            
            if 'quoteResponse' in data and 'result' in data['quoteResponse']:
                result = data['quoteResponse']['result']
                if result:
                    q = result[0]
                    results[symbol] = {
                        'name': q.get('shortName', symbol),
                        'price': q.get('regularMarketPrice', 0),
                        'pe': q.get('forwardPE', 0),
                        'eps': q.get('forwardEps', 0),
                        'target': q.get('targetMeanPrice', 0),
                        'recommendation': q.get('recommendationKey', ''),
                    }
            time.sleep(0.5)  # 避免限流
        except Exception as e:
            print(f"  ⚠️ {symbol}: {e}")
    
    return results

def find_opportunities(stocks_data):
    """筛选投资机会"""
    opportunities = []
    
    for symbol, data in stocks_data.items():
        if not data.get('price') or not data.get('pe'):
            continue
        
        pe = data.get('pe', 0)
        price = data.get('price', 0)
        target = data.get('target', 0)
        
        # 筛选条件
        if pe and 0 < pe < 30:  # P/E 合理
            upside = 0
            if target and target > price:
                upside = (target - price) / price * 100
            
            if upside > 20:  # 上涨空间 > 20%
                score = 0
                if pe < 15: score += 30
                if upside > 40: score += 30
                if data.get('recommendation') in ['buy', 'strongBuy']: score += 20
                
                opportunities.append({
                    'symbol': symbol,
                    **data,
                    'upside': round(upside, 1),
                    'score': score
                })
    
    return sorted(opportunities, key=lambda x: x['score'], reverse=True)

# 默认监控列表
WATCHLIST = [
    'NVDA', 'AMD', 'INTC', 'AVGO', 'TSM',  # 芯片
    'MU', 'WDC', 'STX',  # 存储
    'MSFT', 'GOOGL', 'AMZN', 'META',  # 科技巨头
    'MRVL', 'COHR',  # 光模块
    'DELL', 'SMCI', 'VRT',  # 服务器
]

def main():
    print(f"🔭 股票扫描 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    # 尝试获取数据
    print("获取数据中...")
    data = get_stock_data(WATCHLIST)
    
    if not data:
        print("❌ 无法获取数据")
        print("\n备选方案：使用 Web Fetch 获取 TradingView 数据")
        return None
    
    opportunities = find_opportunities(data)
    
    print(f"\n{'代码':<8} {'名称':<20} {'价格':<8} {'P/E':<6} {'目标价':<8} {'空间':<6}")
    print("-" * 70)
    
    for op in opportunities[:10]:
        print(f"{op['symbol']:<8} {op.get('name', '')[:18]:<20} ${op['price']:<7.2f} {op['pe']:<6.1f} ${op['target']:<7.1f} +{op['upside']}%")
    
    if opportunities:
        print(f"\n🎯 发现 {len(opportunities)} 只潜力股")
    else:
        print("\n😔 当前没有符合条件的标的")
    
    return opportunities

if __name__ == '__main__':
    main()
