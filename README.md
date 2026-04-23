# 学习通自动签到

基于 yuban10703/chaoxingsign 改编的学习通自动签到工具。

## 功能特性

- 自动登录学习通
- 自动查询课程签到状态
- 自动完成签到
- 支持照片签到
- 支持位置签到
- 支持 Server酱 推送签到结果
- 支持多用户

## 环境要求

- Python 3.6+

## 安装

```bash
pip install -r requirements.txt
```

## 配置

1. 复制配置文件示例：
```bash
cp config.json.example config.json
```

2. 编辑 `config.json`：
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

| 配置项 | 说明 |
|--------|------|
| username | 学习通手机号 |
| passwd | 学习通密码 |
| SCKEY | Server酱推送key (可选) |
| name | 签到显示的名字 |
| address | 签到地址 |
| latitude | 纬度 |
| longitude | 经度 |
| picname | 签到照片文件名 (可选) |

## 使用

### 本地运行

```bash
python xuexitongsign.py
```

### 云函数运行

```python
from xuexitongsign import main_handler

main_handler(None, None)
```

## 注意事项

- 请妥善保管配置文件，不要提交到公开仓库
- 使用前请确保了解相关风险
- 仅供学习交流使用
