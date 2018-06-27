import json
import random
import time
import os
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support import expected_conditions as EC
import selenium.webdriver.support.ui as ui
from selenium.webdriver.common.by import By
from cv_engine.util import file_operation as fo
from django.conf import settings

from cv_engine.captcha_resolver.captcha_resolver import CaptchaResolver


def check_error_element_exist_by_id(id):
    try:
        element = web.find_element_by_id(id)
        if element.text == '驗證碼輸入錯誤':
            return True
        else:
            return False
    except NoSuchElementException:
        return False


@csrf_exempt
def validate_id_card(request):
    global web

    payloads = json.loads(request.body.decode("utf-8"))
    re_try = 15
    sleep_period = 2

    target = 'https://www.ris.gov.tw/id_card/'
    default_file_name = '國民身分證領補換資料查詢作業.pdf'
    chrome_path = settings.BASE_DIR + "/driver/chromedriver"  # chromedriver.exe執行檔所存在的路徑

    res_list = list()
    try:

        for payload in payloads:
            res = {}

            user_id = payload['id']

            result_folder = settings.BASE_DIR + '/result/' + str(user_id)
            fo.create_result_folder_if_not_exist(result_folder)

            tmp_folder = settings.BASE_DIR + "/idcardTemp/" + str(user_id)
            fo.clean_all_temp_files(tmp_folder)

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
                'printing.print_preview_sticky_settings.appState': json.dumps(appState),
                'savefile.default_directory': tmp_folder}
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_experimental_option('prefs', profile)
            chrome_options.add_argument('--kiosk-printing')
            web = webdriver.Chrome(chrome_path, chrome_options=chrome_options)

            fo.create_result_folder_if_not_exist(tmp_folder)
            fo.clean_all_temp_files(tmp_folder)

            try:
                web.implicitly_wait(random.randint(1,3))
                web.get(target)
                web.set_window_position(50, 50)  # 瀏覽器位置
                web.set_window_size(1024, 768)  # 瀏覽器大小

                place_input_data(payload, web)

                captcha_result = False

                for i in range(0, re_try):

                    cookie_str = get_inline_cookie(web)
                    captcha_key = web.find_element_by_id('captchaKey').get_property('value')
                    captcha_resolver = CaptchaResolver(captcha_key, cookie_str, retry=i, tmp_folder=tmp_folder)
                    captcha_code = captcha_resolver.resolve()
                    if captcha_code is None: continue

                    print('captcha_code=' + captcha_code)
                    web.find_element_by_id('captchaInput').send_keys(captcha_code)

                    # this doesn't work...........don't know why.. Fuck fuck fuck
                    # web.find_element_by_xpath('//*[@id="queryActionBtn"]').click()
                    web.execute_script('document.getElementById("queryActionBtn").click()')
                    # Wait for 10 seconds, or timeout.
                    try:
                        ui.WebDriverWait(web, 10).until(
                            EC.presence_of_element_located((By.ID, "resultBlock")))
                    except TimeoutException as e:
                        print('Submit action timeout.')
                        continue

                    if not check_error_element_exist_by_id('captchaInput.errors'):
                        print('Login successfully!')
                        captcha_result = True
                        break
                    else:
                        captcha_result = False
                        print('Captcha input incorrect.')
                        continue

                time.sleep(sleep_period)
                if captcha_result:
                    web.execute_script('window.print();')
                    file_name_prefix = user_id + '-idCard-'
                    tmp_pdf = tmp_folder + '/' + default_file_name
                    result_folder = settings.BASE_DIR + '/result/' + str(user_id)
                    fo.create_result_folder_if_not_exist(result_folder)
                    os.rename(tmp_pdf,
                              result_folder + '/' + file_name_prefix + time.strftime("%Y-%m-%d",
                                                                                     time.localtime()) + '.pdf')
                    res = {
                        'id': user_id,
                        'status': 'SUCCESS',
                        'message': None
                    }
                else:
                    res = {
                        'id': user_id,
                        'status': 'FAILED',
                        'message': 'Captcha resolve failed'
                    }

            except FileNotFoundError as e:
                print('Image file not found.')
                res = {
                    'id': user_id,
                    'status': 'FAILED',
                    'message': (e.args[0] if len(e.args) >= 1 else str(e))
                }
            finally:
                res_list.append(res)
                web.quit()

        return JsonResponse(res_list, status=200, safe=False)

    except Exception as e:
        print('ID card validation failed.' + (e.args[0] if len(e.args) >= 1 else str(e)))
        return JsonResponse(None, status=500, safe=False)
    finally:
        web.quit()


def place_input_data(payload, web):
    place_id(str(payload['id']), web, sleep_period=5)
    # time.sleep(2)
    place_city(str(payload['city']), web)
    # time.sleep(2)
    place_reason(str(payload['category']), web)
    # time.sleep(2)
    place_date(str(payload['card_date']), web)


def place_reason(test_category, web):
    for option in web.find_element_by_id('applyReason').find_elements_by_tag_name('option'):
        if test_category == option.text:
            option.click()


def place_city(test_city, web):
    for option in web.find_element_by_id('siteId').find_elements_by_tag_name('option'):
        if test_city == option.text:
            option.click()


def place_id(id, web, sleep_period=1):
    time.sleep(sleep_period)
    web.find_element_by_id('idnum').send_keys(id)


def get_inline_cookie(web):
    cookie_str = ''
    for cookie in web.get_cookies():
        cookie_str += ("%s=%s;" % (cookie['name'], cookie['value']))
    return cookie_str


def place_date(date, web):
    card_date = date.split('-')
    test_gen_date_twyear = card_date[0]
    test_gen_date_month = card_date[1]
    test_gen_date_day = card_date[2]
    # time.sleep(2)
    web.find_element_by_id('applyTWY').send_keys(test_gen_date_twyear)
    # time.sleep(2)
    web.find_element_by_id('applyMM').send_keys(test_gen_date_month)
    # time.sleep(2)
    web.find_element_by_id('applyDD').send_keys(test_gen_date_day)
