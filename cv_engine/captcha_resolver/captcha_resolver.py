import requests
import re

import time

from cv_engine.captcha_resolver.solve_captchas_with_model import ImageReader
from cv_engine.util.exceptions import CaptchaResolveFailException
from cv_engine.util.file_operation import check_temp_file, save_captcha_img


class CaptchaResolver():
    def __init__(self, captcha_key, cookies, retry, tmp_folder):
        self.tmp_folder = tmp_folder + '/captcha%d.jpeg' % retry
        self.img_url = 'https://www.ris.gov.tw/apply/captcha/image'
        self.captcha_key = captcha_key
        self.headers = {
            'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7,zh-CN;q=0.6',
            'Connection': 'keep-alive',
            # Default cookie for test
            'Cookie': cookies,
            'DNT': '1',
            'Host': 'www.ris.gov.tw',
            'Referer': 'https://www.ris.gov.tw/id_card/',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36'

        }

    def check_ocr_result(self, result_dict):

        captcha_code = result_dict.get('text')
        captcha_code_pattern = '[\dA-Za-z]{5}'
        filter = re.compile(captcha_code_pattern)
        if result_dict.get('conf') >= 80 and filter.match(captcha_code) is not None:
            return str.upper(captcha_code)
        else:
            return None

    def resolve(self):
        # Send request for getting image again

        reader = ImageReader()
        check_temp_file(self.tmp_folder)
        for i in range(0, 100):
            time.sleep(3)
            response = requests.get(
                self.img_url + '?CAPTCHA_KEY={captcha_key}&time={time}'.format(
                    captcha_key=self.captcha_key,
                    time=round(time.time() * 1000)),
                headers=self.headers,
                stream=True,
                verify=True)
            # print('Captcha image retrieve successfully? %s' % save_captcha_img(response, self.tmp_folder))
            if save_captcha_img(response, self.tmp_folder):
                reader_result = self.check_ocr_result(reader.solve_captcha(self.tmp_folder))
                if reader_result is not None:
                    return reader_result

        raise CaptchaResolveFailException('Confidence of captcha cant not reach to 80!')
