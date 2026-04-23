import requests
import json
import time
import datetime
import os
import base64
from Crypto.Cipher import AES

session = requests.session()
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0',
    'Referer': 'http://passport2.chaoxing.com/login?fid=&newversion=true&refer=http%3A%2F%2Fi.chaoxing.com'
}
allname = []
allclassid = []
allcourseid = []
activates = []
cook = []
allobjectid = []

LOG_FILE = 'sign.log'
COOKIE_FILE = 'cookies.json'

def log(message, level='INFO'):
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_msg = f'[{timestamp}] [{level}] {message}'
    print(log_msg)
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(log_msg + '\n')


class Login:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.block_size = 16
        self.AES_KEY = "u2oh6Vu^HWe4_AES"

    def pad(self, text):
        text_length = len(text)
        amount_to_pad = self.block_size - (text_length % self.block_size)
        if amount_to_pad == 0:
            amount_to_pad = self.block_size
        pad = chr(amount_to_pad).encode()
        return text + pad * amount_to_pad

    def encrypt(self, text):
        ciper = AES.new(self.AES_KEY.encode(), AES.MODE_CBC, self.AES_KEY.encode())
        return base64.b64encode(ciper.encrypt(self.pad(text.encode()))).decode()

    def get_information(self):
        self.username = self.encrypt(self.username)
        self.password = self.encrypt(self.password)


