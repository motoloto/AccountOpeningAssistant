import requests
import shutil
import os

from Captcha_resolver.solve_captchas_with_model import ImageReader


class CaptchaResolver():
    def __init__(self, img_url, cookies):
        self.temp_file = 'captcha.jpeg'
        self.img_url = img_url
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

    def resolve(self):
        # Send request for getting image again
        self.check_temp_file(self.temp_file)
        response = requests.get(
            self.img_url,
            headers=self.headers,
            stream=True,
            verify=False)
        print('Captcha image retrieve successfully? %d' % self.save_captcha_img(response, self.temp_file))
        reader = ImageReader()

        return reader.solve_captcha(self.temp_file)

    def check_temp_file(self, temp_file):
        if os.path.isfile(temp_file):
            print('Clean temp file.')
            os.remove(temp_file)

    def save_captcha_img(self, response, path):
        if response.status_code == 200:
            with open(path, 'wb') as f:
                response.raw.decode_content = True
                shutil.copyfileobj(response.raw, f)
            return os.path.isfile(path)
        else:
            print('Failed to retrieve captcha image. Return code:' + response.status_code)
            return False
