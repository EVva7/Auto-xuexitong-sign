import requests
import json
import time
import datetime
import os

session = requests.session()
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.108 Safari/537.36'}
allname = []
allclassid = []
allcourseid = []
activates = []
cook = []
allobjectid = []

LOG_FILE = 'sign.log'

def log(message, level='INFO'):
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_msg = f'[{timestamp}] [{level}] {message}'
    print(log_msg)
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(log_msg + '\n')


class XxSign():
    def __init__(self, num, conf):
        self.username = conf['username'][num]
        self.passwd = conf['passwd'][num]
        self.retry_times = conf.get('retry_times', 3)[num] if isinstance(conf.get('retry_times', [3]), list) else conf.get('retry_times', 3)
        
        if len(conf.get('SCKEY', [''])) == 1:
            self.SCKEY = conf['SCKEY'][0]
        else:
            self.SCKEY = conf['SCKEY'][num]

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
        url = 'https://passport2-api.chaoxing.com/v11/loginregister'
        data = {'uname': self.username, 'code': self.passwd}
        session = requests.session()
        cookie_jar = session.post(url=url, data=data, headers=headers).cookies
        cookie_t = requests.utils.dict_from_cookiejar(cookie_jar)
        cook.append(cookie_t)
        log(f'用户 {self.index} 获取cookie成功')
        return cookie_t

    def get_course(self, cookie):
        url = "http://mooc1-api.chaoxing.com/mycourse/backclazzdata"
        res = requests.get(url, headers=headers, cookies=cookie)
        cdata = json.loads(res.text)
        
        name = []
        classid = []
        courseid = []
        
        if cdata['result'] != 1:
            log(f'用户 {self.index} 课程列表获取失败', 'ERROR')
            return
        
        for item in cdata['channelList']:
            if "course" not in item['content']:
                continue
            courseid.append(item['content']['course']['data'][0]['id'])
            name.append(item['content']['course']['data'][0]['name'])
            classid.append(item['content']['id'])
        
        allname.append(name)
        allclassid.append(classid)
        allcourseid.append(courseid)
        log(f'用户 {self.index} 获取到 {len(name)} 门课程')

    def find_sign_task(self, i):
        aid = []
        url = "https://mobilelearn.chaoxing.com/ppt/activeAPI/taskactivelist"
        for index in range(len(allname[i])):
            payload = {
                'courseId': str(allcourseid[i][index]),
                'classId': str(allclassid[i][index]),
                'uid': cook[i]['UID']
            }
            time.sleep(1.5)
            log(f'用户 {i} 正在查询课程: {allname[i][index]}')
            res = requests.get(url, params=payload, headers=headers, cookies=cook[i])
            respon = res.status_code
            
            if respon == 200:
                data = json.loads(res.text)
                activeList = data.get('activeList', [])
                for item in activeList:
                    if "nameTwo" not in item:
                        continue
                    if item['activeType'] == 2 and item['status'] == 1:
                        aid = item['id']
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
        url = "https://mobilelearn.chaoxing.com/pptSign/stuSignajax"
        
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

        data = {
            'name': name,
            'address': address,
            'activeId': aid,
            'uid': cook[i]['UID'],
            'longitude': longitude,
            'latitude': latitude,
            'objectId': objectId
        }
        
        try:
            res = requests.post(url, data=data, headers=headers, cookies=cook[i], timeout=10)
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
        E_SCKEY = user_sign.SCKEY

        if E_SCKEY.isspace() or len(E_SCKEY) == 0:
            return
        else:
            api = f'https://sc.ftqq.com/{E_SCKEY}.send'
            title = "签到成功!"
            content = f'用户: {i}\n\n课程: {allname[i][index]}\n\n签到状态: {msg}'
            data = {
                "text": title,
                "desp": content
            }
            try:
                requests.post(api, data=data, timeout=10)
                log('微信推送成功')
            except Exception as e:
                log(f'微信推送失败: {str(e)}', 'ERROR')

    def push_failed(self, i, index, msg):
        user_sign = XxSign(i, conf) if i < len(conf['username']) else XxSign(0, conf)
        E_SCKEY = user_sign.SCKEY

        if E_SCKEY.isspace() or len(E_SCKEY) == 0:
            return
        else:
            api = f'https://sc.ftqq.com/{E_SCKEY}.send'
            title = "签到失败!"
            content = f'用户: {i}\n\n课程: {allname[i][index]}\n\n失败原因: {msg}'
            data = {
                "text": title,
                "desp": content
            }
            try:
                requests.post(api, data=data, timeout=10)
                log('失败通知推送成功')
            except Exception as e:
                log(f'失败通知推送失败: {str(e)}', 'ERROR')


def load_config():
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.loads(f.read())
            log('获取配置成功')
            
            if 'retry_times' not in config:
                config['retry_times'] = [3]
            elif isinstance(config['retry_times'], int):
                config['retry_times'] = [config['retry_times']]
            
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
