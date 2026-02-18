#!/usr/bin/env python3
"""
板块股票监控脚本
基于小金投资方法论：寻找 P/E < 20 且有上涨空间的标的
"""
import yfinance as yf
import json
import time
from datetime import datetime

# 板块相关股票列表
SECTOR_STOCKS = {
    'SNDK': {'name': 'SanDisk', 'sector': '存储'},
    'NVDA': {'name': 'NVIDIA', 'sector': 'AI芯片'},
    'AMD': {'name': 'AMD', 'sector': 'AI芯片'},
    'INTC': {'name': 'Intel', 'sector': '芯片'},
    'MU': {'name': 'Micron', 'sector': '存储'},
    'TSM': {'name': '台积电', 'sector': '芯片制造'},
    'AVGO': {'name': 'Broadcom', 'sector': '芯片'},
}

def check_stock(symbol):
    """检查单只股票是否符合条件"""
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        pe = info.get('forwardPE', 0)
        eps = info.get('forwardEps', 0)
        price = info.get('currentPrice', 0)
        target = info.get('targetMeanPrice', 0)
        recommendation = info.get('recommendationKey', '')
        
        # 筛选条件
        if pe and pe > 0 and pe < 25:  # P/E < 25
            upside = 0
            if target and target > price:
                upside = (target - price) / price * 100
            
            return {
                'symbol': symbol,
                'name': SECTOR_STOCKS.get(symbol, {}).get('name', symbol),
                'sector': SECTOR_STOCKS.get(symbol, {}).get('sector', '未知'),
                'price': round(price, 2) if price else 0,
                'target': round(target, 2) if target else 0,
                'pe': round(pe, 2),
                'eps': round(eps, 2) if eps else 0,
                'upside': round(upside, 1),
                'recommendation': recommendation
            }
    except Exception as e:
        print(f"  ⚠️ {symbol}: {e}")
    return None

def main():
    print(f"🔍 板块监控 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    opportunities = []
    
    for i, symbol in enumerate(SECTOR_STOCKS):
        print(f"检查 {symbol}...", end=" ", flush=True)
        result = check_stock(symbol)
        time.sleep(1)  # 避免请求过快
        
        if result:
            opportunities.append(result)
            print(f"✅ PE={result['pe']}")
        else:
            print(f"❌ 不符合条件")
    
    print("\n" + "=" * 50)
    
    if opportunities:
        # 按上涨空间排序
        opportunities.sort(key=lambda x: x['upside'], reverse=True)
        
        print("🎯 发现投资机会:\n")
        print(f"{'代码':<8} {'名称':<12} {'板块':<10} {'现价':<8} {'目标价':<8} {'P/E':<6} {'上涨空间':<8}")
        print("-" * 70)
        
        for op in opportunities:
            print(f"{op['symbol']:<8} {op['name']:<12} {op['sector']:<10} ${op['price']:<7} ${op['target']:<7} {op['pe']:<6} +{op['upside']}%")
        
        print(f"\n共发现 {len(opportunities)} 只符合条件的股票")
        
        # 输出 JSON 格式（方便程序解析）
        print("\n📦 JSON Output:")
        print(json.dumps(opportunities, ensure_ascii=False, indent=2))
    else:
        print("😔 当前没有符合条件的标的")
        print("提示: P/E > 25 或没有目标价")
    
    return opportunities

if __name__ == '__main__':
    main()
