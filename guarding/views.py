from django.shortcuts import render

import json
import os
from selenium import webdriver
import time
from django.http import JsonResponse
from cv_engine.util.file_operation import create_result_folder_if_not_exist, clean_all_temp_files
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings


@csrf_exempt
def validate_guarding(request):
    chrome_path = "./driver/chromedriver"  # chromedriver.exe執行檔所存在的路徑
    target = 'http://domestic.judicial.gov.tw/abbs/wkw/WHD9HN01.jsp'
    temp_file_path = 'guardingTemp'
    res = list()
    payloads = json.loads(request.body.decode("utf-8"))
    print(str(payloads))
    create_result_folder_if_not_exist(settings.BASE_DIR + '/result')
    create_result_folder_if_not_exist(settings.BASE_DIR + '/' + temp_file_path)
    clean_all_temp_files(settings.BASE_DIR + '/' + temp_file_path)
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
        'savefile.default_directory': temp_file_path}
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_experimental_option('prefs', profile)
    chrome_options.add_argument('--kiosk-printing')
    try:
        web = webdriver.Chrome(chrome_path, chrome_options=chrome_options)

        for payload in payloads:

            name = payload['name']
            id = payload['id']

            try:
                web.get(target)
                web.set_window_position(50, 50)  # 瀏覽器位置
                web.set_window_size(800, 600)  # 瀏覽器大小
                time.sleep(2)
                # process
                web.find_element_by_name("clnm").send_keys(name)
                web.find_element_by_name("idno").send_keys(id)
                time.sleep(1)
                web.find_element_by_name("kdid").find_elements_by_tag_name('option')[2].click()
                time.sleep(1)
                web.find_element_by_xpath(
                    '//*[@id="form"]/table/tbody/tr[2]/td/div/div[1]/center/table/tbody/tr[1]/td[2]/font/input').click()
                time.sleep(5)
                web.execute_script('window.print();')
                file_name = id + '-GUARDING-' + time.strftime("%Y-%m-%d", time.localtime()) + '.pdf'

                result_folder = settings.BASE_DIR + '/result/' + id
                create_result_folder_if_not_exist(result_folder)
                os.rename(settings.BASE_DIR + '/' + temp_file_path + '/家事事件公告.pdf'
                          , result_folder + '/' + file_name)
                res.append({
                    'id': id,
                    'status': 'SUCCESS',
                    'message': None
                })
            except Exception as e:
                print(str(e))
                res.append({
                    'id': id,
                    'status': 'FAILED',
                    'message': (e.args[0] if len(e.args) >= 1 else str(e))
                })
    except Exception as e:
        print(str(e))
        return JsonResponse(None, status=500)
    finally:
        web.quit()

    return JsonResponse(res, status=200, safe=False)

