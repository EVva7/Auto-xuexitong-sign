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

---

## 实现原理详解

### 1. 整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                      程序流程图                               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   ┌──────────┐    ┌──────────┐    ┌──────────────┐        │
│   │  登录    │ -> │ 获取课程 │ -> │  查询签到任务 │        │
│   └──────────┘    └──────────┘    └──────────────┘        │
│        │               │                   │                │
│        v               v                   v                │
│   ┌──────────┐    ┌──────────┐    ┌──────────────┐        │
│   │ 获取Cookie│    │ 课程列表 │    │ 自动签到    │        │
│   └──────────┘    └──────────┘    └──────────────┘        │
│                                             │              │
│                                             v              │
│                                    ┌─────────────────┐     │
│                                    │  推送通知/记录日志│     │
│                                    └─────────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

### 2. 核心实现原理

#### 2.1 登录获取Cookie

**原理：** 学习通使用Cookie来维持登录状态，登录成功后服务器返回Cookie，后续请求带上Cookie即可识别用户。

**实现代码：**
```python
def login(self):
    url = 'https://passport2-api.chaoxing.com/v11/loginregister'
    data = {'uname': self.username, 'code': self.passwd}
    session = requests.session()
    cookie_jar = session.post(url=url, data=data, headers=headers).cookies
    cookie_t = requests.utils.dict_from_cookiejar(cookie_jar)
    cook.append(cookie_t)
```

**请求地址：** `https://passport2-api.chaoxing.com/v11/loginregister`

**请求参数：**
| 参数 | 说明 |
|------|------|
| uname | 学习通手机号 |
| code | 学习通密码 |

**返回：** Cookie对象，包含UID等信息，后续请求需要携带。

---

#### 2.2 获取课程列表

**原理：** 调用学习通API获取当前用户的所有课程信息，包括课程ID、班级ID等。

**实现代码：**
```python
def get_course(self, cookie):
    url = "http://mooc1-api.chaoxing.com/mycourse/backclazzdata"
    res = requests.get(url, headers=headers, cookies=cookie)
    cdata = json.loads(res.text)
    
    for item in cdata['channelList']:
        courseid.append(item['content']['course']['data'][0]['id'])
        name.append(item['content']['course']['data'][0]['name'])
        classid.append(item['content']['id'])
```

**API地址：** `http://mooc1-api.chaoxing.com/mycourse/backclazzdata`

---

#### 2.3 查询签到任务

**原理：** 轮询每个课程的签到任务，查找状态为"进行中"的签到。

**实现代码：**
```python
def find_sign_task(self, i):
    url = "https://mobilelearn.chaoxing.com/ppt/activeAPI/taskactivelist"
    payload = {
        'courseId': str(allcourseid[i][index]),
        'classId': str(allclassid[i][index]),
        'uid': cook[i]['UID']
    }
    res = requests.get(url, params=payload, headers=headers, cookies=cook[i])
    
    for item in activeList:
        if item['activeType'] == 2 and item['status'] == 1:
            # activeType=2 表示签到任务
            # status=1 表示进行中
            self.sign(aid, i, index)
```

**API地址：** `https://mobilelearn.chaoxing.com/ppt/activeAPI/taskactivelist`

**参数说明：**
| 参数 | 说明 |
|------|------|
| courseId | 课程ID |
| classId | 班级ID |
| uid | 用户ID（从Cookie获取） |

**返回数据中的关键字段：**
| 字段 | 说明 |
|------|------|
| activeType | 2=签到, 3=投票, 4=测验等 |
| status | 1=进行中, 2=已结束 |
| id | 签到活动ID（用于签到） |

---

#### 2.4 发起签到

**原理：** 向签到API发送POST请求，携带用户信息和签到参数完成签到。

**实现代码：**
```python
def sign(self, aid, i, index):
    url = "https://mobilelearn.chaoxing.com/pptSign/stuSignajax"
    data = {
        'name': name,           # 显示的名字
        'address': address,     # 签到地址（位置签到）
        'activeId': aid,       # 签到活动ID
        'uid': cook[i]['UID'], # 用户ID
        'longitude': longitude, # 经度
        'latitude': latitude,   # 纬度
        'objectId': objectId   # 照片ID（照片签到）
    }
    res = requests.post(url, data=data, headers=headers, cookies=cook[i])
```

**API地址：** `https://mobilelearn.chaoxing.com/pptSign/stuSignajax`

**签到类型：**
| 类型 | 说明 |
|------|------|
| 普通签到 | 只需传入基本参数 |
| 位置签到 | 需传入address、latitude、longitude |
| 照片签到 | 需先上传图片获取objectId |

---

#### 2.5 照片上传（如需要）

**原理：** 如果配置了照片签到，需要先上传图片到学习通图床，获取objectId后再签到。

**实现代码：**
```python
def upload_pic(self, i):
    # 1. 获取上传token
    url = 'https://pan-yz.chaoxing.com/api/token/uservalid'
    res = requests.get(url, headers=headers, cookies=cook[0])
    token = json.loads(res.text)['_token']
    
    # 2. 上传图片
    url = 'https://pan-yz.chaoxing.com/upload'
    files = {'file': (picname, open(picname, 'rb'), 'image/*')}
    res = requests.post(url, data={'puid': cook[0]['UID'], '_token': token}, 
                      files=files, headers=headers, cookies=cook[0])
    objectId = json.loads(res.text)['objectId']
```

