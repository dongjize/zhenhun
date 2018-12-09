from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import time
from PIL import Image
from io import BytesIO
from os import listdir

USERNAME = '18239831004'
PASSWORD = 'qweqweqwe'


class CrackWeiboSlide():
    def __init__(self):
        self.url = 'https://passport.weibo.cn/signin/login'
        self.browser = webdriver.Chrome()
        self.wait = WebDriverWait(self.browser, 20)
        self.username = USERNAME
        self.password = PASSWORD

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

    # 获取所有的验证码
    def main(self):
        count = 0
        while True:
            name = str(count) + '.png'
            self.open()
            self.get_image(name)
            count += 1


if __name__ == '__main__':
    crack = CrackWeiboSlide()
    crack.main()
