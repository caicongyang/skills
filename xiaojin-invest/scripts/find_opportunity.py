#!/usr/bin/env python3
"""
新机会发现器 - 寻找下一个15倍股
基于小金投资方法论：
1. 基本面驱动（AI需求 → 业绩增长）
2. EPS 预测大幅上调
3. 估值合理（P/E 适中）
"""
import yfinance as yf
import time
from datetime import datetime, timedelta

# AI/科技相关股票池（扩大范围发现新机会）
AI_TECH_STOCKS = {
    # AI 基础设施
    'NVDA': {'name': 'NVIDIA', 'cat': 'AI芯片'},
    'AMD': {'name': 'AMD', 'cat': 'AI芯片'},
    'INTC': {'name': 'Intel', 'cat': 'AI芯片'},
    'AVGO': {'name': 'Broadcom', 'cat': 'AI芯片'},
    'TSM': {'name': '台积电', 'cat': 'AI芯片'},
    
    # 存储
    'MU': {'name': 'Micron', 'cat': '存储'},
    'WDC': {'name': 'Western Digital', 'cat': '存储'},
    'STX': {'name': 'Seagate', 'cat': '存储'},
    
    # AI 应用
    'MSFT': {'name': 'Microsoft', 'cat': 'AI应用'},
    'GOOGL': {'name': 'Google', 'cat': 'AI应用'},
    'AMZN': {'name': 'Amazon', 'cat': 'AI应用'},
    'META': {'name': 'Meta', 'cat': 'AI应用'},
    'PLTR': {'name': 'Palantir', 'cat': 'AI应用'},
    
    # 算力/数据中心
    'DELL': {'name': 'Dell', 'cat': '服务器'},
    'HPE': {'name': 'HPE', 'cat': '服务器'},
    'SMCI': {'name': 'Super Micro', 'cat': '服务器'},
    
    # 光模块/网络
    'MRVL': {'name': 'Marvell', 'cat': '光模块'},
    'COHR': {'name': 'Coherent', 'cat': '光模块'},
    'LITE': {'name': 'Lumentum', 'cat': '光模块'},
    
    # AI 安全
    'PANW': {'name': 'Palo Alto', 'cat': '安全'},
    'FTNT': {'name': 'Fortinet', 'cat': '安全'},
    
    # 新兴AI标的
    'IO': {'name': 'ION OS', 'cat': 'AI基础设施'},
    'VRT': {'name': 'Vertiv', 'cat': '数据中心'},
    'DYES': {'name': 'Dayforce', 'cat': 'AI HR'},
}

def analyze_stock(symbol):
    """深度分析单只股票"""
    try:
        ticker = yf.Ticker(symbol)
        
        # 获取多个数据点
        info = ticker.info
        financials = ticker.financials
        earnings = ticker.earnings
        
        # 基础数据
        price = info.get('currentPrice', 0)
        pe_fwd = info.get('forwardPE', 0)
        eps_fwd = info.get('forwardEps', 0)
        eps_trailing = info.get('trailingEps', 0)
        target = info.get('targetMeanPrice', 0)
        recommendation = info.get('recommendationKey', '')
        
        # 计算增长
        eps_growth = 0
        if eps_trailing and eps_fwd:
            eps_growth = (eps_fwd - eps_trailing) / eps_trailing * 100
        
        # 上涨空间
        upside = 0
        if target and price:
            upside = (target - price) / price * 100
        
        # 关键信号判断
        signals = []
        
        # 信号1: EPS 增长 > 50%
        if eps_growth > 50:
            signals.append(f"EPS增长{eps_growth:.0f}%")
        
        # 信号2: 上涨空间 > 30%
        if upside > 30:
            signals.append(f"上涨空间{upside:.0f}%")
        
        # 信号3: P/E 合理 (< 30)
        if pe_fwd and pe_fwd < 30:
            signals.append(f"P/E={pe_fwd:.1f}")
        
        # 信号4: 分析师推荐
        if recommendation in ['buy', 'strongBuy']:
            signals.append(recommendation)
        
        # 综合评分 (0-100)
        score = 0
        if eps_growth > 50: score += 30
        if eps_growth > 100: score += 20
        if upside > 30: score += 20
        if upside > 50: score += 10
        if pe_fwd and pe_fwd < 20: score += 10
        if recommendation == 'strongBuy': score += 10
        
        if score >= 30:  # 只返回有价值的
            return {
                'symbol': symbol,
                'name': AI_TECH_STOCKS.get(symbol, {}).get('name', symbol),
                'cat': AI_TECH_STOCKS.get(symbol, {}).get('cat', '其他'),
                'price': round(price, 2) if price else 0,
                'pe': round(pe_fwd, 1) if pe_fwd else 0,
                'eps_fwd': round(eps_fwd, 2) if eps_fwd else 0,
                'eps_growth': round(eps_growth, 1) if eps_growth else 0,
                'target': round(target, 2) if target else 0,
                'upside': round(upside, 1) if upside else 0,
                'recommendation': recommendation,
                'signals': signals,
                'score': score
            }
    except Exception as e:
        pass
    return None

def main():
    print("🔭 发现下一个15倍股")
    print(f"扫描时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    opportunities = []
    count = 0
    
    for symbol in AI_TECH_STOCKS:
        count += 1
        print(f"[{count}/{len(AI_TECH_STOCKS)}] 分析 {symbol}...", end=" ", flush=True)
        
        result = analyze_stock(symbol)
        time.sleep(0.8)  # 避免限流
        
        if result:
            opportunities.append(result)
            print(f"✅ 得分:{result['score']} {result['signals']}")
        else:
            print("❌")
    
    print("\n" + "=" * 60)
    
    if opportunities:
        opportunities.sort(key=lambda x: x['score'], reverse=True)
        
        print("🎯 TOP 10 机会:\n")
        
        # 分类显示
        categories = {}
        for op in opportunities:
            cat = op['cat']
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(op)
        
        for cat, ops in categories.items():
            print(f"\n📁 {cat}:")
            for op in ops[:3]:  # 每类最多3个
                print(f"   {op['symbol']:6} {op['name']:20} PE={op['pe']:5} ↑{op['upside']:5}% 信号:{','.join(op['signals'][:2])}")
        
        print("\n" + "=" * 60)
        print(f"共发现 {len(opportunities)} 只潜力标的")
        
        # 保存到文件
        import json
        with open('/tmp/opportunities.json', 'w') as f:
            json.dump(opportunities, f, ensure_ascii=False, indent=2)
        print("\n📄 详细数据已保存到 /tmp/opportunities.json")
    else:
        print("😔 未发现明显机会，可能需要等待财报季")
    
    return opportunities

if __name__ == '__main__':
    main()