class XxSign():
    def __init__(self, num, conf):
        self.username = conf['username'][num]
        self.passwd = conf['password'][num]
        self.retry_times = conf.get('retry_times', [3])[num] if isinstance(conf.get('retry_times', [3]), list) else conf.get('retry_times', 3)
        
        if len(conf.get('SENDKEY', [''])) == 1:
            self.SENDKEY = conf['SENDKEY'][0]
        else:
            self.SENDKEY = conf['SENDKEY'][num]

        if len(conf.get('TGCHATID', [''])) == 1:
            self.TGCHATID = conf['TGCHATID'][0]
        else:
            self.TGCHATID = conf['TGCHATID'][num]

        if len(conf.get('BOTTOKEN', [''])) == 1:
            self.BOTTOKEN = conf['BOTTOKEN'][0]
        else:
            self.BOTTOKEN = conf['BOTTOKEN'][num]

        if len(conf.get('name', [''])) == 1:
            self.name = conf['name'][0]
        else:
            self.name = conf['name'][num]

        if len(conf.get('address', [''])) == 1:
            self.address = conf['address'][0]
        else:
            self.address = conf['address'][num]

        if len(conf.get('longitude', [''])) == 1:
            self.longitude = conf['longitude'][0]
        else:
            self.longitude = conf['longitude'][num]

        if len(conf.get('latitude', [''])) == 1:
            self.latitude = conf['latitude'][0]
        else:
            self.latitude = conf['latitude'][num]

        if len(conf.get('picname', [''])) == 1:
            self.picname = conf['picname'][0]
        else:
            self.picname = conf['picname'][num]
            
        self.index = num

    def login(self):
        global session
        
        if os.path.exists(COOKIE_FILE):
            try:
                with open(COOKIE_FILE, 'r') as f:
                    session.cookies.update(json.load(f))
                log(f'用户 {self.index} 使用缓存Cookie')
                cookie_t = dict(session.cookies)
                if 'UID' in cookie_t and cookie_t['UID']:
                    cook.append(cookie_t)
                    log(f'用户 {self.index} Cookie有效')
                    return cookie_t
            except:
                pass
        
        url = 'http://passport2.chaoxing.com/fanyalogin'
        my_login = Login(self.username, self.passwd)
        my_login.get_information()
        
        data = {
            'fid': -1,
            'uname': my_login.username,
            'password': my_login.password,
            'refer': 'http%253A%252F%252Fi.chaoxing.com',
            't': True,
            'forbidotherlogin': 0
        }
        
        res = session.post(url, headers=headers, data=data)
        
        with open(COOKIE_FILE, 'w') as f:
            json.dump(res.cookies.get_dict(), f)
        
        cookie_t = res.cookies.get_dict()
        cook.append(cookie_t)
        log(f'用户 {self.index} 登录成功，获取新Cookie')
        return cookie_t

    def get_course(self, cookie):
        url = "https://mobilelearn.chaoxing.com/v2/apis/class/getClassList"
        res = requests.get(url, headers=headers, cookies=cookie)
        
        try:
            data = json.loads(res.text)
            name = []
            classid = []
            courseid = []
            fid = 0
            
            if data.get('result') != 1 and not data.get('data'):
                log(f'用户 {self.index} 课程列表获取失败: {data}', 'ERROR')
                return
            
            class_list = data.get('data', {}).get('classInfo', [])
            for item in class_list:
                courseid.append(item.get('courseId', ''))
                name.append(item.get('courseName', '未知课程'))
                classid.append(item.get('classId', ''))
                if item.get('fid'):
                    fid = item['fid']
            
            allname.append(name)
            allclassid.append(classid)
            allcourseid.append(courseid)
            cook[i]['fid'] = fid
            log(f'用户 {self.index} 获取到 {len(name)} 门课程')
        except Exception as e:
            log(f'获取课程列表异常: {str(e)}', 'ERROR')

    def find_sign_task(self, i):
        aid = []
        fid = cook[i].get('fid', 0)
        url = "https://mobilelearn.chaoxing.com/v2/apis/active/student/activelist"
        
        for index in range(len(allname[i])):
            payload = {
                'fid': str(fid),
                'courseId': str(allcourseid[i][index]),
                'classId': str(allclassid[i][index]),
                'showNotStartedActive': '0',
                '_': str(int(time.time() * 1000))
            }
            time.sleep(1.5)
            log(f'用户 {i} 正在查询课程: {allname[i][index]}')
            res = requests.get(url, params=payload, headers=headers, cookies=cook[i])
            respon = res.status_code
            
            if respon == 200:
                try:
                    data = json.loads(res.text)
                    activeList = data.get('data', {}).get('activeList', [])
                    for item in activeList:
                        if item.get('activeType') == 2 and item.get('status') == 1:
                            aid = item.get('id', item.get('activeId'))
                            if aid and aid not in activates:
                                log(f'[签到] {allname[i][index]} 查询到待签到活动 活动名称:{item.get("title", "未知")} 状态:{item.get("statusName", "进行中")} aid:{aid}')
                                self.sign(aid, i, index)
                except Exception as e:
                    log(f'解析签到任务异常: {str(e)}', 'ERROR')
                        if aid not in activates:
                            log(f'[签到] {allname[i][index]} 查询到待签到活动 活动名称:{item["nameOne"]} 活动状态:{item["nameTwo"]} 活动时间:{item["nameFour"]} aid:{aid}')
                            self.sign(aid, i, index)

    def get_token(self):
        url = 'https://pan-yz.chaoxing.com/api/token/uservalid'
        res = requests.get(url, headers=headers, cookies=cook[0])
        tokendict = json.loads(res.text)
        return tokendict['_token']

    def upload_pic(self, i):
        picname = XxSign(i, conf).picname if i < len(conf['username']) else ''

        if picname.isspace() or len(picname) == 0:
            return
        else:
            url = 'https://pan-yz.chaoxing.com/upload'
            files = {'file': (picname, open(picname, 'rb'), 'image/webp,image/*')}
            res = requests.post(url, data={'puid': cook[0]['UID'], '_token': self.get_token()}, 
                              files=files, headers=headers, cookies=cook[0])
            resdict = json.loads(res.text)
            allobjectid.append(resdict['objectId'])

    def sign(self, aid, i, index, retry_count=0):
        fid = cook[i].get('fid', 0)
        
        enc = ''
        try:
            enc_url = f'https://mobilelearn.chaoxing.com/v2/apis/sign/refreshQRCode?activeId={aid}'
            enc_res = requests.get(enc_url, headers=headers, cookies=cook[i])
            enc_data = enc_res.json()
            if enc_data.get('data'):
                enc = enc_data['data'].get('enc', '')
        except Exception as e:
            log(f'获取enc失败: {str(e)}', 'WARNING')
        
        user_sign = XxSign(i, conf) if i < len(conf['username']) else XxSign(0, conf)
        
        if len(user_sign.picname) == 0:
            objectId = ''
        else:
            self.upload_pic(i)
            objectId = allobjectid[i] if i < len(allobjectid) else ''

        name = user_sign.name
        address = user_sign.address
        longitude = user_sign.longitude
        latitude = user_sign.latitude

        sign_url = f"https://mobilelearn.chaoxing.com/pptSign/stuSignajax?activeId={aid}&clientip=&latitude=-1&longitude=-1&appType=15&fid={fid}&enc={enc}&address={address}"
        
        data = {
            'name': name,
            'address': address,
            'activeId': aid,
            'uid': cook[i]['UID'],
            'longitude': longitude,
            'latitude': latitude,
            'objectId': objectId,
            'fid': fid,
            'enc': enc
        }
        
        try:
            res = requests.post(sign_url, data=data, headers=headers, cookies=cook[i], timeout=10)
            result = res.text
            log(f'用户 {i} 签到响应: {result}')
            
            if result == 'success':
                log(f'用户 {i} 课程 {allname[i][index]} 签到成功!', 'SUCCESS')
                self.log_sign_result(i, index, aid, 'success')
                self.push(i, index, result)
            else:
                log(f'用户 {i} 课程 {allname[i][index]} 签到失败: {result}', 'WARNING')
                self.log_sign_result(i, index, aid, f'failed: {result}')
                
                if retry_count < user_sign.retry_times:
                    log(f'用户 {i} 正在重试 ({retry_count + 1}/{user_sign.retry_times})...', 'WARNING')
                    time.sleep(2)
                    self.sign(aid, i, index, retry_count + 1)
                else:
                    log(f'用户 {i} 课程 {allname[i][index]} 签到重试次数已用完', 'ERROR')
                    self.push_failed(i, index, result)
            
            activates.append(aid)
            
        except Exception as e:
            log(f'签到请求异常: {str(e)}', 'ERROR')
            if retry_count < user_sign.retry_times:
                log(f'用户 {i} 正在重试 ({retry_count + 1}/{user_sign.retry_times})...', 'WARNING')
                time.sleep(2)
                self.sign(aid, i, index, retry_count + 1)
            else:
                log(f'用户 {i} 课程 {allname[i][index]} 签到重试次数已用完', 'ERROR')

    def log_sign_result(self, i, index, aid, status):
        log_data = {
            'time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'user': i,
            'course': allname[i][index] if index < len(allname[i]) else 'unknown',
            'aid': aid,
            'status': status
        }
        log_file = 'sign_history.json'
        
        history = []
        if os.path.exists(log_file):
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
            except:
                history = []
        
        history.append(log_data)
        
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)

    def push(self, i, index, msg):
        user_sign = XxSign(i, conf) if i < len(conf['username']) else XxSign(0, conf)
        
        course_name = allname[i][index] if index < len(allname[i]) else 'unknown'
        
        self.push_serverchan(user_sign.SENDKEY, course_name, msg)
        self.push_telegram(user_sign.TGCHATID, user_sign.BOTTOKEN, course_name, msg)

    def push_serverchan(self, SENDKEY, course_name, msg):
        if not SENDKEY or SENDKEY.isspace():
            log('SENDKEY 为空，跳过Server酱推送')
            return
        
        if msg == 'success':
            title = "学习通-签到成功"
            desp = f"{course_name} 签到成功"
        elif msg == '您已签到过了':
            title = "学习通-已签到过了"
            desp = f"{course_name} 您已签到过了"
        else:
            title = "学习通-签到失败"
            desp = f"签到失败，原因：{msg}"
        
        try:
            api = f'https://sctapi.ftqq.com/{SENDKEY}.send'
            data = {'text': title, 'desp': desp}
            r = requests.post(api, data=data, timeout=10)
            if r.status_code == 200:
                log('Server酱推送成功')
            elif r.status_code == 400:
                log('Server酱推送失败，SENDKEY填写有误', 'ERROR')
            else:
                log(f'Server酱推送失败，状态码: {r.status_code}', 'ERROR')
        except Exception as e:
            log(f'Server酱推送异常: {str(e)}', 'ERROR')

    def push_telegram(self, TGCHATID, BOTTOKEN, course_name, msg):
        if not TGCHATID or not BOTTOKEN or TGCHATID.isspace() or BOTTOKEN.isspace():
            return
        
        if msg == 'success':
            text = f"{course_name} 签到成功"
        elif msg == '您已签到过了':
            text = f"{course_name} 您已签到过了"
        else:
            text = f"签到失败，原因：{msg}"
        
        try:
            api = f'https://api.telegram.org/bot{BOTTOKEN}/sendMessage?chat_id={TGCHATID}&text={text}'
            r = requests.get(api, timeout=10)
            if r.status_code == 200:
                log('Telegram推送成功')
            elif r.status_code == 400:
                log('Telegram推送失败，CHAT_ID填写有误', 'ERROR')
            else:
                log(f'Telegram推送失败，状态码: {r.status_code}', 'ERROR')
        except Exception as e:
            log(f'Telegram推送异常: {str(e)}', 'ERROR')

    def push_failed(self, i, index, msg):
        user_sign = XxSign(i, conf) if i < len(conf['username']) else XxSign(0, conf)
        course_name = allname[i][index] if index < len(allname[i]) else 'unknown'
        
        self.push_serverchan(user_sign.SENDKEY, course_name, msg)


