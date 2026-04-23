# 学习通API自动抓包指南

## 快速开始

### 1. 安装mitmproxy

```bash
pip install mitmproxy
```

### 2. 启动抓包

```bash
# 方式1: 直接运行
mitmproxy -s api_catcher.py

# 方式2: 后台运行
mitmproxy -s api_catcher.py --set flow_detail=0 &
```

### 3. 设置代理

**方法A: 浏览器**
1. 打开浏览器设置
2. 搜索"代理"
3. 手动设置HTTP代理: 127.0.0.1:8080

**方法B: Chrome启动参数**
```bash
chrome --proxy-server="127.0.0.1:8080"
```

**方法C: 手机抓包（需要电脑和手机在同一WiFi）**
1. 电脑IP: 运行 `ipconfig` 查看
2. 手机设置HTTP代理为: 电脑IP:8080
3. 手机浏览器访问: http://mitm.it 下载证书

### 4. 访问学习通

1. 浏览器访问: https://i.chaoxing.com/
2. 登录账号
3. 进入课程，点击签到
4. 观察终端输出的URL

### 5. 分析API

按 Ctrl+C 停止抓包，然后运行：

```bash
python analyze_api.py
```

这会显示检测到的所有API接口。

## 文件说明

| 文件 | 说明 |
|------|------|
| api_catcher.py | mitmproxy抓包脚本 |
| analyze_api.py | API分析脚本 |
| chaoxing_api_log.json | 抓包日志（自动生成） |

## 注意事项

1. 抓包时不要登录敏感账号
2. 日志中的密码等敏感信息已自动过滤
3. 抓包完成后记得关闭代理
