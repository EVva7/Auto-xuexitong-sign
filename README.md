# 学习通自动签到工具 / Xuexitong Auto Sign

[English](#english) | [中文](#中文)

---

## 中文

### 简介

基于 [yuban10703/chaoxingsign](https://github.com/yuban10703/chaoxingsign) 改编的学习通（超星）自动签到工具。

### 功能特性

- ✅ 自动登录学习通
- ✅ 自动查询课程签到状态  
- ✅ 自动完成签到
- ✅ 支持照片签到
- ✅ 支持位置签到
- ✅ 支持 Server酱 推送签到结果
- ✅ 支持多用户
- ✅ 签到日志记录
- ✅ 失败自动重试

### 环境要求

- Python 3.6+
- 网络连接

### 安装步骤

#### 1. 克隆项目

```bash
git clone https://github.com/EVva7/Auto-xuexitong-sign.git
cd Auto-xuexitong-sign
```

#### 2. 安装依赖

```bash
pip install -r requirements.txt
```

#### 3. 配置账号

```bash
cp config.example.json config.json
```

编辑 `config.json` 文件，填入你的信息：

```json
{
    "username": ["你的手机号"],
    "passwd": "你的密码",
    "SCKEY": ["你的server酱key"],
    "name": ["显示名字"],
    "address": "签到地址",
    "latitude": ["纬度"],
    "longitude": ["经度"],
    "picname": ["图片文件名"],
    "retry_times": [3],
    "sleep_time": 60
}
```

### 配置说明

| 配置项 | 必填 | 说明 | 示例 |
|--------|------|------|------|
| username | ✅ | 学习通手机号 | 13800138000 |
| passwd | ✅ | 学习通密码 | your_password |
| SCKEY | ❌ | Server酱推送key | SCUxxxxx |
| name | ❌ | 签到显示的名字 | 张三 |
| address | ❌ | 签到地址（位置签到用） | 北京市北京大学 |
| latitude | ❌ | 纬度 | 39.9042 |
| longitude | ❌ | 经度 | 116.4074 |
| picname | ❌ | 签到照片文件名 | photo.jpg |
| retry_times | ❌ | 签到失败重试次数 | 3 |
| sleep_time | ❌ | 轮询间隔（秒） | 60 |

**说明：**
- 所有配置项都可以配置多个用户，使用数组格式
- 如果只有一个用户，可以只填一个值
- SCKEY 用于微信推送签到结果，去 [Server酱](https://sc.ftqq.com/) 申请
- retry_times: 签到失败后自动重试的次数，默认为3次
- sleep_time: 每次轮询之间的等待时间，默认为60秒

### 使用方法

#### 方法一：本地运行（持续签到）

```bash
python xuexitongsign.py
```

程序会一直运行，每隔一段时间自动检查并签到。

#### 方法二：云函数运行（腾讯云）

```python
from xuexitongsign import main_handler

# 触发函数
main_handler(None, None)
```

### 日志文件

程序会自动生成以下日志文件：

| 文件 | 说明 |
|------|------|
| `sign.log` | 运行日志，记录程序运行状态 |
| `sign_history.json` | 签到历史，记录每次签到结果 |

### 常见问题

**Q: 签到失败怎么办？**
A: 程序会自动重试（默认3次），可在 config.json 中调整 `retry_times`。

**Q: 如何后台运行？**
A: 
- Linux/Mac: `nohup python xuexitongsign.py &`
- 或使用 screen: `screen -S sign && python xuexitongsign.py`
- Windows 使用任务计划或创建一个 `.bat` 文件

**Q: 怎么获取经纬度？**
A: 在地图应用上右键点击位置，选择"标注位置"即可看到坐标。

**Q: 如何停止程序？**
A: 
- Linux/Mac: `pkill -f xuexitongsign.py`
- 或按 `Ctrl + C`

### 注意事项

1. 请妥善保管 `config.json`，不要提交到公开仓库
2. 使用前请确保了解相关风险
3. 仅供学习交流使用
4. 建议设置合理的签到间隔，避免频繁请求

---

## English

### Introduction

An automated sign-in tool for Xuexitong (Chaoxing) based on [yuban10703/chaoxingsign](https://github.com/yuban10703/chaoxingsign).

### Features

- ✅ Auto login to Xuexitong
- ✅ Auto check sign-in status
- ✅ Auto complete sign-in
- ✅ Photo sign-in support
- ✅ Location sign-in support  
- ✅ Server酱 (WeChat) push notification
- ✅ Multi-user support
- ✅ Sign-in logging
- ✅ Auto retry on failure

### Requirements

- Python 3.6+
- Internet connection

### Installation

#### 1. Clone the project

```bash
git clone https://github.com/EVva7/Auto-xuexitong-sign.git
cd Auto-xuexitong-sign
```

#### 2. Install dependencies

```bash
pip install -r requirements.txt
```

#### 3. Configure your account

```bash
cp config.example.json config.json
```

Edit `config.json` with your information:

```json
{
    "username": ["your_phone_number"],
    "passwd": "your_password",
    "SCKEY": ["your_serverchan_key"],
    "name": ["your_display_name"],
    "address": "sign_in_address",
    "latitude": ["latitude"],
    "longitude": ["longitude"],
    "picname": ["photo_filename"],
    "retry_times": [3],
    "sleep_time": 60
}
```

### Config Guide

| Config | Required | Description | Example |
|--------|----------|-------------|---------|
| username | ✅ | Xuexitong phone number | 13800138000 |
| passwd | ✅ | Xuexitong password | your_password |
| SCKEY | ❌ | Server酱 key for push | SCUxxxxx |
| name | ❌ | Display name | John Doe |
| address | ❌ | Sign-in address | Peking University |
| latitude | ❌ | Latitude | 39.9042 |
| longitude | ❌ | Longitude | 116.4074 |
| picname | ❌ | Photo filename | photo.jpg |
| retry_times | ❌ | Retry count on failure | 3 |
| sleep_time | ❌ | Poll interval (seconds) | 60 |

**Notes:**
- All configs support multiple users in array format
- For single user, use single value
- SCKEY is for WeChat notifications, get it at [Server酱](https://sc.ftqq.com/)
- retry_times: Number of auto retries on sign-in failure, default is 3
- sleep_time: Wait time between polls, default is 60 seconds

### Usage

#### Method 1: Local Run (Continuous)

```bash
python xuexitongsign.py
```

The program will run continuously and check/sign in periodically.

#### Method 2: Cloud Function (Tencent Cloud)

```python
from xuexitongsign import main_handler

# Trigger function
main_handler(None, None)
```

### Log Files

The program automatically generates the following log files:

| File | Description |
|------|-------------|
| `sign.log` | Runtime log, records program status |
| `sign_history.json` | Sign-in history, records each sign-in result |

### FAQ

**Q: Sign-in failed, what to do?**
A: The program will automatically retry (default 3 times). Adjust `retry_times` in config.json.

**Q: How to run in background?**
A: 
- Linux/Mac: `nohup python xuexitongsign.py &`
- Or use screen: `screen -S sign && python xuexitongsign.py`
- Windows: Task Scheduler or create a `.bat` file

**Q: How to get coordinates?**
A: Right-click on location in map apps to see coordinates.

**Q: How to stop the program?**
A: 
- Linux/Mac: `pkill -f xuexitongsign.py`
- Or press `Ctrl + C`

### Warnings

1. Keep `config.json` safe, don't commit to public repo
2. Understand the risks before using
3. For learning purposes only
4. Set reasonable intervals to avoid frequent requests

---

## License

MIT License
