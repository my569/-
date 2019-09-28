import requests    
import re    
from bs4 import BeautifulSoup  
import json  
import time
import js2py

host = 'http://wechat.laixuanzuo.com'
home_url = 'http://wechat.laixuanzuo.com/index.php/reserve/index.html?f=wechat'
session = ""
seats = []
js_url = ""

class seat_class(object):
    def __init__(self, lib_id, seat_key):
        self.lib_id = lib_id
        self.seat_key = seat_key

# 进入选座系统，找出有空位的教室
def step1(debug=False):
    global session
    global home_url
    global seats
    global js_url
    
    contents = session.get(home_url)
    if contents.status_code == 404 :
        exit("网络错误，请重试")
    if "请在微信客户端打开链接" in contents.text :
        exit("会话id已失效，请更新后再次开始运行程序")

    soup = BeautifulSoup(contents.text, 'html.parser')
    seat_list = soup.select("#seat_info td")[0:2]#常用座位1和2
    seats.clear()
    count = 0
    for seat in seat_list:
        if seat.has_attr('class') and 'disabled' not in seat['class']:
            js_url = soup.select("script")[-1]['src']
            count +=1
        else:
            js_url = soup.select("script")[-1]['src']
            seats.append({'lib_id': seat['lib_id'], 'seat_key': seat['seat_key']})
    return count > 0
        
def selectSeat(ajax_url, code_url, lib_id, seat_key):
    global session
    #selectSeat('http://wechat.laixuanzuo.com/index.php/reserve/get/', 'http://static.wechat.laixuanzuo.com/template/theme2/cache/layout/2NKYhwyti4825333.js', '11065', '11,65')
    # 获取js脚本
    js = requests.get(code_url)
    # 替换js
    js_str = re.sub(r'T\.ajax_get\(AJAX_URL\+', 'return (', js.text)
    js_str = re.sub(r'"&yzm="\+t.+', '"&yzm=")};', js_str)
    # 运行js
    context_js_obj = js2py.EvalJs()
    context_js_obj.execute(js_str)
    # 拼接url
    seat_url = context_js_obj.reserve_seat(str(lib_id),str(seat_key))
    seat_url = str(ajax_url) + str(seat_url)
    # 发起抢座请求
    data = session.get(seat_url)
    #result = session.get(data.text['url'])
    # 获取json数据中的url
    print("返回结果" + data.text)
    success_url = json.loads(data.text)['url']
    result = session.get(success_url)
    print(result.text)

def main():    
    global host
    global home_url
    global session
    global js_url
    global seats
    
    debug = True
    
    headers = {    
        'User-Agent': 'Mozilla/5.0 (Linux; Android 5.1.1; vivo X7 Build/LMY47V; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/66.0.3359.126 MQQBrowser/6.2 TBS/044904 Mobile Safari/537.36 MMWEBID/8041 MicroMessenger/7.0.5.1440(0x27000537) Process/tools NetType/4G Language/zh_CN',
        'Cookie' : 'wechatSESS_ID=06bce7eae6fb3cfe398aef951ff48b8c'
    }
    session = requests.session()
    session.headers = headers

    finish = False
    print("开始检测常用座位...")
    while not step1(debug):
        now = time.localtime(time.time())
        if now.tm_sec >= 55 or now.tm_sec <= 5:
            print(now.tm_hour, ":", now.tm_min)
        continue
    for seat in seats:
        selectSeat('http://wechat.laixuanzuo.com/index.php/reserve/get/', js_url, seat['lib_id'], seat['seat_key'])
main()