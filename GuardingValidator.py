import json
import os
from selenium import webdriver
import time

chrome_path = "./driver/chromedriver"  # chromedriver.exe執行檔所存在的路徑
target = 'http://domestic.judicial.gov.tw/abbs/wkw/WHD9HN01.jsp'
filePath = '/Users/motoloto/Documents/workspacePython/AccountOpeningAssistant'

name_for_check = 'XXX'

appState = {
    "recentDestinations": [
        {
            "id": "Save as PDF",
            "origin": "local"
        }
    ],
    "selectedDestinationId": "Save as PDF",
    "version": 2
}

profile = {
    'printing.print_preview_sticky_settings.appState': json.dumps(appState), 'savefile.default_directory': filePath}
chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option('prefs', profile)
chrome_options.add_argument('--kiosk-printing')
web = webdriver.Chrome(chrome_path, chrome_options=chrome_options)

web.get(target)
web.set_window_position(50, 50)  # 瀏覽器位置
web.set_window_size(800, 600)  # 瀏覽器大小

time.sleep(2)

# process
web.find_element_by_name("clnm").send_keys(name_for_check)
time.sleep(1)
web.find_element_by_name("kdid").find_elements_by_tag_name('option')[2].click()
time.sleep(1)
web.find_element_by_xpath('//*[@id="form"]/table/tbody/tr[2]/td/div/div[1]/center/table/tbody/tr[1]/td[2]/font/input').click()
web.execute_script('window.print();')

file_name = name_for_check + time.strftime("%Y-%m-%d",time.localtime())+'.pdf'
os.rename(filePath+'/家事事件公告.pdf', filePath+'/result/'+file_name)
print(web)
web.quit()
