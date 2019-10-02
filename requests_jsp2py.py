import requests
import re    
from bs4 import BeautifulSoup  
import json
import time
import js2py
import datetime
import threading

# 用户要输入的参数
wechatSESS_ID = '4c9d54bf6023105b4383f88a0f232932'
# 全局常量
host = 'http://wechat.laixuanzuo.com'
# home_url = 'http://localhost'
home_url = 'http://wechat.laixuanzuo.com/index.php/reserve/index.html?f=wechat'
# 全局变量
session = ""
seats = []
js_url = ""

def ptime():
    while True:
        print(datetime.datetime.now().strftime("%H:%M:%S"))
        time.sleep(1)

# 进入选座系统，找出有空位的教室
def checkSeat():
    global session
    global home_url
    global seats
    global js_url
    print("正在检查座位...")
    contents = session.get(home_url)
    # print(contents.text)
    # print(contents.headers)
    # print(contents.url)
    if contents.status_code == 404 :
        exit("网络错误，请重试")
    if "请在微信客户端打开链接" in contents.text :
        exit("会话id已失效，请更新后再次开始运行程序")

    soup = BeautifulSoup(contents.text, 'html.parser')
    seat_list = soup.select("#seat_info td")[0:2]#常用座位1和2
    seats.clear()
    count = 0
    for seat in seat_list:
        print(seat)
        if not seat.has_attr('class'):#如果有class就是disabled
            print(seat, 'is empty')
            js_url = soup.select("script")[-1]['src']
            seats.append({'lib_id': seat['lib_id'], 'seat_key': seat['seat_key']})
            count +=1
        else:
            js_url = soup.select("script")[-1]['src']
            seats.append({'lib_id': seat['lib_id'], 'seat_key': seat['seat_key']})
    return count > 0
   
# 调用示例
# selectSeat('http://wechat.laixuanzuo.com/index.php/reserve/get/', 'http://static.wechat.laixuanzuo.com/template/theme2/cache/layout/2NKYhwyti4825333.js', '11065', '11,65')
def selectSeat(ajax_url, code_url, lib_id, seat_key):
    global session
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
    print("返回结果" + data.text)
    #result = session.get(data.text['url'])
    # 获取json数据
    json_data = json.loads(data.text)
    if json_data['code'] == 0:
        success_url = json.loads(data.text)['url']
        session.get(success_url)# 此处不必要保存结果

def main():    
    global host
    global home_url
    global session
    global js_url
    global seats
    # 需获取的两个参数
    global wechatSESS_ID
    global wxCode
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 5.1.1; vivo X7 Build/LMY47V; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/66.0.3359.126 MQQBrowser/6.2 TBS/044904 Mobile Safari/537.36 MMWEBID/8041 MicroMessenger/7.0.5.1440(0x27000537) Process/tools NetType/4G Language/zh_CN',
        'Cookie' : 'wechatSESS_ID=' + str(wechatSESS_ID),
        'Referer':'https://wechat.laixuanzuo.com/index.php/reserve/index.html'
    }
    session = requests.session()
    session.headers = headers

    # 发起第一次请求，用来维持会话
    checkSeat()
    # 定时
    print("开始运行程序",datetime.datetime.now().time())
    start_time = datetime.time(7,29,58,0) #7点29分58秒
    cnt = 0
    while datetime.datetime.now().time() < start_time :
        time.sleep(1)
        if cnt == 120:
            cnt = 0
            checkSeat()
        else:
            cnt += 1
    print("开始抢座位" + str(datetime.datetime.now().time()))
    print("正在检测常用座位...")
    # 每隔一秒打印一次时间
    time_thread = threading.Thread(target=ptime)
    time_thread.setDaemon(True) #设置后台线程，当主线程退出时，子线程也被强制退出
    time_thread.start()
    # 开始检测常用座位
    while not checkSeat():
        time.sleep(0.05)
        continue
    print("常用座位可选，正在抢座位...")
    for seat in seats:
        selectSeat('http://wechat.laixuanzuo.com/index.php/reserve/get/', js_url, seat['lib_id'], seat['seat_key'])
    now = time.localtime(time.time())
    print(datetime.datetime.now().strftime("%H:%M:%S"))
    print("抢座位成功！")
    time_thread.join(1)
main()
print("Exiting Main Thread")