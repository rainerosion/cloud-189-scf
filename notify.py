# 发送通知信息类
# go-cqhttp 通知机器人
# go-cqhttp使用参考
# https://docs.go-cqhttp.org/guide/quick_start.html#使用
import requests


class Notify:
    # 服务器地址
    url = f'http://localhost:5701/'
    # 使用的api接口
    group = 'send_group_msg?group_id=839483517'
    # 验证access_token
    token = 'your_access_token'
    # gotify apptoken
    gotify_app_token = 'your_app_token'
    gotify_url = 'https://gotify.rainss.cn/message?token='

    def __init__(self):
        self.sendurl = f"%s%s&access_token=%s" % (self.url, self.group, self.token)
        self.gotify_url = self.gotify_url + self.gotify_app_token

    def cqHttp(self, message):
        s = requests.Session()
        s.get(self.sendurl + "&message=" + message)

    def gotify(self, message, title="天翼云盘签到"):
        s = requests.Session()
        s.post(self.gotify_url, json={
            "message": message,
            "priority": 1,
            "title": title
        })
