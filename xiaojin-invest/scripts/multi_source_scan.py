#!/usr/bin/env python3
"""
多数据源股票扫描器
支持 Financial Modeling Prep, Alpha Vantage, Finnhub
自动轮询切换
"""
import requests
import time
import json
from datetime import datetime

class StockScanner:
    def __init__(self, api_keys=None):
        self.api_keys = api_keys or {}
        self.current_source = None
    
    # ============ Financial Modeling Prep ============
    def query_fmp(self, symbol):
        """Financial Modeling Prep API"""
        key = self.api_keys.get('fmp')
        if not key:
            return None, "No FMP API key"
        
        url = f"https://financialmodelingprep.com/api/v3/profile/{symbol}?apikey={key}"
        try:
            resp = requests.get(url, timeout=10)
            data = resp.json()
            
            if data and isinstance(data, list) and len(data) > 0:
                item = data[0]
                return {
                    'source': 'FMP',
                    'symbol': symbol,
                    'name': item.get('companyName'),
                    'price': item.get('price'),
                    'pe': item.get('pe'),
                    'eps': item.get('eps'),
                    'target': item.get('targetMeanPrice'),
                    'recommendation': item.get('ratingRecommendation'),
                }, None
        except Exception as e:
            return None, str(e)
        return None, "No data"
    
    # ============ Alpha Vantage ============
    def query_alpha_vantage(self, symbol):
        """Alpha Vantage API"""
        key = self.api_keys.get('alphavantage')
        if not key:
            return None, "No Alpha Vantage API key"
        
        # 获取 overview
        url = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={symbol}&apikey={key}"
        try:
            resp = requests.get(url, timeout=10)
            data = resp.json()
            
            if 'Error Message' in data or 'Note' in data:
                return None, data.get('Error Message') or data.get('Note')
            
            if data.get('Name'):
                # 还需要获取 price
                price_url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={key}"
                price_resp = requests.get(price_url, timeout=10)
                price_data = price_resp.json()
                
                price = 0
                if 'Global Quote' in price_data:
                    price = float(price_data['Global Quote'].get('05. price', 0))
                
                return {
                    'source': 'AlphaVantage',
                    'symbol': symbol,
                    'name': data.get('Name'),
                    'price': price,
                    'pe': float(data.get('PERatio', 0) or 0),
                    'eps': float(data.get('EPS', 0) or 0),
                    'target': float(data.get('AnalystTargetPrice', 0) or 0),
                    'recommendation': '',
                }, None
        except Exception as e:
            return None, str(e)
        return None, "No data"
    
    # ============ Finnhub ============
    def query_finnhub(self, symbol):
        """Finnhub API"""
        key = self.api_keys.get('finnhub')
        if not key:
            return None, "No Finnhub API key"
        
        try:
            # 公司信息
            profile_url = f"https://finnhub.io/api/v1/stock/profile2?symbol={symbol}&token={key}"
            resp = requests.get(profile_url, timeout=10)
            profile = resp.json()
            
            if not profile or not profile.get('name'):
                return None, "No profile"
            
            # 报价
            quote_url = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={key}"
            quote_resp = requests.get(quote_url, timeout=10)
            quote = quote_resp.json()
            
            return {
                'source': 'Finnhub',
                'symbol': symbol,
                'name': profile.get('name'),
                'price': quote.get('c', 0),  # current
                'target': 0,  # finnhub没有目标价
                'recommendation': '',
            }, None
        except Exception as e:
            return None, str(e)
    
    # ============ 通用查询（轮询） ============
    def query(self, symbol):
        """轮询尝试各个数据源"""
        sources = [
            ('fmp', self.query_fmp),
            ('alpha', self.query_alpha_vantage),
            ('finnhub', self.query_finnhub),
        ]
        
        for name, func in sources:
            result, error = func(symbol)
            if result:
                return result, None
            time.sleep(0.5)  # 避免请求过快
        
        return None, "All sources failed"
    
    def scan_watchlist(self, symbols):
        """扫描自选股"""
        results = []
        for symbol in symbols:
            result, error = self.query(symbol)
            if result:
                results.append(result)
            time.sleep(1)  # 避免限流
        return results

# 默认监控列表
WATCHLIST = [
    'NVDA', 'AMD', 'INTC', 'AVGO', 'TSM',
    'MU', 'WDC', 'STX',
    'MRVL', 'COHR',
    'DELL', 'SMCI', 'VRT',
]

def main():
    # 从文件加载 API keys
    keys_file = '/root/.openclaw/workspace/skills/xiaojin-invest/config/keys.json'
    api_keys = {}
    
    try:
        with open(keys_file, 'r') as f:
            api_keys = json.load(f)
    except:
        print("⚠️ 请先配置 API keys")
        print("\n=== API Key 配置说明 ===")
        print("\n1. Financial Modeling Prep (推荐)")
        print("   官网: https://site.financialmodelingprep.com/")
        print("   免费: 250次/天")
        print("\n2. Alpha Vantage")
        print("   官网: https://www.alphavantage.co/")
        print("   免费: 500次/天")
        print("\n3. Finnhub")
        print("   官网: https://finnhub.io/")
        print("   免费: 60次/分钟")
        print("\n请将 API key 写入: keys.json")
        return
    
    scanner = StockScanner(api_keys)
    
    print(f"🔭 股票扫描 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    results = scanner.scan_watchlist(WATCHLIST)
    
    # 筛选机会
    opportunities = []
    for r in results:
        pe = r.get('pe', 0)
        price = r.get('price', 0)
        target = r.get('target', 0)
        
        if pe and 0 < pe < 30 and target and target > price:
            upside = (target - price) / price * 100
            if upside > 20:
                r['upside'] = round(upside, 1)
                opportunities.append(r)
    
    # 排序并显示
    opportunities.sort(key=lambda x: x.get('upside', 0), reverse=True)
    
    print(f"{'代码':<8} {'名称':<18} {'价格':<8} {'P/E':<6} {'目标':<8} {'空间':<6}")
    print("-" * 65)
    
    for op in opportunities:
        print(f"{op['symbol']:<8} {op.get('name', '')[:16]:<18} ${op['price']:<7.2f} {op['pe']:<6.1f} ${op['target']:<7.1f} +{op.get('upspace', 0)}%")
    
    print(f"\n🎯 发现 {len(opportunities)} 只潜力股")

if __name__ == '__main__':
    main()
