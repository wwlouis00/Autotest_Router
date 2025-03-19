'''
Louis Wang Selenium Code
'''
import os
import re
import time
import logging
from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QApplication
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from os import listdir
from os.path import isfile, isdir, join
import requests
from bs4 import BeautifulSoup

dut_url = "http://www.asusrouter.com/Main_Login.asp"
dut_url_wifi = "http://www.asusrouter.com/Advanced_Wireless_Content.asp"
esg_url = "http://192.168.50.18/display"

# dut_url = "http://192.168.50.1/"
http_username = "admin"
http_password = "00000000"


logging.basicConfig(level=logging.INFO, format="[%(asctime)s - %(levelname)s] - %(message)s")
logger = logging.getLogger()

def print_msg(msg):
    logger.info(msg)

def countdown(seconds):
    for i in range(seconds, 0, -1):
        print_msg(f"倒數: {i}秒")
        time.sleep(1)  # 暫停 1 秒

def esg_number(i):
    driver.find_element("xpath", f"//*[@value=\" {i} \"]").click()
    print_msg(f"按下 '{i}' ")
    # driver.find_element("xpath", "//*[@value=\" 9 \"]").click()
    countdown(3)

def esg_fun(i):
    driver.find_element("xpath", f"//*[@value=\" {i} \"]").click()
    print_msg(f"按下 '{i}' ")
    # driver.find_element("xpath", "//*[@value=\" 9 \"]").click()
    countdown(3)

def esg_rf():
    print_msg("RF On/Off")
    countdown(3)
    driver.find_element("xpath", "//*[@value=\"  RF On/Off  \"]").click()
    countdown(3)

def dfs_channel():
    try:
        driver.get(dut_url_wifi)
        countdown(5)
        # 發送 HTTP 請求
        response = requests.get(dut_url_wifi)

        if response.status_code == 200:
            # 使用 BeautifulSoup 解析 HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 查找包含 "當前控制頻道:" 的元素
            element = soup.find(text="5 GHz").find_next(string=lambda text: "當前控制頻道" in text)
            
            if element:
            # 提取數字部分
                channel = element.split("當前控制頻道:")[-1].strip()
                print(f"5G 當前控制頻道: {channel}")
            else:
                print("未找到 5G 的當前控制頻道")
        else:
            print(f"請求失敗，狀態碼：{response.status_code}")

    except TimeoutError:
        driver.quit()

# 函式: 登入路由器
def login(driver):
    print_msg("嘗試登入路由器")
    try:
        driver.get(dut_url)
        # 找到登入框並輸入帳號和密碼
        username_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "login_username"))
        )
        username_input.send_keys(http_username)

        password_input = driver.find_element(By.NAME, "login_passwd")
        password_input.send_keys(http_password)

        # 點擊登入按鈕
        try:
            driver.find_element(By.XPATH, "//div[@onclick='login();']").click()
        except:
            driver.find_element(By.XPATH, "//div[@onclick='preLogin();']").click()
        
        print_msg("登入成功")
        countdown(3)
    except Exception as e:
        print_msg(f"登入失敗: {e}")
        driver.quit()
        exit(1)

# 函式: 提取 5G 當前控制頻道
def get_dfs_channel(driver, element_id):
    print_msg("前往 WiFi 設定頁面")
    try:
        # 導向 WiFi 設定頁
        driver.get(dut_url_wifi)
        # 等待頁面加載
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, element_id))
        )
        # 抓取指定 `span` 的文字內容
        span_element = driver.find_element(By.ID, element_id)
        channel_info = span_element.text.strip()
        print_msg(f"找到控制頻道資訊: {channel_info}")
        if channel_info:
            match = re.search(r'\d+', channel_info)
            # test_hz = int(channel_info)*5 + 5001
            if match:
                channel_number = int(match.group())
                print_msg(f"5 GHz 當前控制頻道: {channel_number}")
            else:
                print_msg("未找到數字")
                driver.quit()
        else:
            print_msg("未找到 5 GHz 的控制頻道資訊")
            driver.quit()
        return channel_number
    except Exception as e:
        print_msg(f"提取控制頻道失敗: {e}")
        driver.quit()
        return None

def open_esg_web(channel_number):
    print_msg("前往 ESG 設定頁面")
    test_hz = (channel_number * 5 + 5001) / 1000
    print_msg(f'FREQUENCY: {test_hz} GHZ')
    # 將數字轉換為字串，分解為陣列
    hz_array = [char if char == '.' else int(char) for char in str(test_hz)]
    try:
        driver.get(esg_url)
        try:
            print_msg("Preset")
            driver.find_element("xpath", "//*[@value=\"Preset\"]").click()
            countdown(3)
            print_msg("Recall")
            driver.find_element("xpath", "//*[@value=\"Recall\"]").click()
            countdown(3)
            print_msg("Select Reg")
            driver.find_element("xpath", "//*[@value=\"\/\"]").click()
            countdown(3)
            print_msg("Recall")
            driver.find_element("xpath", "//*[@onclick=\"return key(65)\"]").click()
            countdown(3)
            print_msg("輸入 FREQUENCY")
            driver.find_element("xpath", "//*[@value=\"  Freq   \"]").click()
            # 將每個陣列元素丟進 esg_fun(i)
            for item in hz_array:
                if item == ".":
                    print_msg("按下 '.'")
                    driver.find_element("xpath", "//*[@value=\" .  \"]").click()
                    countdown(3)
                    continue
                esg_fun(item)
            driver.find_element("xpath", "//*[@onclick=\"return key(65)\"]").click()
            esg_rf()
        except:
            print_msg("ESG 啟動失敗")
    except:
        print_msg("ESG啟動失敗")

if __name__ == "__main__":
    global driver
    driver = webdriver.Chrome()
    driver.maximize_window()

    try:
        login(driver)  # 登入路由器
        # 呼叫倒數函式
        countdown(3)
        # 提取 5 GHz 的控制頻道
        element_id = "5g1_current_channel"
        channel_number = get_dfs_channel(driver, element_id)
        countdown(3)
        open_esg_web(channel_number)
    finally:
        driver.quit()
        print_msg("結束程式")
