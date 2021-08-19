import base64
import hashlib
import logging as log
import random
import re
import time

import requests

import rsa
from notify import Notify

log.basicConfig(level=log.INFO)
BI_RM = list("0123456789abcdefghijklmnopqrstuvwxyz")
b64map = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"


def main(username, password):
    # 通知信息
    message = f"用户：{username[:3] + '****' + username[7:]}\n"
    s = requests.Session()
    login(s, username, password)
    rand = str(round(time.time() * 1000))
    nocache = random.random()
    surl = f'https://api.cloud.189.cn/mkt/userSign.action?rand={rand}&clientType=TELEANDROID&version=8.6.3&model=SM-G930K'
    url = f'https://m.cloud.189.cn/v2/drawPrizeMarketDetails.action?taskId=TASK_SIGNIN&activityId=ACT_SIGNIN'
    url2 = f'https://m.cloud.189.cn/v2/drawPrizeMarketDetails.action?taskId=TASK_SIGNIN_PHOTOS&activityId=ACT_SIGNIN'
    userInfoUrl = f'https://cloud.189.cn/api/open/user/getUserInfoForPortal.action?noCache={nocache}'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 5.1.1; SM-G930K Build/NRD90M; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/74.0.3729.136 Mobile Safari/537.36 Ecloud/8.6.3 Android/22 clientId/355325117317828 clientModel/SM-G930K imsi/460071114317824 clientChannelId/qq proVersion/1.0.6',
        "Referer": "https://m.cloud.189.cn/zhuanti/2016/sign/index.jsp?albumBackupOpened=1",
        "Host": "m.cloud.189.cn",
        "Accept-Encoding": "gzip, deflate",
    }
    headers2 = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36',
        "Referer": "https://cloud.189.cn/web/main/file/folder/-11",
        "Host": "m.cloud.189.cn",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept": "application/json;charset=UTF-8",
        "Host": "cloud.189.cn"
    }
    response = s.get(surl, headers=headers)
    netdiskBonus = response.json()['netdiskBonus']
    if (response.json()['isSign'] == "false"):
        message += f"状态：签到成功\n获得：{netdiskBonus}M空间"
        log.info(f"状态：签到成功，获得：{netdiskBonus}M空间")
    else:
        message += f"状态：已经签到过了\n获得：{netdiskBonus}M空间"
        log.info(f"状态：已经签到过了，获得：{netdiskBonus}M空间")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 5.1.1; SM-G930K Build/NRD90M; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/74.0.3729.136 Mobile Safari/537.36 Ecloud/8.6.3 Android/22 clientId/355325117317828 clientModel/SM-G930K imsi/460071114317824 clientChannelId/qq proVersion/1.0.6',
        "Referer": "https://m.cloud.189.cn/zhuanti/2016/sign/index.jsp?albumBackupOpened=1",
        "Host": "m.cloud.189.cn",
        "Accept-Encoding": "gzip, deflate",
    }
    response = s.get(url, headers=headers)
    if ("errorCode" in response.text):
        errCode = response.json()['errorCode']
        message += f"\n抽奖：{errCode}"
        log.info(response.text)
    else:
        description = response.json()['description']
        message += f"\n抽奖：{description}"
        log.info(f"抽奖获得{description}")
    response = s.get(url2, headers=headers)
    if ("errorCode" in response.text):
        errCode = response.json()['errorCode']
        message += f"\n抽奖：{errCode}"
        log.info(response.text)
    else:
        description = response.json()['description']
        message += f"\n抽奖：{description}"
        log.info(f"抽奖获得{description}")
    response = s.get(userInfoUrl, headers=headers2)
    userinfo = response.json()
    capacity = userinfo['capacity'] / 1073741824
    available = userinfo['available'] / 1073741824
    message += "\n总共容量：%.2fG" % capacity
    message += "\n可用容量：%.2fG" % available
    Notify().sendMessage(message)


def int2char(a):
    return BI_RM[a]


def b64tohex(a):
    d = ""
    e = 0
    c = 0
    for i in range(len(a)):
        if list(a)[i] != "=":
            v = b64map.index(list(a)[i])
            if 0 == e:
                e = 1
                d += int2char(v >> 2)
                c = 3 & v
            elif 1 == e:
                e = 2
                d += int2char(c << 2 | v >> 4)
                c = 15 & v
            elif 2 == e:
                e = 3
                d += int2char(c)
                d += int2char(v >> 2)
                c = 3 & v
            else:
                e = 0
                d += int2char(c << 2 | v >> 4)
                d += int2char(15 & v)
    if e == 1:
        d += int2char(c << 2)
    return d


def rsa_encode(j_rsakey, string):
    rsa_key = f"-----BEGIN PUBLIC KEY-----\n{j_rsakey}\n-----END PUBLIC KEY-----"
    pubkey = rsa.PublicKey.load_pkcs1_openssl_pem(rsa_key.encode())
    result = b64tohex((base64.b64encode(rsa.encrypt(f'{string}'.encode(), pubkey))).decode())
    return result


def calculate_md5_sign(params):
    return hashlib.md5('&'.join(sorted(params.split('&'))).encode('utf-8')).hexdigest()


def login(s, username, password):
    url = "https://cloud.189.cn/api/portal/loginUrl.action?redirectURL=https%3A%2F%2Fcloud.189.cn%2Fweb%2Fredirect.html"
    r = s.get(url)
    captchaToken = re.findall(r"captchaToken' value='(.+?)'", r.text)[0]
    lt = re.findall(r'lt = "(.+?)"', r.text)[0]
    returnUrl = re.findall(r"returnUrl = '(.+?)'", r.text)[0]
    paramId = re.findall(r'paramId = "(.+?)"', r.text)[0]
    j_rsakey = re.findall(r'j_rsaKey" value="(\S+)"', r.text, re.M)[0]
    s.headers.update({"lt": lt})

    username = rsa_encode(j_rsakey, username)
    password = rsa_encode(j_rsakey, password)
    url = "https://open.e.189.cn/api/logbox/oauth2/loginSubmit.do"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:74.0) Gecko/20100101 Firefox/76.0',
        'Referer': 'https://open.e.189.cn/',
    }
    data = {
        "appKey": "cloud",
        "accountType": '01',
        "userName": f"{{RSA}}{username}",
        "password": f"{{RSA}}{password}",
        "validateCode": "",
        "captchaToken": captchaToken,
        "returnUrl": returnUrl,
        "mailSuffix": "@189.cn",
        "paramId": paramId
    }
    r = s.post(url, data=data, headers=headers, timeout=5)
    if (r.json()['result'] == 0):
        log.info(r.json()['msg'])
    else:
        log.info(r.json()['msg'])
    redirect_url = r.json()['toUrl']
    r = s.get(redirect_url)
    return s


def main_handler(event, context):
    i = 1
    user = [
        {'user': '152xxxxxxxx', 'pwd': 'xxxxxxxx'}
    ]
    for u in user:
        log.info("第%s个帐号" % i)
        i += 1
        try:
            main(u['user'], u['pwd'])
        except Exception as result:
            log.error("异常%s"%result)

