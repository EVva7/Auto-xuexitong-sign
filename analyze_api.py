#!/usr/bin/env python3
"""
分析抓取的API日志
Usage: python analyze_api.py
"""

import json
import os
from collections import defaultdict

LOG_FILE = 'chaoxing_api_log.json'

def analyze_apis():
    if not os.path.exists(LOG_FILE):
        print(f"[-] 日志文件 {LOG_FILE} 不存在")
        print("[*] 请先运行: mitmproxy -s api_catcher.py")
        return
    
    apis = defaultdict(list)
    
    with open(LOG_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                data = json.loads(line)
                if 'url' in data:
                    url = data['url']
                    path = data.get('path', '')
                    method = data.get('method', 'GET')
                    
                    for keyword in ['login', 'sign', 'course', 'class', 'active', 'api']:
                        if keyword in path.lower():
                            apis[keyword].append({
                                'method': method,
                                'path': path,
                                'url': url,
                                'query': data.get('query', {}),
                                'time': data.get('time', '')
                            })
            except:
                continue
    
    print("\n" + "="*60)
    print("📡 检测到的API接口")
    print("="*60)
    
    for keyword, items in sorted(apis.items()):
        print(f"\n🔑 关键词: {keyword}")
        print("-" * 40)
        
        seen = set()
        for item in items:
            key = f"{item['method']}:{item['path']}"
            if key not in seen:
                seen.add(key)
                print(f"  {item['method']:6} {item['path']}")
                if item['query']:
                    print(f"         参数: {list(item['query'].keys())}")

    print("\n" + "="*60)
    print("📝 完整API列表")
    print("="*60)
    
    all_apis = []
    with open(LOG_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                data = json.loads(line)
                if 'url' in data and data.get('type') != 'response':
                    path = data.get('path', '')
                    if '/api' in path or '/apis' in path:
                        all_apis.append(f"{data.get('method', 'GET'):6} {path}")
            except:
                continue
    
    for api in sorted(set(all_apis)):
        print(f"  {api}")

if __name__ == '__main__':
    analyze_apis()
