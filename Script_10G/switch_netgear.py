#encoding: utf-8
import os
import sys
import time
import ctypes
import shutil
# import common
import selenium
import threading
import subprocess
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from os import listdir
from os.path import isfile, isdir, join
from datetime import datetime
from multiprocessing import Process
from signal import signal
from signal import SIGTERM



http_password = "Asus#1234"
dut_url = "http://192.168.1.11/"

adv_8021q_url = dut_url + "iss/specific/Cf8021q.html?Gambit=mkfjffjfefjjfciffcobfjjjjfefggififjg"

index_url = dut_url+"index.asp"
adv_wan_url = dut_url+ "Advanced_WAN_Content.asp"
adv_wan_port_url =  dut_url+ "Advanced_WANPort_Content.asp"
adv_sys_url =  dut_url+ "Advanced_System_Content.asp"
adv_fw_url =  dut_url+ "Advanced_FirmwareUpgrade_Content.asp"
analysis_url =  dut_url+ "Main_Analysis_Content.asp"
aiportection_url =  dut_url+ "AiProtection_HomeProtection.asp"
qos_url =dut_url+ "QoS_EZQoS.asp"
reset_default_url =  dut_url+ "Advanced_SettingBackup_Content.asp"
disable_redirect_url =  dut_url+ "Main_Login.asp?redirect=false"

''' 
default : portImage remImg
tag : portImage        tagImg
Untag: portImage  untImg
'''

target_states = {
    "1": "remImg",
    "5": "remImg",  # 編號5對應狀態untImg
    "7": "remImg"  # 編號7對應狀態tagImg
}

tag_port = {
    "1": "tagImg",
    "5": "tagImg",  # 編號5對應狀態untImg
    "7": "tagImg" 
}
untag_port = {
    "1": "untImg",
    "5": "untImg",  # 編號5對應狀態untImg
    "7": "untImg" 
}

def print_msg(msg):
    print(msg)
    l_file = open(log_file, "a")
    l_file.write(msg)
    l_file.write('\n')
    l_file.close()


def Get_Key_From_Value(d, val):
    print('Get_Key_From_Value: %s, %s' %(d, val))
    for key, value in d.items():
        #print('%s, %s' %(key, value))
        if value.upper().replace(' ','_').replace('-','_') == val.upper().replace(' ','_').replace('-','_'):
            return key


def Ping(address, retry, success):
    #print('ping ' + address + '=')
    #return True
    i = 0
    ok = 0
    if len(address) == 0:
        msg = 'No IP, stop ping\n'
        print_msg(msg)
    else:
        cmd = 'ping -n 1 ' + address
        print_msg(cmd)
        while (i < retry):
            try:
                output = subprocess.check_output(cmd)
                #print(output)
                if b'TTL=' in output:
                    ok += 1
                    msg="PING OK"
                    #print_msg(msg)
                else:
                    msg="FAIL"
                    print_msg(msg)
                if ok == success:
                    msg="Ping Success"
                    print_msg(msg)
                    return True
            except subprocess.CalledProcessError as e:
                code = e.returncode
                msg="Ping Error! Re-send again. [ERROR NO]: " + str(code)
                print_msg(msg)
            i += 1
            time.sleep(1)

    return False


def query_chrome_driver_version():
    cmd = 'ChromeDriver -V'
    stdout, stderr = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               shell=True).communicate()
    stdoutput = stdout.decode()
    return stdoutput.split(' ')[1]

		
def browser_driver_version_check():
    chrome_driver_version = query_chrome_driver_version()
    print('Chrome driver version : << {} >>'.format(chrome_driver_version))

    try:
        browser = webdriver.Chrome()
    except selenium.common.exceptions.SessionNotCreatedException as e:
        err_msg = e.msg.split('\n')[1]
        print_msg(err_msg)
        version = e.msg.split('\n')[1].split('with')[0]
        print_msg(version)
        return version
    try:
        msg='Browser version : '+ browser.capabilities['version']
        print(msg)
    except KeyError:
        msg='Browser version : ' + browser.capabilities['browserVersion']
        print(msg)
        browser.quit()

    return 'OK'
      
    
def Try_Login(driver):
    print_msg("Try to login")
    try:
        element1 = driver.find_element("xpath", "//*[@id=\"Password\"]")
        sleep(1)
        if element1:
            print_msg("Find Password")
            element1 = driver.find_element("xpath", "//*[@id=\"Password\"]")
            element1.send_keys(http_password);
            sleep(1)
            try:
                driver.find_element("xpath", "//*[@id=\"button_Login\"]").click()
            except:
                print_msg("Can not click Login button.")
                
            sleep(1)
    except:
        print_msg("Do not need login.")
    
    #printf("OK")

