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
    "picname": ["图片文件名"]
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

**说明：**
- 所有配置项都可以配置多个用户，使用数组格式
- 如果只有一个用户，可以只填一个值
- SCKEY 用于微信推送签到结果，去 [Server酱](https://sc.ftqq.com/) 申请

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

### 常见问题

**Q: 签到失败怎么办？**
A: 检查账号密码是否正确，网络是否稳定。

**Q: 如何后台运行？**
A: Linux/Mac 使用 screen 或 nohup，Windows 使用任务计划。

**Q: 怎么获取经纬度？**
A: 在地图应用上右键点击位置，选择"标注位置"即可看到坐标。

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
    "picname": ["photo_filename"]
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

**Notes:**
- All configs support multiple users in array format
- For single user, use single value
- SCKEY is for WeChat notifications, get it at [Server酱](https://sc.ftqq.com/)

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

### FAQ

**Q: Sign-in failed, what to do?**
A: Check if username/password is correct and network is stable.

**Q: How to run in background?**
A: Linux/Mac: use screen or nohup. Windows: use Task Scheduler.

**Q: How to get coordinates?**
A: Right-click on location in map apps to see coordinates.

### Warnings

1. Keep `config.json` safe, don't commit to public repo
2. Understand the risks before using
3. For learning purposes only
4. Set reasonable intervals to avoid frequent requests

---

## License

MIT License
