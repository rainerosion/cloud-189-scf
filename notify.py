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

    def __init__(self):
        self.sendurl = f"%s%s&access_token=%s" % (self.url, self.group, self.token)

    def sendMessage(self, message):
        s = requests.Session()
        s.get(self.sendurl + "&message=" + message)