# 定義檢查並點擊的函數
def check_and_click_button(member, target_state):
    xpath_check = f'.//div[contains(@class, "portImage") and contains(@class, "{target_state}")]'

    # 初始狀態檢查
    def check_state():
        try:
            port_image = member.find_element(By.XPATH, xpath_check)
            return True
        except:
            return False
    
    # 如果初始狀態已經符合目標狀態，則直接打印並返回
    if check_state():
        print(f"Port {member}已經包含 {target_state}，無需點擊！")
        return

    # 點擊並檢查直到達到目標狀態
    while not check_state():
        print_msg(f"Port {member}未包含 {target_state}，點擊並重試...")
        # 點擊按鈕
        member.click()
        print_msg(f"成功點擊按鈕，等待狀態更新...")
        time.sleep(1)  # 等待狀態更新

        if check_state():  # 確認是否達到目標狀態
            print_msg(f"Port {member} 成功切換為 {target_state}！")
        else:
            print_msg(f"Port {member} 未成功切換為 {target_state}！")
            continue  # 若未達到目標狀態，繼續點擊
    print_msg("切換成功")

# # VLAN_ID, tag_port, untag_port
# # 2, 1, 3
# # 3, 15, 21
def Set_VLAN(VLAN_ID, tag_port, untag_port):
    try:
        select = Select(driver.find_element("xpath", "//*[@id=\"vlanIdOption\"]"))
        sleep(1)
    except:
        print_msg("Can not find select element: VLAN_ID")

    try:
        select.select_by_index(VLAN_ID)
        print_msg(f"Select VID {VLAN_ID}")
        sleep(1)
    except:
        print_msg(f"Can not select VID {VLAN_ID}")
        sleep(15)
    
    try:
        # tag
        for number, tag_port in tag_port.items():
            # 根據編號定位到對應的 portMember 元素
            xpath_member = f'//div[@class="portMember margin"]//span[text()="{number}"]/..'
            member = driver.find_element(By.XPATH, xpath_member)

            # 呼叫檢查並點擊函數
            check_and_click_button(member, tag_port)
        # untag
        for number, untag_port in untag_port.items():
            # 根據編號定位到對應的 portMember 元素
            xpath_member = f'//div[@class="portMember margin"]//span[text()="{number}"]/..'
            member = driver.find_element(By.XPATH, untag_port)

            # 呼叫檢查並點擊函數
            check_and_click_button(member, tag_port)
    except Exception as e:
        print(f"發生錯誤: {e}")

def Set_VLAN():
    try:
        for number, target_state in target_states.items():
            # 根據編號定位到對應的 portMember 元素
            xpath_member = f'//div[@class="portMember margin"]//span[text()="{number}"]/..'
            member = driver.find_element(By.XPATH, xpath_member)

            # 呼叫檢查並點擊函數
            check_and_click_button(member, target_state)
    except Exception as e:
        print(f"發生錯誤: {e}")

    
def Get_Value(f_lines, keyword):
    ret = ""
    
    for line in f_lines:
        if keyword in line:
            line_2 = line.replace('\n','')
            splitStr = line_2.split('=')
            ret = splitStr[1]
            break
    #print(ret)
    return ret


def main():
    driver.get(dut_url)
    sleep(1)
    move = driver.find_element(By.TAG_NAME, 'body')
    move.send_keys(Keys.CONTROL + Keys.HOME)
    
    Try_Login(driver)

    try:
        element1 = driver.find_element("xpath", "//*[@id=\"VLAN\"]")
        element1.click()
        print_msg("Click 'VLAN'")
        sleep(1)
    except:
        print_msg("Cannot click 'VLAN'. Stop test.")
        sleep(5)
        return
    
    try:
        element1 = driver.find_element("xpath", "//*[@id=\"VLAN_802.1Q\"]")
        element1.click()
        print_msg("Click '802.1Q'")
        sleep(1)
    except:
        print_msg("Cannot click '802.1Q'. Stop test.")
        sleep(5)
        return    

    try:
        element1 = driver.find_element("xpath", "//*[@id=\"f2\"]")
        element1.click()
        print_msg("Click 'Advanced'")
        sleep(1)
    except:
        print_msg("Cannot click 'Advanced'. Stop test.")
        sleep(5)
        return

    try:
        element1 = driver.find_element("xpath", "/html/body/table/tbody/tr[7]/td/table/tbody/tr/td[1]/table/tbody/tr/td/div/div[3]/div[2]/a/span")
        element1.click()
        print_msg("Click 'VLAN config'")
        sleep(3)
    except:
        print_msg("Cannot click 'VLAN'. Stop test.")
        sleep(30)
        return

    try:
        element1 = driver.find_element("xpath", "/html/body/table/tbody/tr[7]/td/table/tbody/tr/td[1]/table/tbody/tr/td/div/div[4]/div[2]/a/span")
        element1.click()
        print_msg("Click 'VLAN membership'")
        sleep(3)
    except:
        print_msg("Cannot click 'VLAN'. Stop test.")
        sleep(30)
        return

    driver.switch_to.frame('maincontent')
    print_msg("Switch to frame")

