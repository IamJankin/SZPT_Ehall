import urllib.request, urllib.parse, urllib.error
import re
import http.cookiejar
from Crypto.Cipher import AES
import math
import random
import base64
import json
import sendMail
import time
import requests
import configparser
import os

#configparser初始化
dirname = os.path.split(os.path.realpath(__file__))[0]
config = configparser.ConfigParser()
config.read(dirname + "/config.ini", encoding="utf-8")
# 读取用户名密码
username = config.get("user", "username")
password = config.get("user", "password")

#URL
GET_INFO_POST_URL = 'https://ehall.szpt.edu.cn/publicappinternet/sys/szptpubxsjkxxbs/mrxxbs/getSaveReportInfo.do'   #获取信息
SAVE_INFO_POST_URL = 'https://ehall.szpt.edu.cn/publicappinternet/sys/szptpubxsjkxxbs/mrxxbs/saveReportInfo.do'     #提交信息
#GET_SESSION_URL将返回一个包含随机sessionToken的登录页面
GET_SESSION_URL = 'https://ehall.szpt.edu.cn:443/amp-auth-adapter/login?service=https%3A%2F%2Fehall.szpt.edu.cn%3A443%2Fpublicappinternet%2Fsys%2Fszptpubxsjkxxbs%2F*default%2Findex.do%3FnodeId%3D0%26taskId%3D0%26processInstanceId%3D0%26instId%3D0%26defId%3D0%26defKey%3D0'
UPDATE_COOKIE_URL = 'https://ehall.szpt.edu.cn/publicappinternet/sys/itpub/MobileCommon/getMenuInfo.do'
#LOGIN_URL = GET_LOGIN_URL()    #下面调用GET_LOGIN_URL()获取登录URL

# 请求头
header = {
    'User-Agent':'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.116 Mobile Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Host': 'ehall.szpt.edu.cn',
}
header_getinfo = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.116 Mobile Safari/537.36',

}

# 参数
APPID = ""
APPNAME = ""

lt = ''
execution = ''

# cookiejar
cookie = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie))

# AES
class AESCipher:

    def __init__(self, key):
        self.key = key[0:16].encode('utf-8')  # 只截取16位
        self.iv = self.random_string(16).encode()  # 16位字符，用来填充缺失内容，可固定值也可随机字符串，具体选择看需求。

    def __pad(self, text):
        """填充方式，加密内容必须为16字节的倍数，若不足则使用self.iv进行填充"""
        text_length = len(text)
        amount_to_pad = AES.block_size - (text_length % AES.block_size)
        if amount_to_pad == 0:
            amount_to_pad = AES.block_size
        pad = chr(amount_to_pad)
        return text + pad * amount_to_pad

    def __unpad(self, text):
        pad = ord(text[-1])
        return text[:-pad]

    def encrypt(self, text):
        """加密"""
        raw = self.random_string(64) + text
        raw = self.__pad(raw).encode()
        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        return base64.b64encode(cipher.encrypt(raw))

    def decrypt(self, enc):
        """解密"""
        enc = base64.b64decode(enc)
        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        return self.__unpad(cipher.decrypt(enc).decode("utf-8"))

    @staticmethod
    def random_string(length):
        aes_chars = 'ABCDEFGHJKMNPQRSTWXYZabcdefhijkmnprstwxyz2345678'
        aes_chars_len = len(aes_chars)
        retStr = ''
        for i in range(0, length):
            retStr += aes_chars[math.floor(random.random() * aes_chars_len)]
        return retStr

# 密码AES加密
def pwdEncrypt(aes_key):
    pc = AESCipher(aes_key)
    password_aes = pc.encrypt(password)
    return password_aes

# 获取登录页面
def GET_LOGIN_URL():
    res = requests.get(GET_SESSION_URL, allow_redirects=False)
    LOGIN_URL = res.headers['Location']
    return LOGIN_URL
LOGIN_URL = GET_LOGIN_URL()