def load_config():
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.loads(f.read())
            log('获取配置成功')
            
            if 'retry_times' not in config:
                config['retry_times'] = [3]
            elif isinstance(config['retry_times'], int):
                config['retry_times'] = [config['retry_times']]
            
            if 'SENDKEY' not in config:
                config['SENDKEY'] = ['']
            if 'TGCHATID' not in config:
                config['TGCHATID'] = ['']
            if 'BOTTOKEN' not in config:
                config['BOTTOKEN'] = ['']
            
            return config
    except FileNotFoundError:
        log("配置文件 config.json 不存在，请创建配置文件", 'ERROR')
        exit(1)
    except json.JSONDecodeError:
        log("配置文件格式错误", 'ERROR')
        exit(1)


conf = {}


def main_handler(event=None, context=None):
    global conf
    conf = load_config()
    number = len(conf.get('username', []))
    
    if number == 0:
        log("未配置用户信息", 'ERROR')
        return
    
    log('========== 程序开始运行 ==========')
    
    for n in range(number):
        signer = XxSign(n, conf)
        signer.login()
        time.sleep(0.8)

    for m in range(number):
        signer = XxSign(m, conf)
        signer.get_course(cook[m])
        time.sleep(0.8)

    for o in range(number):
        signer = XxSign(o, conf)
        signer.find_sign_task(o)
    
    log('========== 本次运行结束 ==========')


if __name__ == "__main__":
    conf = load_config()
    number = len(conf.get('username', []))
    
    if number == 0:
        log("未配置用户信息", 'ERROR')
        exit(1)
    
    log('========== 程序开始运行 ==========')
    
    for n in range(number):
        signer = XxSign(n, conf)
        signer.login()
        time.sleep(0.8)

    for m in range(number):
        signer = XxSign(m, conf)
        signer.get_course(cook[m])
        time.sleep(0.8)
    
    while True:
        for o in range(number):
            signer = XxSign(o, conf)
            signer.find_sign_task(o)
        
        log(f'本次轮询完成，{conf.get("sleep_time", 60)}秒后进行下一次轮询')
        time.sleep(conf.get('sleep_time', 60))