#vlanIdOption
#//*[@id="vlanIdOption"]
    # try:
    #     select = Select(driver.find_element("xpath", "//*[@id=\"vlanIdOption\"]"))
    #     sleep(1)
    # except:
    #     print_msg("Can not find select element: VLAN_ID")

    # try:
    #     select.select_by_index(2)
    #     print_msg("Select VID 2")
    #     sleep(1)
    # except:
    #     print_msg("Can not select VID 2")
    #     sleep(15)

    try:
        Set_VLAN()
        # Set_VLAN(1, tag_port, untag_port)
        # Set_VLAN(2, tag_port, untag_port)
    except:
        print_msg("執行失敗")
    finally:
        driver.quit()
   
    # #//*[@id="unit1"]/div[6]/div
    # try:
    #     element1 = driver.find_element("xpath", "//*[@id=\"unit1\"]/div[6]/div")
    #     print_msg("Find ports 11")
    #     sleep(3)
    # except:
    #     print_msg("Cant Find ports 11")
    #     sleep(30)
    #     return

    # driver.switch_to.default_content()
    try:
        element1 = driver.find_element("xpath", "//*[@id=\"btn_Apply\"]")
        element1.click()
        print_msg("Click 'Apply'")
        sleep(30)
    except:
        print_msg("Cannot click 'Apply'. Stop test.")
        sleep(15)
        driver.quit()
    return
        
    '''
    try:
        element1 = driver.find_element("xpath", "/html/body/table/tbody/tr[7]/td/table/tbody/tr/td[1]/table/tbody/tr/td/div/div[5]/div[2]/a/span")
        element1.click()
        print_msg("Click 'VID'")
        sleep(3)
    except:
        print_msg("Cannot click 'VLAN'. Stop test.")
        sleep(30)
        return
    '''
    '''
    # Locate the "Enable" radio button using XPath or a different locator strategy
    enable_radio_button = driver.find_element(By.XPATH, "//input[@type='radio' and @value='Enable' and @name='status']")

    # Check if the "Enable" radio button is selected
    is_selected = enable_radio_button.is_selected()

    # Print the result
    if is_selected:
        print("The 'Enable' radio button is selected.")
    else:
        print("The 'Enable' radio button is not selected.")

    # Close the WebDriver (optional, if you want to close the browser)
    driver.quit()

    try:
        # Locate the "Enable" radio button using XPath or a different locator strategy
        enable_radio_button = driver.find_element(By.XPATH, "//input[@type='radio' and @value='Enable' and @name='status']")

        # Click the "Enable" radio button
        enable_radio_button.click()

        print_msg("Click 'Enable'")
        sleep(1)

        try:
            alert = driver.switch_to.alert    
            msg = ("alert:" + alert.text)
            print_msg(msg)
            alert.accept()
        except:
            print_msg("No alert")
        try:
            element1 = driver.find_element("xpath", "//*[@id=\"btn_Apply\"]")
            element1.click()
            print_msg("Click 'Apply'")
            sleep(1)
        except:
            print_msg("Cannot click 'Apply'. Stop test.")
            sleep(5)
            driver.quit()
            return
    except:
        print_msg("Cannot click 'Enable'. Stop test.")
        sleep(5)
        driver.quit()
        return
    '''
    
if __name__ == "__main__":
    now = datetime.now()
    now_time = now.strftime("%Y-%m-%d-%H-%M")
    cur_directory = os.getcwd()
    log_file = cur_directory +'\\process.log'
    # chrome_chk_ret = browser_driver_version_check()

    # if chrome_chk_ret != 'OK':
    #     chrome_driver_version = query_chrome_driver_version()
    #     warn_msg = ('Chromedriver version is %s' %(chrome_driver_version))
    #     print_msg(warn_msg)
    #     warn_msg = chrome_chk_ret + '\nPlease go to \"https://chromedriver.chromium.org/\" & download new chromedriver.'
    #     print_msg(warn_msg)
    #     sleep(15)
    # else:
    driver = webdriver.Chrome()
    driver.maximize_window()
    main()
