import shutil
from django.conf import settings
import os


def create_result_folder_if_not_exist(folder):
    if not os.path.exists(folder):
        os.makedirs(folder)
        print('Create result folder: %s' % folder)
    else:
        print('Result folder exist: %s' % folder)


def clean_all_temp_files(temp_folder):
    directory = os.path.dirname(temp_folder)
    if os.path.exists(directory):
        for file in os.listdir(temp_folder):
            try:
                if os.path.isfile(file):
                    os.remove(file)
                elif os.path.isdir(file):
                    shutil.rmtree(file)
            except Exception as e:
                print(e)


def check_temp_file(temp_file):
    if os.path.isfile(temp_file):
        os.remove(temp_file)


def save_captcha_img(response, path):
    if response.status_code == 200:
        with open(path, 'wb') as f:
            response.raw.decode_content = True
            shutil.copyfileobj(response.raw, f)
        return os.path.isfile(path)
    else:
        print('Failed to retrieve captcha image. Return code:' + response.status_code)
        return False
