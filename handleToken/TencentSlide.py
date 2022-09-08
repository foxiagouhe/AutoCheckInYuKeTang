import logging

from selenium.webdriver.support import expected_conditions as EC  # 显性等待
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import cv2 as cv
import requests
import random
import time


class TencentSlide:
    """
    识别腾讯验证码
    """

    def __init__(self, url, username, password, types, chromedrive_path=""):
        """
        初始化浏览器配置，声明变量

        :param url: 要登录的网站地址
        :param username: 账号
        :param password: 密码
        """
        # profile = webdriver.FirefoxOptions()  # 配置无头
        # profile.add_argument('-headless')
        self.options = Options()
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('disable-infobars')
        self.options.add_argument('--disable-gpu')
        self.options.add_argument('--headless')
        self.chromedrivePath = chromedrive_path
        self.types = types
        self.browser = webdriver.Chrome(executable_path=self.chromedrivePath, options=self.options) \
            if len(chromedrive_path) != 0 \
            else webdriver.Chrome(options=self.options)
        self.wait = WebDriverWait(self.browser, 20)
        self.url = url  # 目标url
        self.username = username  # 用户名
        self.password = password  # 密码

    def end(self):
        """
        结束后退出，可选

        :return:
        """
        self.browser.quit()

    def set_info(self):
        """
        填写个人信息，在子类中完成

        """
        pass

    def tx_code(self):
        """
        主要部分，函数入口

        :return:
        """
        self.set_info()

        WebDriverWait(self.browser, 20, 0.5).until(
            EC.presence_of_element_located((By.ID, 'tcaptcha_iframe')))  # 等待 iframe
        self.browser.switch_to.frame(
            self.browser.find_element_by_id('tcaptcha_iframe'))  # 加载 iframe
        time.sleep(0.5)
        bk_block = self.browser.find_element_by_xpath(
            '//img[@id="slideBg"]').get_attribute('src')
        # print(bk_block)
        logging.info("img url: " + bk_block)
        if self.save_img(bk_block):
            dex = self.get_pos()
            if dex:
                track_list = self.get_track(dex)
                time.sleep(0.5)
                slid_ing = self.browser.find_element_by_xpath(
                    '//div[@id="tcaptcha_drag_thumb"]')  # 滑块定位
                ActionChains(self.browser).click_and_hold(
                    on_element=slid_ing).perform()  # 鼠标按下
                time.sleep(0.2)
                logging.info('轨迹:' + str(track_list))
                for track in track_list:
                    ActionChains(self.browser).move_by_offset(
                        xoffset=track, yoffset=0).perform()  # 鼠标移动到距离当前位置（x,y）
                time.sleep(0.5)
                ActionChains(self.browser).release(
                    on_element=slid_ing).perform()  # print('第三步,释放鼠标')
                time.sleep(0.5)
                # 识别图片
                return True
            else:
                self.re_start()
        else:
            logging.info('缺口图片捕获失败')
            return False

    @staticmethod
    def save_img(bk_block):
        """
        保存图片

        :param bk_block: 图片url
        :return: bool类型，是否被保存
        """
        try:
            img = requests.get(bk_block).content
            with open('tx.jpeg', 'wb') as f:
                f.write(img)
            return True
        except:
            return False

    @staticmethod
    def get_pos():
        """
        识别缺口
        注意：网页上显示的图片为缩放图片，缩放 50% 所以识别坐标需要 0.5

        :return: 缺口位置
        """
        image = cv.imread('tx.jpeg')
        # 高斯滤波
        blurred = cv.GaussianBlur(image, (5, 5), 0)
        # 边缘检测
        canny = cv.Canny(blurred, 200, 400)
        # 轮廓检测
        contours, hierarchy = cv.findContours(
            canny, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        for i, contour in enumerate(contours):
            m = cv.moments(contour)
            if m['m00'] == 0:
                cx = cy = 0
            else:
                cx, cy = m['m10'] / m['m00'], m['m01'] / m['m00']
            if 6000 < cv.contourArea(contour) < 8000 and 370 < cv.arcLength(contour, True) < 390:
                if cx < 400:
                    continue
                x, y, w, h = cv.boundingRect(contour)  # 外接矩形
                cv.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)
                # cv.imshow('image', image)  # 显示识别结果
                logging.info('[缺口识别] 位置: {x}px'.format(x=x / 2))
                return x / 2
        return 0

    @staticmethod
    def get_track(distance):
        """
        轨迹方程

        :param distance: 距缺口的距离
        :return: 位移列表
        """
        distance -= 37  # 初始位置
        # 初速度
        v = 0
        # 单位时间为0.2s来统计轨迹，轨迹即0.2内的位移
        t = 0.2
        # 位移/轨迹列表，列表内的一个元素代表0.2s的位移
        tracks = []
        # 当前的位移
        current = 0
        # 到达mid值开始减速
        mid = distance * 4 / 5

        distance += 10  # 先滑过一点，最后再反着滑动回来
        # a = random.randint(1,3)
        while current < distance:
            if current < mid:
                # 加速度越小，单位时间的位移越小,模拟的轨迹就越多越详细
                a = random.randint(2, 4)  # 加速运动
                # a = 3
            else:
                a = -random.randint(3, 5)  # 减速运动
                # a = -2
            # 初速度
            v0 = v
            # 0.2秒时间内的位移
            s = v0 * t + 0.5 * a * (t ** 2)
            # 当前的位置
            current += s
            # 添加到轨迹列表
            tracks.append(round(s))

            # 速度已经达到v,该速度作为下次的初速度
            v = v0 + a * t

        # 反着滑动到大概准确位置
        for i in range(4):
            tracks.append(-random.randint(2, 3))
        for i in range(4):
            tracks.append(-random.randint(1, 3))
        return tracks

    def move_to(self, index):
        """
        移动滑块

        :param index:
        :return:
        """
        pass

    def re_start(self):
        """
        准备开始

        :return: None
        """
        self.tx_code()
        time.sleep(4)
        # self.end()
