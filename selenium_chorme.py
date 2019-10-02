from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import inspect

#my_classroom = [i for i in range(0,15)]
my_classroom = [3]                          # 选择的教室
my_seat = [str(i) for i in range(40,50)]    # 选择的位置


cookies = [
    {
        'name': 'wechatSESS_ID',
        'value': '153f48cbf3b5b400ca0909ef25dac39f', #变量
    }
]

host = 'http://wechat.laixuanzuo.com'
home_url = 'http://wechat.laixuanzuo.com/index.php/reserve/index.html?f=wechat'

    
# 浏览器标识
options = webdriver.ChromeOptions()
options.add_argument('--user-agent="Mozilla/5.0 (Linux; Android 5.1.1; vivo X7 Build/LMY47V; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/66.0.3359.126 MQQdriver/6.2 TBS/044904 Mobile Safari/537.36 MMWEBID/8041 MicroMessenger/7.0.5.1440(0x27000537) Process/tools NetType/4G Language/zh_CN"')
# 打开浏览器
driver = webdriver.Chrome(chrome_options=options)
driver.get(host)
# 设置cookies
for cookie in cookies:
    driver.add_cookie(cookie)

# 访问首页
driver.execute_script('window.location = "' + home_url + '";')
windows = driver.window_handles
home = windows[-1]
# 设置隐藏等待
driver.implicitly_wait(10) # seconds

def isMychoose(i):
    if i not in my_classroom:
        print("教室" + str(i) + "不是我的常用教室")
        return False
    else:
        print("教室" + str(i) + "是我的常用教室")
        return True
    
def isAvail(i):
    msg = driver.execute_script("return document.getElementsByClassName('list-group-item')[" + str(i) + "].innerText")
    #print(msg)
    if 'disabled' in driver.execute_script("return document.getElementsByClassName('list-group-item')[" + str(i) +"].classList"):
        print("教室" + str(i) + "未开放")
        return False
    elif '已满' in msg :
        print("教室" + str(i) + "已满")
        return False
    else:
        print("教室" + str(i) + "有空位")
        return True

def run(driver, i):
    # 等待一下元素
    driver.find_elements(By.CLASS_NAME, 'grid_1')
    driver.find_element(By.ID, 'select_btn')
    time.sleep(1)
    driver.execute_script(r"document.getElementsByClassName('grid_1')[" + str(i) + "].addEventListener('click', function (ev) { var _this = $(this); cur_checked = _this; $('#seat_checked_label').html($(this).text() + ' 号座位');})")
    #扫描选择的座位
    len = driver.execute_script(r"return document.getElementsByClassName('grid_1').length")
    print('教室%d有%d个空位' %(i,len))
    for i in range(len):
        seat = driver.execute_script(r"return document.getElementsByClassName('grid_1')[" + str(i) + "].innerText")
        if seat in my_seat:
            driver.execute_script(r"document.getElementsByClassName('grid_1')[" + str(i) + "].click()")
            driver.execute_script(r"document.getElementById('select_btn').click()")
            # 等待一下元素
            element = WebDriverWait(driver, 10).until(driver.execute_script(r"return document.getElementById('ti_tips') != null"))
            # driver.find_element(By.ID, 'ti_tips')
            # time.sleep(1)
            result = driver.execute_script(r"return document.getElementById('ti_tips').innerText")
            print(result)
            if result == '选座成功':
                return True
            else :
                continue
                
                
    print('所选座位无空位，正在抢其它位置')
    #抢其他座位
    len = driver.execute_script(r"return document.getElementsByClassName('grid_1').length")
    for i in range(len):
        driver.execute_script(r"document.getElementsByClassName('grid_1')[" + str(i) + "].click()")
        driver.execute_script(r"document.getElementById('select_btn').click()")
        # 等待一下元素
        # element = WebDriverWait(driver, 10).until(driver.execute_script(r"return document.getElementById('ti_tips') != null"))
        driver.find_element(By.ID, 'ti_tips')
        # time.sleep(1)
        if '选座成功' == driver.execute_script(r"return document.getElementById('ti_tips').innerText"):
            print('选座成功')
            return True
        else :
            print('选座失败，继续选座')
            continue
    return False

isFinish = False
while not isFinish :
    print("%d:%d %d" %(time.localtime(time.time()).tm_hour, time.localtime(time.time()).tm_min, time.localtime(time.time()).tm_sec))
    if time.localtime(time.time()).tm_hour != 7:
        time.sleep(20)
    else:
        time.sleep(1)

    driver.switch_to.window(home)
    driver.refresh()
    time.sleep(1)
    
    frequent_seats = driver.find_elements(By.CSS_SELECTOR, '#seat_info > tbody > tr td')
    if len(frequent_seats) == 0:
        driver.execute_script('window.location = "' + home_url + '";')
        time.sleep(1)
        continue
    
    count = 0
    for i in range(len(frequent_seats)-1):
        if driver.execute_script("return !document.querySelectorAll('#seat_info > tbody > tr td')[" + str(i) + "].classList.contains('disabled')") :
            count = count + 1
            driver.execute_script("document.querySelectorAll('#seat_info > tbody > tr td')[0].click()")
            # 等待一下元素
            # WebDriverWait(driver, 10).until(driver.execute_script(r"return document.getElementById('ti_tips') != null"))
            driver.find_element(By.ID, 'ti_tips')
            if '选座成功' == driver.execute_script(r"return document.getElementById('ti_tips').innerText"):
                print('选座成功')
                isFinish = True
            else :
                print('选座失败，继续选座')
                continue
    print("--->常用座位空闲数为:" + str(count))
    if isFinish:
        break
            
    all_elements = driver.find_elements(By.CLASS_NAME,'list-group-item')
    avail_urls = []
    for i in range(len(all_elements)):
        if isAvail(i) and isMychoose(i):
            sub_url = driver.execute_script("return document.getElementsByClassName('list-group-item')[" + str(i) + "].getAttribute('data-url')")
            avail_urls.append(host+sub_url)
    print("--->空闲教室数为:" + str(len(avail_urls)))
    print("-----------------------------")

    for i in range(len(avail_urls)):
        driver.execute_script('window.open("' + avail_urls[i] + '");')
        windows = driver.window_handles
        driver.switch_to.window(windows[-1])
        CommonTasks.waitForPageLoad(dirver);
        if run(driver, i) :
            isFinish = True
            time.sleep(10)
            break