---

#### 2.6 微信推送

**原理：** 签到完成后调用Server酱API发送微信通知。

**实现代码：**
```python
def push(self, i, index, msg):
    api = 'https://sc.ftqq.com/{SCKEY}.send'
    data = {
        "text": "签到成功!",
        "desp": f"课程: {course_name}\n状态: {msg}"
    }
    requests.post(api, data=data)
```

---

### 3. 完整流程时序图

```
用户                    学习通服务器                 Server酱
  │                        │                        │
  │──登录请求(username)──>│                        │
  │<──Cookie(UID)────────│                        │
  │                        │                        │
  │──获取课程列表────────>│                        │
  │<──课程列表───────────│                        │
  │                        │                        │
  │──查询签到任务────────>│                        │
  │<──签到任务列表───────│                        │
  │                        │                        │
  │──[发现待签到]────────>│                        │
  │<──签到结果(success)──│                        │
  │                        │                        │
  │                        │──微信通知────────────>│
  │                        │                        │
```

---

### 4. 日志文件说明

**sign.log** - 运行日志
```
[2024-01-01 12:00:00] [INFO] 获取配置成功
[2024-01-01 12:00:00] [INFO] 用户 0 获取cookie成功
[2024-01-01 12:00:01] [INFO] 用户 0 获取到 5 门课程
[2024-01-01 12:00:03] [INFO] 用户 0 课程 Python基础 签到成功!
[2024-01-01 12:00:03] [SUCCESS] 微信推送成功
```

**sign_history.json** - 签到历史
```json
[
    {
        "time": "2024-01-01 12:00:03",
        "user": 0,
        "course": "Python基础",
        "aid": "123456",
        "status": "success"
    }
]
```

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

---

## Implementation Principle

### 1. Architecture

```
┌─────────────────────────────────────────┐
│           Program Flow                  │
├─────────────────────────────────────────┤
│   Login -> Get Courses -> Check Tasks  │
│                ↓                        │
│         Auto Sign-in                    │
│                ↓                        │
│    Push Notification / Log              │
└─────────────────────────────────────────┘
```

### 2. Core Implementation

#### 2.1 Login (Get Cookie)

**Principle:** Xuexitong uses cookies to maintain session. After login, server returns cookie for subsequent requests.

```python
url = 'https://passport2-api.chaoxing.com/v11/loginregister'
data = {'uname': username, 'code': password}
cookie_jar = session.post(url=url, data=data).cookies
```

**API:** `https://passport2-api.chaoxing.com/v11/loginregister`

#### 2.2 Get Course List

**Principle:** Call API to get all courses for current user.

```python
url = "http://mooc1-api.chaoxing.com/mycourse/backclazzdata"
res = requests.get(url, cookies=cookie)
```

**API:** `http://mooc1-api.chaoxing.com/mycourse/backclazzdata`

#### 2.3 Find Sign-in Tasks

**Principle:** Poll each course for active sign-in tasks.

```python
url = "https://mobilelearn.chaoxing.com/ppt/activeAPI/taskactivelist"
payload = {'courseId': course_id, 'classId': class_id, 'uid': uid}
# activeType=2, status=1 means active sign-in
```

**API:** `https://mobilelearn.chaoxing.com/ppt/activeAPI/taskactivelist`

| Parameter | Description |
|-----------|-------------|
| courseId | Course ID |
| classId | Class ID |
| uid | User ID (from Cookie) |

#### 2.4 Submit Sign-in

**Principle:** Send POST request to complete sign-in.

```python
url = "https://mobilelearn.chaoxing.com/pptSign/stuSignajax"
data = {
    'activeId': aid,
    'uid': uid,
    'name': name,
    'address': address,
    'latitude': latitude,
    'longitude': longitude,
    'objectId': objectId  # for photo sign-in
}
```

**API:** `https://mobilelearn.chaoxing.com/pptSign/stuSignajax`

| Sign Type | Description |
|-----------|-------------|
| Normal | Basic parameters only |
| Location | Requires address, latitude, longitude |
| Photo | Requires objectId from uploaded image |

#### 2.5 Photo Upload (Optional)

```python
# 1. Get upload token
url = 'https://pan-yz.chaoxing.com/api/token/uservalid'
# 2. Upload photo
url = 'https://pan-yz.chaoxing.com/upload'
```

#### 2.6 WeChat Push

```python
api = 'https://sc.ftqq.com/{SCKEY}.send'
requests.post(api, data={"text": "签到成功!", "desp": content})
```

### 3. Log Files

**sign.log** - Runtime log
```
[2024-01-01 12:00:00] [INFO] Get config success
[2024-01-01 12:00:00] [INFO] User 0 login success
[2024-01-01 12:00:03] [SUCCESS] User 0 course Python 签到成功!
```

**sign_history.json** - Sign history
```json
[
    {
        "time": "2024-01-01 12:00:03",
        "user": 0,
        "course": "Python",
        "aid": "123456",
        "status": "success"
    }
]
```

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
