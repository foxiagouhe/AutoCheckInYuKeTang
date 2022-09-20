import csv
import datetime
import json
import logging
import os

from selenium.common.exceptions import TimeoutException
from TencentSlide import TencentSlide as txSlide
from TencentSlide import EC
from TencentSlide import By
from selenium.webdriver.common.keys import Keys
import time
import requests
import requests.cookies


class YuKeTang(txSlide):
    """
    Tencent的子类，完成set_info()函数
    """

    def set_info(self):
        """
        填写表单信息

        :return: None
        """
        self.browser.get(url=self.url)
        try:
            self.browser.find_element_by_css_selector('.changeImg').click()

            if self.types == "E":
                self.browser.find_element_by_css_selector('[data-type=email]').click()  # email
                input_elem = self.browser.find_element_by_css_selector('[type=email][name=loginname]')  # email
                pwd_elem = self.browser.find_elements_by_css_selector('[name=password]')[1]  # 0: phone; 1: email
            elif self.types == "PP":
                self.browser.find_element_by_css_selector('[data-type=phone]').click()  # phone
                input_elem = self.browser.find_element_by_css_selector('[type=mobile][name=loginname]')  # phone
                pwd_elem = self.browser.find_elements_by_css_selector('[name=password]')[0]  # 0: phone; 1: email
            else:
                raise "Some element not found!"

            input_elem.clear()
            pwd_elem.clear()

            input_elem.send_keys(self.username)
            pwd_elem.send_keys(self.password)
            pwd_elem.send_keys(Keys.ENTER)


        except TimeoutException as e:
            print('Error:', e.args)
            self.set_info()

    def get_cookie(self) -> dict:
        dictCookies: list = self.browser.get_cookies()
        for i in dictCookies:
            if i.get('name', None) == 'sessionid':
                return i

    def saveData(self):
        result = {}
        cookie_dict = self.get_cookie()
        logging.info("get cookie success")
        cookieJar = requests.cookies.RequestsCookieJar()
        cookieJar.set(name=cookie_dict['name'], value=cookie_dict['value'])
        res = requests.get(url="https://changjiang.yuketang.cn/v2/api/web/userinfo", cookies=cookieJar).json()
        try:
            result['name'] = res['data'][0]['name']
            result['user_id'] = res['data'][0]['user_id']
            result['cookie'] = cookie_dict
        except KeyError as e:
            result['name'] = None
            result['user_id'] = None
            result['cookie'] = None
        return result


if __name__ == '__main__':
    startTime = time.time()
    url = 'https://changjiang.yuketang.cn/web'
    path = os.path.abspath(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    if not os.path.exists(path=path + '/log/' + str(datetime.date.today())):
        os.makedirs(name=path + '/log/' + str(datetime.date.today()))

    logging.getLogger().setLevel(logging.INFO)
    logging.basicConfig(
        filename=path + '/log/' + str(datetime.date.today()) + '/' + 'handleToken-' +
                 time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime(time.time())) + ".log",
        format="%(asctime)s - %(filename)s - %(levelname)s:%(message)s",
        level=logging.INFO,
        filemode='w',
        datefmt="%Y-%m-%d %I:%M:%S")
    logging.info("script start up\n")

    logging.info("start time: " + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(startTime)))
    logging.info("loading user csv")
    with open(path + '/data/user.csv') as f:
        user_data_list = []
        user_data_csv_list = [x for x in csv.DictReader(f)]
        logging.info("read csv finished, start execute all user")
        while len(user_data_csv_list) > 0:
            try:
                user = user_data_csv_list.pop()
                logging.info("now execute user: " + user['name'])
                tencent = YuKeTang(url, user['user'], user['pwd'], user['type'])
                tencent.re_start()
                user_data_json = tencent.saveData()
                user_data_json['apikey'] = user['apikey']
                user_data_list.append(user_data_json)
                tencent.end()
                logging.info("user " + user['name'] + ' execute success')
                logging.info('sleep 1 min')
                time.sleep(60)
            except Exception:
                logging.info("user " + user['name'] + ' execute failed')
                user_data_csv_list.insert(0, user)
                tencent.end()
                logging.info('sleep 1 min')
                time.sleep(60)

    with open(path + "/data/user_data.json", 'w') as f:
        json.dump(user_data_list, f, ensure_ascii=False)
    endTime = time.time()
    logging.info("end time: " + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(endTime)))
    logging.info("total run time(s): " + str(endTime - startTime))
