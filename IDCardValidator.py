import json
import time

from selenium import webdriver

from Captcha_resolver.captchaResolver import CaptchaResolver

test_id = 'E123456789'
test_gen_date_twyear = 102
test_gen_date_month = 7
test_gen_date_day = 2
test_city = '高市'
test_category = '補發'

chrome_path = "./driver/chromedriver"  # chromedriver.exe執行檔所存在的路徑
target = 'https://www.ris.gov.tw/id_card/'
filePath = '/Users/motoloto/Documents/workspacePython/AccountOpeningAssistant'

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

try:
    web.get(target)
    web.set_window_position(50, 50)  # 瀏覽器位置
    web.set_window_size(800, 600)  # 瀏覽器大小

    time.sleep(2)
    web.find_element_by_id('idnum').send_keys(test_id)

    time.sleep(2)
    web.find_element_by_id('applyTWY').send_keys(test_gen_date_twyear)

    time.sleep(2)
    web.find_element_by_id('applyMM').send_keys(test_gen_date_month)

    time.sleep(2)
    web.find_element_by_id('applyDD').send_keys(test_gen_date_day)

    time.sleep(2)
    for option in web.find_element_by_id('siteId').find_elements_by_tag_name('option'):
        if test_city == option.text:
            option.click()
    for option in web.find_element_by_id('applyReason').find_elements_by_tag_name('option'):
        if test_category == option.text:
            option.click()

    time.sleep(2)
    captchaUrl = web.find_element_by_id('applyReason')

    time.sleep(2)
    captchaUrl = web.find_element_by_id('captchaImage').get_property('src')

    cookieStr = ''
    for cookie in web.get_cookies():
        cookieStr += ("%s=%s;" % (cookie['name'], cookie['value']))

    captcha_resolver = CaptchaResolver(captchaUrl, cookieStr)
    captcha_code = captcha_resolver.resolve()
    web.find_element_by_id('captchaInput').send_keys(captcha_code)

    if web.find_element_by_id('queryActionBtn').click():
        web.execute_script('window.print();')
    else:
        print('Input error.')

except:
    print('Failed')
finally:
    web.quit()
