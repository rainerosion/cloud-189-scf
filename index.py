import base64
import hashlib
import json
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
    s = login(username, password)
    rand = str(round(time.time() * 1000))
    nocache = random.random()
    surl = f'https://api.cloud.189.cn/mkt/userSign.action?rand={rand}&clientType=TELEANDROID&version=8.6.3&model=SM-G930K'
    url = f'https://m.cloud.189.cn/v2/drawPrizeMarketDetails.action?taskId=TASK_SIGNIN&activityId=ACT_SIGNIN'
    url2 = f'https://m.cloud.189.cn/v2/drawPrizeMarketDetails.action?taskId=TASK_SIGNIN_PHOTOS&activityId=ACT_SIGNIN'
    url3 = f'https://m.cloud.189.cn/v2/drawPrizeMarketDetails.action?taskId=TASK_2022_FLDFS_KJ&activityId=ACT_SIGNIN'
    user_info_url = f'https://cloud.189.cn/api/open/user/getUserInfoForPortal.action?noCache={nocache}'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 5.1.1; SM-G930K Build/NRD90M; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/74.0.3729.136 Mobile Safari/537.36 Ecloud/8.6.3 Android/22 clientId/355325117317828 clientModel/SM-G930K imsi/460071114317824 clientChannelId/qq proVersion/1.0.6',
        "Referer": "https://m.cloud.189.cn/zhuanti/2016/sign/index.jsp?albumBackupOpened=1",
        "Host": "m.cloud.189.cn",
        "Accept-Encoding": "gzip, deflate",
    }
    user_info_headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1',
        "Referer": "https://cloud.189.cn/api/open/user/getUserInfoForPortal.action",
        "Host": "cloud.189.cn",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept": "application/json;charset=UTF-8"
    }
    response = s.get(surl, headers=headers)
    netdisk_bonus = response.json()['netdiskBonus']
    if (response.json()['isSign'] == "false"):
        message += f"状态：签到成功\n获得：{netdisk_bonus}M空间"
        log.info(f"状态：签到成功，获得：{netdisk_bonus}M空间")
    else:
        message += f"状态：已经签到过了\n获得：{netdisk_bonus}M空间"
        log.info(f"状态：已经签到过了，获得：{netdisk_bonus}M空间")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 5.1.1; SM-G930K Build/NRD90M; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/74.0.3729.136 Mobile Safari/537.36 Ecloud/8.6.3 Android/22 clientId/355325117317828 clientModel/SM-G930K imsi/460071114317824 clientChannelId/qq proVersion/1.0.6',
        "Referer": "https://m.cloud.189.cn/zhuanti/2016/sign/index.jsp?albumBackupOpened=1",
        "Host": "m.cloud.189.cn",
        "Accept-Encoding": "gzip, deflate",
    }
    # 第一次抽奖
    response = s.get(url, headers=headers)
    if ("errorCode" in response.text):
        errCode = response.json()['errorCode']
        message += f"\n【1】抽奖：{errCode}"
        log.info(f"【1】抽奖：{errCode}")
    else:
        description = response.json()['prizeName']
        message += f"\n【1】抽奖：{description}"
        info4 = json.dumps(response.json(), sort_keys=True, indent=4, separators=(', ', ': '), ensure_ascii=False)
        log.info(f"【1】抽奖结果{info4}")
        log.info(f"【1】抽奖获得{description}")

    # 第二次抽奖
    response = s.get(url2, headers=headers)
    if ("errorCode" in response.text):
        errCode = response.json()['errorCode']
        message += f"\n【2】抽奖：{errCode}"
        log.info(f"【2】抽奖：{errCode}")
    else:
        description = response.json()['prizeName']
        message += f"\n【2】抽奖：{description}"
        info4 = json.dumps(response.json(), sort_keys=True, indent=4, separators=(', ', ': '), ensure_ascii=False)
        log.info(f"【2】抽奖结果{info4}")
        log.info(f"【2】抽奖获得{description}")

    # 第三次抽奖
    response = s.get(url3, headers=headers)
    if ("errorCode" in response.text):
        errCode = response.json()['errorCode']
        message += f"\n【3】抽奖：{errCode}"
        log.info(f"【3】抽奖：{errCode}")
    else:
        description = response.json()['prizeName']
        message += f"\n【3】抽奖：{description}"
        info4 = json.dumps(response.json(), sort_keys=True, indent=4, separators=(', ', ': '), ensure_ascii=False)
        log.info(f"【3】抽奖结果{info4}")
        log.info(f"【3】抽奖获得{description}")

    response = s.get(user_info_url, headers=user_info_headers)
    userinfo = response.json()
    capacity = userinfo['capacity'] / 1073741824
    available = userinfo['available'] / 1073741824
    message += "\n总共容量：%.2fG" % capacity
    message += "\n可用容量：%.2fG" % available
    log.info("总共容量：%.2fG" % capacity)
    log.info("可用容量：%.2fG" % available)
    Notify().gotify(message)


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


def login(username, password):
    url = "https://cloud.189.cn/api/portal/loginUrl.action?redirectURL=https%3A%2F%2Fcloud.189.cn%2Fweb%2Fredirect.html"
    redirect_url = "https://m.cloud.189.cn/udb/udb_login.jsp?pageId=1&pageKey=default&clientType=wap&redirectURL=https://m.cloud.189.cn/zhuanti/2021/shakeLottery/index.html"
    s = requests.Session()
    r = s.get(redirect_url)
    # 使用正则表达式匹配URL
    url_pattern = re.compile(r"https://[^\s';\"]+")
    match = url_pattern.search(r.text)
    if match:
        url = match.group()
    else:
        raise Exception("未找到匹配的URL")
    r = s.get(url)
    # 预编译正则表达式
    href_pattern = re.compile(r"<a id=\"j-tab-login-link\"[^>]*href=\"([^\"]+)\"")
    match = href_pattern.search(r.text)
    if match:
        url = match.group(1)
    else:
        raise Exception("未找到匹配的URL")
    r = s.get(url)
    captchaToken = re.findall(r"captchaToken' value='(.+?)'", r.text)[0]
    lt = re.findall(r'lt = "(.+?)"', r.text)[0]
    returnUrl = re.findall(r"returnUrl= '(.+?)'", r.text)[0]
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
    # 访问重定向url获取ck
    r = s.get(redirect_url)
    return s


# 云函数入口方法
def main_handler(event, context):
    i = 1
    # user中填入账号密码
    user = [
        {'user': '13800138000', 'pwd': 'rainerosion'},
    ]
    for u in user:
        log.info("第%s个帐号" % i)
        i += 1
        try:
            main(u['user'], u['pwd'])
        except Exception as result:
            log.error("异常%s" % result)


if __name__ == '__main__':
    main_handler(None, None)
