#!/usr/bin/env python3
"""
学习通API自动抓包脚本
Usage: mitmproxy -s api_catcher.py
"""

import json
import os
from datetime import datetime
from mitmproxy import http
from mitmproxy import ctx

LOG_FILE = 'chaoxing_api_log.json'
API_PATTERNS = [
    'chaoxing.com',
    'mobilelearn',
    'mooc1',
    'passport2'
]

FILTERED_PARAMS = ['password', 'passwd', 'code', 'token', 'UID', 'fid']

def should_log(url):
    """判断是否需要记录这个请求"""
    for pattern in API_PATTERNS:
        if pattern in url:
            return True
    return False

def sanitize_params(params):
    """过滤敏感参数"""
    if isinstance(params, dict):
        return {k: '***' if k.lower() in FILTERED_PARAMS else v 
                for k, v in params.items()}
    return params

def request(flow: http.HTTPFlow):
    """处理每个HTTP请求"""
    url = flow.request.pretty_url
    
    if not should_log(url):
        return
    
    log_entry = {
        'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'method': flow.request.method,
        'url': url,
        'path': flow.request.path,
        'query': dict(flow.request.query) if flow.request.query else {},
        'headers': dict(flow.request.headers) if flow.request.headers else {},
    }
    
    if flow.request.method in ['POST', 'PUT']:
        try:
            log_entry['post_data'] = flow.request.get_text(strict=False)
        except:
            log_entry['post_data'] = str(flow.request.content)
    
    log_entry['query'] = sanitize_params(log_entry['query'])
    
    print(f"[+] {flow.request.method} {flow.request.path}")
    
    try:
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
    except Exception as e:
        ctx.log.error(f"Write error: {e}")

def response(flow: http.HTTPFlow):
    """处理每个HTTP响应"""
    url = flow.request.pretty_url
    
    if not should_log(url):
        return
    
    try:
        response_text = flow.response.get_text(strict=False)
        
        if response_text and len(response_text) < 50000:
            log_entry = {
                'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'type': 'response',
                'url': url,
                'status_code': flow.response.status_code,
                'response': response_text[:10000]
            }
            
            with open(LOG_FILE, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
                
    except Exception as e:
        ctx.log.error(f"Response error: {e}")

def done():
    """脚本结束时调用"""
    print(f"\n[+] API日志已保存到: {LOG_FILE}")
    print("[+] 分析日志命令: python analyze_api.py")
