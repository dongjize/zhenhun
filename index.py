from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
import time
from PIL import Image
from io import BytesIO
from os import listdir

import tkinter as tk
from tkinter import filedialog


class CrackWeiboSlide:
    def __init__(self, username, password):
        self.url = 'https://passport.weibo.cn/signin/login'
        self.browser = webdriver.Chrome()
        self.wait = WebDriverWait(self.browser, 20)
        self.username = username
        self.password = password

    def __del__(self):
        self.browser.close()

    def open(self):
        """
        打开网页输入用户名密码登录
        :return: None
        """
        self.browser.get(self.url)
        username = self.wait.until(EC.presence_of_element_located((By.ID, 'loginName')))
        password = self.wait.until(EC.presence_of_element_located((By.ID, 'loginPassword')))
        submit = self.wait.until(EC.element_to_be_clickable((By.ID, 'loginAction')))
        username.send_keys(self.username)
        password.send_keys(self.password)
        submit.click()

    def get_position(self):
        """
        获取验证码的位置
        :return: 位置
        """
        try:
            img = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'patt-shadow')))
        except TimeoutException:
            print('未出现验证码')
            self.open()
        time.sleep(2)
        location = img.location
        size = img.size
        top = location['y']
        bottom = location['y'] + size['height']
        left = location['x']
        right = location['x'] + size['width']
        return (top, bottom, left, right)

    def get_screenshot(self):
        """
        获取截图
        :return:截图
        """
        screentshot = self.browser.get_screenshot_as_png()
        # BytesIO将网页截图转换成二进制
        screentshot = Image.open(BytesIO(screentshot))
        return screentshot

    def get_image(self, name):
        """获取验证码图片"""
        top, bottom, left, right = self.get_position()
        print('验证码位置', top, bottom, left, right)
        screenshot = self.get_screenshot()
        # crop()将图片裁剪出来,后面需要一个参数
        captcha = screenshot.crop((left, top, right, bottom))
        captcha.save(name)
        return captcha

    def detect_image(self, image):
        """
        匹配图片
        :param self:
        :param image: 图片
        :return: 拖动顺序
        """
        # 图片所在的文件夹
        for template_name in listdir('templates/'):
            print('正在匹配', template_name)
            template = Image.open('templates/' + template_name)
            # 匹配图片
            if self.same_img(image, template):
                # 将匹配到的文件名转换为列表
                numbers = [int(number) for number in list(template_name.split('.')[0])]
                print('拖动顺序', numbers)
                return numbers
        return [1, 2, 3, 4]

    def is_pixel_equal(self, image1, image2, x, y):
        """
        判断两个像素的相似度
        :param image1: 图片1
        :param image2: 图片2
        :param x: 位置x
        :param y: 位置y
        :return: 像素是否相同
        """
        # 取像素点
        pixel1 = image1.load()[x, y]
        pixel2 = image2.load()[x, y]
        # 偏差量等于60
        threshold = 60
        if abs(pixel1[0] - pixel2[0]) < threshold and abs(pixel1[1] - pixel2[1]) < threshold and abs(
                pixel1[2] - pixel2[2]) < threshold:
            return True
        else:
            return False

    def same_img(self, image, template):
        """
        识别相似的验证码
        :param image: 准备识别的验证码
        :param template: 模板
        :return:
        """
        # 相似度阈值
        threshold = 0.992
        count = 0
        # 匹配所有像素点
        for x in range(image.width):
            for y in range(image.height):
                # 判断像素
                if self.is_pixel_equal(image, template, x, y):
                    count += 1
        result = float(count) / (image.width * image.height)
        if result > threshold:
            print('成功匹配')
            return True
        return False

    def move(self, numbers):
        """
        根据顺序拖动,此处接收的参数为前面的验证码的顺序列表
        :param numbers:
        :return:
        """
        # 获取四宫格的四个点
        circles = self.browser.find_elements_by_css_selector('.patt-wrap .patt-circ')
        print('-----------------', circles)
        dx = dy = 0
        for index in range(4):
            circle = circles[numbers[index] - 1]
            if index == 0:
                # 点击第一个点
                ActionChains(self.browser).move_to_element_with_offset(circle, circle.size['width'] / 2, circle.size[
                    'height'] / 2).click_and_hold().perform()
            else:
                # 慢慢移动
                times = 30
                for i in range(times):
                    ActionChains(self.browser).move_by_offset(dx / times, dy / times).perform()
                    time.sleep(1 / times)
            if index == 3:
                # 松开鼠标
                ActionChains(self.browser).release().perform()
            else:
                # 计算下次的偏移
                dx = circles[numbers[index + 1] - 1].location['x'] - circle.location['x']
                dy = circles[numbers[index + 1] - 1].location['y'] - circle.location['y']

    def crack(self):
        """
        破解入口
        :return:
        """
        self.open()
        # 获取验证码图片
        image = self.get_image('captcha.png')
        numbers = self.detect_image(image)
        self.move(numbers)
        time.sleep(10)
        print('识别结束')

        self.browser.get(
            "http://m.weibo.cn/p/index?containerid=231219_3015_votemore_1001&luicode=10000011&lfid=231219_3015_newartificial_1001")

        btn_vote = self.wait.until(EC.presence_of_element_located((By.XPATH,
                                                                   '//*[@id="app"]/div[1]/div[2]/div[2]/div/div/div[3]/div/div/div[1]')))
        btn_vote.click()
        print("点赞成功")


if __name__ == '__main__':
    root = tk.Tk()
    root.withdraw()

    file_path = filedialog.askopenfilename()
    while not str(file_path).endswith(".txt"):
        file_path = filedialog.askopenfilename()

    f_accounts = open(file_path, "r")
    accounts = f_accounts.readlines()

    # f_posts = open("posts.txt", "rb")
    # posts = f_posts.readlines()

    i = 1000  # 每个用户每天只能投票10次
    while i > 0:
        i -= 1
        for line in accounts:
            strs = line.split("----")
            username, password = strs[0], strs[1]
            print(username, password)
            crack = CrackWeiboSlide(username, password)
            crack.crack()