# 登录
def login():
    global APPID, APPNAME
    # 登录请求
    request = urllib.request.Request(url=LOGIN_URL,
                                     method='GET')
    response = opener.open(request)
    html = response.read().decode('utf-8')

    # 获取登录参数
    lt = re.search('name="lt" value="(.*?)"/>', html, re.S).group(1)
    execution = re.search('name="execution" value="(.*?)"/>', html, re.S).group(1)
    aes_key = re.search('pwdDefaultEncryptSalt = "(.*?)";', html, re.S).group(1)
    password_aes = pwdEncrypt(aes_key)
    # print(password_aes)
    params = {
        'username': username,
        'password': password_aes,
        'lt': lt,
        'dllt': 'userNamePasswordLogin',
        'execution': execution,
        '_eventId': 'submit',
        'rmShown': '1'
    }

    # 登录提交
    request = urllib.request.Request(url=LOGIN_URL, data=urllib.parse.urlencode(params).encode(encoding='UTF-8'), method='POST')
    response = opener.open(request)
    html = response.read().decode('utf-8')

    # 登录判断
    if "USERID='"+ username + "'" in html:
        APPID = re.search("APPID='(.*?)';", html, re.S).group(1)
        APPNAME = re.search("APPNAME='(.*?)';", html, re.S).group(1)
        return 0
    elif "您的用户名或密码有误，可尝试使用手机验证码登录" in html:
        return 1
    elif html.count("验证码") == 12:
        return 2
    else:
        return 3

# 设置cookies
def set_cookies():
    params_data = {}
    params_data["APPID"] = APPID
    params_data["APPNAME"] = APPNAME
    # 转换成json参数
    params = {
        'data': json.dumps(params_data)
    }
    # 更新Cookie: _WEU
    request = urllib.request.Request(url=UPDATE_COOKIE_URL,
                                     data=urllib.parse.urlencode(params).encode(encoding='UTF-8'),
                                     method='POST', headers=header) # 获取Cookie: _WEU
    opener.open(request)


def send_info():
    # 设置cookies
    set_cookies()

    # 获取个人信息json数据
    params = {
        'USER_ID': username
    }
    request = urllib.request.Request(url=GET_INFO_POST_URL,
                                     data=urllib.parse.urlencode(params).encode(encoding='UTF-8'),
                                     method='POST', headers=header_getinfo)

    # 保存的参数
    response = opener.open(request)
    data = json.loads(response.read().decode('utf-8'))
    # print(data)
    # update 每日首次提交表单会缺失以下数据
    temp_dict = {
        "WID": "", "ZSDZ": "", "SXFS": "", "SFZZSXDWSS": "", "FSSJ": "", "FXSJ": "", "SSSQ": "", "XSQBDSJ": "",
        "JSJJGCJTSJ": "", "JSJTGCJTSJ": "", "JSJJJTGCYY": "", "STYCZK": "", "STYXZK": ""
    }
    data['datas'].update(temp_dict)
    now_date = time.strftime("%Y-%m-%d",time.localtime())   #获取当前日期

    # 提交信息
    params = {
        'formData': data['datas']
    }

    request = urllib.request.Request(url=SAVE_INFO_POST_URL,
                                     data=urllib.parse.urlencode(params).encode(encoding='UTF-8'),
                                     method='POST', headers=header_getinfo)
    response = opener.open(request)

    try:
        # 判断是否提交成功
        result_json = json.loads(response.read().decode('utf-8'))
        if result_json["code"] == "0":
            print("[+] 填报成功")
            sendMail.sendMail('SZPT - 填报成功 - 每日填报通知',"填报成功")

    except:
        print('[-] 已填报或需手动更新表单（以往表单数据不可用）')
        sendMail.sendMail('SZPT - 已填报或需手动更新表单 - 每日填报通知',"已填报或需手动更新表单（以往表单数据不可用）")

def main():
    if config.getint("other", "time_sleep") != 0:
        tsleep = random.randint(1,config.getint("other", "time_sleep"))
        print('[*] 延时运行%d秒'%tsleep)
        time.sleep(tsleep)

    login_status = login()
    if login_status == 0:
        print('[+] 登录成功')
        send_info()
    elif login_status == 1:
        print("[-] 登录失败，您的用户名或密码有误")
        sendMail.sendMail('SZPT - 用户名密码错误 - 每日填报通知',"您的用户名或密码有误")
    elif login_status == 2:
        print("[-] 无法登录，需要验证码，请稍后再试或手动填报。")
        sendMail.sendMail('SZPT - 无法登录，需要验证码 - 每日填报通知',"无法登录，需要验证码，请稍后再试或手动填报。")

    else:
        print("[-] 无法登录，未知错误，请检查网站是否能访问。")
        sendMail.sendMail('SZPT - 无法登录 - 每日填报通知',"无法登录，未知错误，请检查网站是否能访问")

if __name__ == '__main__':
    main()