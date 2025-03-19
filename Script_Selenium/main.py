'''
Louis Wang Selenium Code
'''
import os
import qis
import sys
import time
import ctypes
import shutil
import psutil
import common
import win32api
import selenium
import threading
import subprocess
import url
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
import zipfile
log_file = ''
LOG_FILE = "log/test.log"
autorun_path = 'autorun.txt'
run_qis = 0
# Argument
version = "1.0.0.14"
location = "Taipei"
chariot_pair_no= "10"
dut_ip = "192.168.50.1"
http_username = "admin"
http_password = "00000000"
ppp_username = "asus"
ppp_password = "asus#1234"
fw_version = ""
dut_wan_ip = "192.168.2.10"
wan_1_dut_wan_ip = "192.168.2.10"
wan_pc_1_wan_server_ip = "192.168.101.11"
wan_pc_1_netmask = "255.255.255.0"
wan_pc_1_gateway = "192.168.101.11"
wan_pc_1_ppp_server_ip = '101.0.0.11'
wan_2_dut_wan_ip = "192.168.2.10"
wan_pc_2_wan_server_ip = "192.168.102.12"
wan_pc_2_netmask = "255.255.255.0"
wan_pc_2_gateway = "192.168.102.12"
wan_pc_2_ppp_server_ip = '102.0.0.11'
wan_3_dut_wan_ip = "192.168.2.10"
wan_pc_3_wan_server_ip = "192.168.103.13"
wan_pc_3_netmask = "255.255.255.0"
wan_pc_3_gateway = "192.168.103.13"
wan_pc_3_ppp_server_ip = '103.0.0.11'

all_port_no = 5
UI_lan_port_list = []
UI_wan_port_list = []
test_lan_port_list = []
connect_dict = {}
wan_type_list = ["","Static IP","PPPoE","PPTP","L2TP"]
#wan_type_list = ["","Static IP","PPPoE","","L2TP"]
function_list = ['Default','AiProtection','Adaptive_QoS','Traditional_QoS']
#function_list = ['Default','','','']
function = 'Default'
UI_start = 0
model_name = ''
test_time = '1'
run_chariot = '1'
specify_lan_port_test = 0
cur_directory = 'D:\Multi-port_V5'
#config_path = 'D:\Multi-port\Config'
TPT = []
now_time = ''
log_file = ''
result_file = ''
run_qis = 0
ping_lan_client_fail = 0
autorun_path = 'autorun.txt'
sync_report = 0

CHROMEDRIVER_FOLDER = "chromedriver"
CHROMEDRIVER_FILE_test = "chromedriver-win64/chromedriver.exe"
dut_url = "http://www.asusrouter.com/"

# dut_url = "http://192.168.50.1/"
qis_url = dut_url + "QIS_wizard.htm"
index_url = dut_url+"index.asp"
adv_wan_port_url =  dut_url+ "Advanced_WANPort_Content.asp"
adv_sys_url =  dut_url+ "Advanced_System_Content.asp"
adv_fw_url =  dut_url+ "Advanced_FirmwareUpgrade_Content.asp"
analysis_url =  dut_url+ "Main_Analysis_Content.asp"
aiportection_url =  dut_url+ "AiProtection_HomeProtection.asp"
aiportection_web_url =  dut_url+ "AiProtection_WebProtector.asp"
guest_network_url = dut_url+ "Guest_network.asp"
reset_default_url =  dut_url+ "Advanced_SettingBackup_Content.asp"
traffic_url = dut_url + "TrafficAnalyzer_Statistic.asp"

cloud_url = dut_url + "cloud_main.asp"
disable_redirect_url =  dut_url+ "Main_Login.asp?redirect=false"


# Initialize logger
logging.basicConfig(level=logging.INFO, format="[%(asctime)s - %(levelname)s] - %(message)s")
logger = logging.getLogger()

function_list = ['Default','AiProtection','Adaptive_QoS','Traditional_QoS']

def print_msg(msg):
    logger.info(msg)
    # l_file = open(log_file, "a")
    # l_file.write(msg)
    # l_file.write('\n')
    # l_file.close()
    # os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    # with open(LOG_FILE, "a") as log_file:
    #     log_file.write(msg + "\n")

def countdown(seconds):
    for i in range(seconds, 0, -1):
        print_msg(f"倒數: {i}秒")
        time.sleep(1)  # 暫停 1 秒

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

# def get_latest_chromedriver_version():
#     """Fetch the latest ChromeDriver version."""
#     url = "https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json"
#     response = requests.get(url)
#     if response.status_code == 200:
#         data = response.json()
#         return data["channels"]["Stable"]["version"], data["channels"]["Stable"]["downloads"]["chromedriver"]
#     else:
#         raise Exception("Unable to fetch the latest ChromeDriver version.")

# def download_chromedriver(logger,download_url, download_path=CHROMEDRIVER_FOLDER):
#     """Download the ChromeDriver."""
#     if not os.path.exists(download_path):
#         os.makedirs(download_path)

#     file_name = os.path.join(download_path, download_url.split("/")[-1])

#     logger.info(f"Downloading ChromeDriver: {download_url}")
#     response = requests.get(download_url, stream=True)
#     if response.status_code == 200:
#         with open(file_name, 'wb') as file:
#             for chunk in response.iter_content(chunk_size=1024):
#                 file.write(chunk)
#         logger.info(f"ChromeDriver downloaded to: {file_name}")
#     else:
#         raise Exception("Failed to download ChromeDriver.")

#     return file_name

# def extract_chromedriver(logger,file_path, extract_to=CHROMEDRIVER_FOLDER):
#     """Extract the downloaded ChromeDriver."""
#     if file_path.endswith(".zip"):
#         with zipfile.ZipFile(file_path, 'r') as zip_ref:
#             zip_ref.extractall(extract_to)
#         logger.info(f"ChromeDriver extracted to: {extract_to}")
#         # Delete the zip file after extraction
#         os.remove(file_path)
#         logger.info(f"Deleted ChromeDriver zip file: {file_path}")
#     else:
#         raise Exception("Only ZIP files are supported for extraction.")

# def replace_chromedriver(logger,directory):
#     """Replace ChromeDriver in the specified directory."""
#     try:
#         version, downloads = get_latest_chromedriver_version()
#         logger.info(f"Latest ChromeDriver version: {version}")

#         platform = os.name
#         if platform == "nt":
#             driver_info = next(item for item in downloads if "win64" in item["url"])
#         elif platform == "posix" and os.uname().sysname == "Linux":
#             driver_info = next(item for item in downloads if "linux64" in item["url"])
#         elif platform == "posix" and os.uname().sysname == "Darwin":
#             driver_info = next(item for item in downloads if "mac-x64" in item["url"])
#         else:
#             raise Exception("Unsupported platform.")

#         download_url = driver_info["url"]
#         downloaded_file = download_chromedriver(logger,download_url)
#         extract_chromedriver(logger,downloaded_file)

#         logger.info("Checking and replacing ChromeDriver in directory.")
#         logger.info("Replacing ChromeDriver in specified directories...")

#         return version
#     except Exception as e:
#         logger.error(f"Error occurred while replacing ChromeDriver: {e}")

# def query_chrome_driver_version():
#     directory = os.getcwd()
#     version = replace_chromedriver(logger,directory)
#     return version

# def browser_driver_version_check(logger):
#     chrome_driver_version = query_chrome_driver_version()
#     cmd = 'ChromeDriver -V'
#     stdout, stderr = subprocess.Popen(cmd, stdout=subprocess.PIPE,
#                                stderr=subprocess.PIPE,
#                                shell=True).communicate()
#     stdoutput = stdout.decode()
#     logger.info('stdoutput')
#     logger.info(f'Chrome driver version : << {chrome_driver_version} >>')

#     try:
#         browser = webdriver.Chrome()
#     except selenium.common.exceptions.SessionNotCreatedException as e:
#         err_msg = e.msg.split('\n')[1]
#         print_msg(err_msg)
#         version = e.msg.split('\n')[1].split('with')[0]
#         print_msg(version)
#         return version
#     try:
#         msg='Browser version : '+ browser.capabilities['version']
#         logger.info(msg)
#     except KeyError:
#         msg='Browser version : ' + browser.capabilities['browserVersion']
#         logger.info(msg)
#         browser.quit()

    return 'OK'
def Try_Login():
    """
    Function to perform login operation on the ASUS router web interface.
    """
    print_msg("Try to Login")
    try:
        element1 = driver.find_element("xpath", "//*[@id=\"login_username\"]")
        if element1:
            print_msg("Find login_username")
            element1 = driver.find_element("xpath", "//*[@id=\"login_username\"]")
            element1.send_keys(http_username);
            element2 = driver.find_element("xpath", "//*[@name=\"login_passwd\"]")
            element2.send_keys(http_password);
            try:
                driver.find_element("xpath", "//div[@onclick=\"login();\"]").click()
            except:
                print_msg("Do not find login(); try preLogin();")
                try:
                    driver.find_element("xpath", "//div[@onclick=\"preLogin();\"]").click()
                except:
                    print_msg("Can not find Login element!")
                
            countdown(3)
    except:
        print_msg("Do not need login.")
    # try:
    #     # driver.get(dut_url)
    #     # driver.get("http://www.asusrouter.com/Main_Login.asp")
    #     # 找到登入框並輸入帳號和密碼
    #     username_input = WebDriverWait(driver, 10).until(
    #         EC.presence_of_element_located((By.ID, "login_username"))
    #     )
    #     username_input.send_keys(http_username)

    #     password_input = driver.find_element(By.NAME, "login_passwd")
    #     password_input.send_keys(http_password)

    #     # 點擊登入按鈕
    #     try:
    #         driver.find_element(By.XPATH, "//div[@onclick='login();']").click()
    #     except:
    #         driver.find_element(By.XPATH, "//div[@onclick='preLogin();']").click()
        
    #     print_msg("登入成功")
    # except:
    #     logging.info("Do not need login.")
'''
Qos Test
'''
def Enable_QoS(qos_type):
    driver.get(url.qos_url)
    msg = ("Enable_QoS: %s" %(qos_type))
    print_msg(msg)
    for i in range(5):
        try:
            driver.get(url.qos_url)
            countdown(3)
            move = driver.find_element(By.TAG_NAME, 'body')
            move.send_keys(Keys.CONTROL + Keys.HOME)
            print_msg("Open qos_url OK")
            break
        except:
            print_msg("Connection refuce, wait 30sec & try ")
            countdown(30)

    Try_Login()
    try:
        iframe = driver.find_element("xpath", "//iframe[@id=\"settingsWindow\"]")
        print_msg("Expert UI")
        driver.switch_to.frame(iframe)
    except:
        print_msg("Normal/ROG UI")
    # Check if QoS has been enabled or not. If enabled, don't click again.
    try:
        element = driver.find_element("xpath", "//*[@id=\"iphone_switch\"]")
        element.click()        
        connect_dict(3)
        print_msg("Click 'Enable QoS' to ON!")
    except:
        print_msg("Do not find QoS switch")

    if qos_type == "Adaptive_QoS":
        print_msg("Adaptive_QoS")
        try:
            driver.find_element("xpath", "//*[@id=\"int_type\"]").click()
            time.sleep(3)

            try:
                btn = driver.find_element("xpath", "//*[@id=\"Web_act\"]")
                print_msg("\"Web accelerate\" has been enabled.")
            except:
                print_msg("pass")
                time.sleep(1)

            try:
                btn = driver.find_element("xpath", "//*[@id=\"Web\"]")
                btn.click()
                print_msg("Click \"Web accelerate\".")
                time.sleep(1)
            except:
                print_msg("Do not find @id=\"Web\"")

            try:
                driver.find_element("xpath", "//div[@onclick=\"submitQoS();\"]").click()
                time.sleep(1)
            except:
                print_msg("Do not find submitQoS()")

            time.sleep(30)
        except:
            msg = ("Do not find Adaptive_QoS button!")
            print_msg(msg)

    if qos_type == "Traditional_QoS":
        driver.find_element("xpath", "//*[@id=\"trad_type\"]").click()
        element = driver.find_element("xpath", "//*[@id=\"obw\"]")
        element.clear()
        element.send_keys("12000")
        element = driver.find_element("xpath", "//*[@id=\"ibw\"]")
        element.clear()
        element.send_keys("12000")
        countdown(1)
        driver.find_element("xpath", "//div[@onclick=\"submitQoS();\"]").click()
        try:
            alert = driver.switch_to.alert    
            msg = ("alert:" + alert.text)
            print_msg(msg)
            alert.accept()
        except:
            print_msg("No alert")
        # time.sleep(120)
        countdown(120)

    msg = ("Enable_QoS: %s done." %(qos_type))
    print_msg(msg)


def Disable_QoS():
    # for i in range(5):
    #     try:
    #         driver.get(qos_url)
    #         countdown(3)
    #         move = driver.find_element(By.TAG_NAME, 'body')
    #         move.send_keys(Keys.CONTROL + Keys.HOME)
    #         print_msg("Open qos_url OK")
    #         break
    #     except:
    #         print_msg("Connection refuce, wait 30sec & try ")
    #         countdown(30)

    # Try_Login()
    # try:
    #     iframe = driver.find_element("xpath", "//iframe[@id=\"settingsWindow\"]")
    #     print_msg("Expert UI")
    #     driver.switch_to.frame(iframe)
    # except:
    #     print_msg("Normal/ROG UI")
    # try:
    #     element = driver.find_element("xpath", "//*[@id=\"int_type\"]")
    #     countdown(1)
    #     print_msg("QoS had been enabled!")
    #     driver.find_element("xpath", "//*[@id=\"iphone_switch\"]").click()
    #     countdown(5)
    #     driver.find_element("xpath", "//div[@onclick=\"submitQoS();\"]").click()
    #     countdown(20)
    #     print_msg("Disable_QoS done.")
    # except:
    #     print_msg("QoS already disabled.")

    print_msg("網頁瀏覽歷史")
    try:
        driver.get(url.qos_webhistory_url)
        countdown(1)
        print_msg("On / OFF")
        driver.find_element("xpath", "//*[@id=\"iphone_switch\"]").click()
        countdown(30)
        print_msg("更新")
        driver.find_element("xpath", "//input[@onclick=\"getWebHistory(document.form.clientList.value, '1')\"]").click()
        countdown(1)
        print_msg("清除")
        driver.find_element("xpath", "//input[@onclick=\"httpApi.cleanLog('web_history', updateWebHistory);\"]").click()
        countdown(10)
        print_msg("匯出")
        driver.find_element("xpath", "//input[@onclick=\"exportWebHistoryLog()\"]").click()
        print_msg("On / OFF")
        driver.find_element("xpath", "//*[@id=\"iphone_switch\"]").click()
        countdown(30)
    except:
        print_msg("QoS already disabled.")

def LAN():
    '''
    Set_Lan_Type
    '''
    print_msg("LAN")
    try:
        driver.get(url.adv_dhcp_url)
        time.sleep(1)
        driver.find_element("xpath", "//input[@onclick=\"applyRule();\"]").click()
        print_msg("Find applyRule")

    except TimeoutError:
        driver.quit()

    time.sleep(6)


def index():
    driver.get(index_url)
    try:
        countdown(1)
        print_msg("網際網路狀態")
        driver.find_element("xpath", "//*[@id=\"iconInternet\"]").click()
        countdown(1)
        print_msg("無線安全層級")
        driver.find_element("xpath", "//*[@id=\"iconRouter\"]").click()
        countdown(1)
        print_msg("用戶數")
        driver.find_element("xpath", "//*[@id=\"iconClient\"]").click()
        countdown(1)
        print_msg("AIMesh節點")
        driver.find_element("xpath", "//*[@id=\"iconAMesh\"]").click()
        countdown(1)
    except TimeoutError:
        driver.quit()

def AIMesh(driver):
    print_msg("AiMesh")
    try:
        driver.get(url.aimesh_url)
        countdown(2)
        driver.find_element("xpath", "//div[@onclick=\"control_category_block('network')\"]").click()
        print_msg("network")
        countdown(2)
        driver.find_element("xpath", "//div[@onclick=\"control_category_block('manage')\"]").click()
        print_msg("manage")

    except TimeoutError:
        driver.quit()

def guest(driver):
    print_msg("訪客網路")
    driver.get(guest_network_url)
    try:
        time.sleep(2)
        driver.find_element("xpath", "//div[@onclick=\"create_guest_unit(0,1);\"]").click()
        print("2.4 G 啟用")
        time.sleep(2)
        driver.find_element("xpath", "//div[@onclick=\"guest_divctrl(0);\"]").click()
        print("取消")
        time.sleep(2)
        driver.find_element("xpath", "//div[@onclick=\"create_guest_unit(0,2);\"]").click()
        print("2.4 G 啟用")
        time.sleep(2)
        driver.find_element("xpath", "//div[@onclick=\"guest_divctrl(0);\"]").click()
        print("取消")
        driver.find_element("xpath", "//div[@onclick=\"enable_amazon_wss(0,2);\"]").click()
        print("Amazon WiFi Simple Setup")
        driver.find_element("xpath", "//div[@onclick=\"Cancel_amazon_wss();\"]").click()
        print("取消")
        driver.find_element("xpath", "//div[@onclick=\"create_guest_unit(0,3);\"]").click()
        print("2.4 G 啟用")
        time.sleep(2)
        driver.find_element("xpath", "//div[@onclick=\"guest_divctrl(0);\"]").click()
        print("取消")

    except TimeoutError:
        driver.quit()
    time.sleep(5)
    
def qis_wizard():
    print_msg("網路設定精靈")
    try:
        driver.get(url.qis_url)
        countdown(2)
        driver.find_element("xpath", "//div[@onclick=\"apply.welcome();\"]").click()
        countdown(2)
        driver.find_element("xpath", "//div[@onclick=\"apply.wireless();\"]").click()
        countdown(50)
    except:
        print_msg("Connection refuce, wait 30sec & try ")
        countdown(30)


def WAN():
    '''
    Set_Wan_Type
    '''
    wan_server_ip = ""
    dut_wan_ip = ""
    netmask = ""
    gateway = ""
    ppp_server_ip = ""
    driver.get(url.adv_wan_url)
    # adv_wan_url
    try:
        time.sleep(1)
        element1 = driver.find_element("xpath", "//*[@id=\"wan_ipaddr_x\"]")
        element1.clear()
        element1.send_keys(dut_wan_ip);
    except:
        element1 = driver.find_element("xpath", "//input[@name=\"wan_ipaddr_x\"]")
        element1.clear()
        element1.send_keys(dut_wan_ip); 
    element2 = driver.find_element("xpath", "//input[@name=\"wan_netmask_x\"]") 
    element2.clear()
    element2.send_keys(netmask);
    try:
        element3 = driver.find_element("xpath", "//*[@id=\"wan_gateway_x\"]")
        element3.clear()
        element3.send_keys(gateway);
    except:
        element3 = driver.find_element("xpath", "//input[@name=\"wan_gateway_x\"]")
        element3.clear()
        element3.send_keys(gateway);
    time.sleep(1)
    #DNS setting
    try:    
        element = driver.find_element("xpath", "//input[@onclick=\"Assign_DNS_service()\"]")
        element.click()
        print_msg("Find Assign DNS button")
        print_msg("sleep 3sec")
        time.sleep(3)
        
        manual_retry = 0
        while(1):
            try:
                manual_btn = driver.find_element("xpath", "//*[@id=\"dns_manual\"]")
                manual_btn.click()
                print_msg("Find manual btn, break")
                break
            except:
                print_msg("can not find manual btn, try again")
                manual_retry += 1
                if manual_retry == 3:
                    print_msg("can not find manual btn 3 times, stop")
                    break
        time.sleep(1)
        print_msg("Click dns_manual")
        element = driver.find_element("xpath", "//*[@id=\"edit_wan_dns1_x\"]")
        element.clear()
        print_msg("Clean wan_dns1")
        time.sleep(1)
        element.send_keys("8.8.8.8");
        time.sleep(1)
        print_msg("key in 8.8.8.8")
        driver.find_element("xpath", "//input[@onclick=\"Update_DNS_service()\"]").click()
        print_msg("apply")
    except:
        print_msg("Normal DNS")
        try:
            element = driver.find_element("xpath", "//input[@name=\"wan_dnsenable_x\" and @value=\"0\"]")
            element.click()
            time.sleep(1)
        except:
            print_msg("No wan_dnsenable_x radio")
        element = driver.find_element("xpath", "//input[@name=\"wan_dns1_x\"]")
        element.clear()
        element.send_keys(wan_server_ip);
    time.sleep(60)
    print_msg('Config WAN type = Static IP')

def Disable_Redirect():
    print("Disable_Redirect")

    for i in range(5):
        try:
            driver.get(url.disable_redirect_url)
            countdown(3)
            move = driver.find_element(By.TAG_NAME, 'body')
            move.send_keys(Keys.CONTROL + Keys.HOME)
            print_msg("Open disable_redirect_url OK")
            break
        except:
            print_msg("Connection refuce, wait 30sec & try ")
            countdown(30)
            
    #sleep(1)
    #Try_Login(driver)
    #element1 = driver.find_element("xpath", "//*[@id=\"login_username\"]")
    
    try:
        element1 = driver.find_element("xpath", "//*[@id=\"login_username\"]")
        if element1:
            print_msg("Try to login")
            element1 = driver.find_element("xpath", "//*[@id=\"login_username\"]")
            element1.send_keys(http_username);
            element2 = driver.find_element("xpath", "//*[@name=\"login_passwd\"]")
            element2.send_keys(http_password);
            try:
                driver.find_element("xpath", "//div[@onclick=\"login();\"]").click()
            except:
                print_msg("Do not find login(); try to preLogin();")
                try:
                    driver.find_element("xpath", "//div[@onclick=\"preLogin();\"]").click()
                except:
                    print_msg("Can not find Login element!")
                
            time.sleep(3)
    except:
        print("Do not need login.")
        
    print("Disable OK")

def Enable_Telnet(driver):
    print_msg("Enable_Telnet")

    for i in range(5):
        try:
            driver.get(url.adv_sys_url)
            time.sleep(3)
            move = driver.find_element(By.TAG_NAME, 'body')
            move.send_keys(Keys.CONTROL + Keys.HOME)
            print_msg("Open adv_sys_url OK")
            break
        except:
            print_msg("Connection refuce, wait 30sec & try ")
            time.sleep(30)
    
    Try_Login(driver)
    try:
        iframe = driver.find_element("xpath", "//iframe[@id=\"settingsWindow\"]")
        print_msg("Expert UI")
        driver.switch_to.frame(iframe)
    except:
        print_msg("Normal/ROG UI")
        
    try:
        iframe = driver.find_element("xpath", "//iframe[@id=\"settingsWindow\"]")
        print("Expert UI")
        driver.switch_to.frame(iframe)
        print("switch_to.frame")
    except:
        print("Normal/ROG UI")
        
    driver.find_element("xpath", "//*[@id=\"telnetd_sshd_table\"]/tbody/tr[1]/td/input[1]").click()
    driver.find_element("xpath", "//input[@onclick=\"applyRule();\"]").click()
    time.sleep(10)


def delete_folder_contents(folder_path):
    if os.path.isdir(folder_path):
        # Loop through all items in the directory
        for item in os.listdir(folder_path):
            item_path = os.path.join(folder_path, item)
            # If it's a directory, use rmtree to delete it
            if os.path.isdir(item_path):
                shutil.rmtree(item_path)
            # If it's a file, use os.remove to delete it
            else:
                os.remove(item_path)
    else:
        print(f"The path {folder_path} is not a directory.")

def Run_QIS():
    print("Run QIS")
    qis_outputs_path = cur_directory + "\\AutoSetQIS\\outputs\\"
    qis_outputs_file = qis_outputs_path + "Set_QIS.txt"
    
    delete_folder_contents(qis_outputs_path)
    win32api.ShellExecute(0,"open","RunQIS.bat","", "", 1)
    check = 0
    while(check < 30):
        print("check: " + qis_outputs_file)
        if os.path.isfile(qis_outputs_file):
            f = open(qis_outputs_file)
            lines = f.readlines()
            if "PASS" in lines:
                return True
            else:
                return False
        else:
            print("wait 30 sec")
            time.sleep(30)
    print("Auto QIS has no result more tan 15 mins. Return False")
    return False

# def Reset_CAP():
#     msg=('Reset CAP - %s' % (cap_ip))
#     print_msg(msg)
    
#     msg=('Reset CAP - %s' % (cap_ip))
#     print_msg(msg)
    # if common.Get_Cookie(cap_ip, admin_token):
    #     command = 'curl -s -A "asusrouter-Windows-ATE-2.0.0.1" -e "%s" -b savecookie.txt -d "{\\\"action_mode\\\":\\\"Restore\\\"}" http://%s/applyapp.cgi' % (cap_ip, cap_ip)
    #     result = send_curl_command(command)
    #     msg=('Sleep 150 sec')
    #     print_msg(msg)
    #     time.sleep(150)
    # else:
    #     print_msg("Reset CAP Fail!")

def Enable_Aiportection():
    print_msg("Enable_Aiportection.")
    for i in range(5):
        try:
            driver.get(url.aiportection_url)
            countdown(3)
            move = driver.find_element(By.TAG_NAME, 'body')
            move.send_keys(Keys.CONTROL + Keys.HOME)
            print_msg("Open aiportection_url OK")
            break
        except:
            print_msg("Connection refuce, wait 30sec & try ")
            countdown(30)

    Try_Login()
    try:
        iframe = driver.find_element("xpath", "//iframe[@id=\"settingsWindow\"]")
        print_msg("Expert UI")
        driver.switch_to.frame(iframe)
    except:
        print_msg("Normal/ROG UI")

    retry = 0
    while retry < 3:
        try:
            element = driver.find_element("xpath", "//*[@id=\"mals_shade\"]")
            style = element.get_attribute("style")
            print_msg("------")
            print(style)
            print_msg("------")
            break
        except:
            print_msg("Not find 'mals_shade', try again.")
            countdown(5)
            retry += 1
    
    if "none;" not in style:
        print_msg("Try to click Enable")
        btn = driver.find_element("xpath", "//*[@id=\"iphone_switch\"]")
        btn.click()
        countdown(2)
        
        try:
            policy_model = driver.find_element("xpath", "//*[@id=\"policy_popup_modal\"]")
            print_msg("Find EULA field")
            countdown(1)
            policy_model2 = driver.find_element(By.CSS_SELECTOR, "div[class='modal-footer']")
            print_msg("Find footer")
            countdown(1)
            btn = policy_model.find_element(By.CSS_SELECTOR, ".btn.btn-primary.agree")
            print_msg("Find EULA BUTTON")
        except:
            print_msg("Not find EULA apply button.")
        print_msg("Enable_Aiportection done.")
    else:
        print_msg("Already enable")

def Disable_Aiportection():
    print_msg("Disable_Aiportection.")
    for i in range(5):
        try:
            driver.get(url.aiportection_url)
            countdown(3)
            move = driver.find_element(By.TAG_NAME, 'body')
            move.send_keys(Keys.CONTROL + Keys.HOME)
            print_msg("Open aiportection_url OK")
            break
        except:
            print_msg("Connection refuce, wait 30sec & try ")
            countdown(30)
    Try_Login()
    try:
        iframe = driver.find_element("xpath", "//iframe[@id=\"settingsWindow\"]")
        print_msg("Expert UI")
        driver.switch_to.frame(iframe)
    except:
        print_msg("Normal/ROG UI")

    retry = 0
    while retry < 3:
        try:
            element = driver.find_element("xpath", "//*[@id=\"mals_shade\"]")
            style = element.get_attribute("style")
            print_msg("------")
            print(style)
            print_msg("------")
            break
        except:
            print_msg("Not find 'mals_shade', try again.")
            countdown(5)
            retry += 1

    if "none" in style:
        driver.find_element("xpath", "//*[@id=\"iphone_switch\"]").click()      
        countdown(5)
        print_msg("Disable_Aiportection done.")

def web_protector():
    print_msg("家長電腦控制程式")
    try:
        driver.get(url.aiportection_web_url)
        print("Try to click Enable")
        btn = driver.find_element("xpath", "//*[@id=\"iphone_switch\"]")
        btn.click()
        countdown(15)
        btn = driver.find_element("xpath", "//*[@id=\"iphone_switch\"]")
        btn.click()
        countdown(20)
    except:
        print_msg("Connection refuce, wait 30sec & try ")
        countdown(30)



# def Disable_QoS(driver):
#     for i in range(5):
#         try:
#             driver.get(url.qos_url)
#             time.sleep(3)
#             move = driver.find_element(By.TAG_NAME, 'body')
#             move.send_keys(Keys.CONTROL + Keys.HOME)
#             print_msg("Open qos_url OK")
#             break
#         except:
#             print_msg("Connection refuce, wait 30sec & try ")
#             time.sleep(30)
    
#     Try_Login(driver)

#     try:
#         iframe = driver.find_element("xpath", "//iframe[@id=\"settingsWindow\"]")
#         print_msg("Expert UI")
#         driver.switch_to.frame(iframe)
#     except:
#         print_msg("Normal/ROG UI")
    
#     try:
#         element = driver.find_element("xpath", "//*[@id=\"int_type\"]")
#         time.sleep(1)
#         msg = ("QoS had been enabled!")
#         print_msg(msg)
#         element = driver.find_element("xpath", "//*[@id=\"iphone_switch\"]")
#         element.click()
#         time.sleep(1)
#         driver.find_element("xpath", "//div[@onclick=\"submitQoS();\"]").click()
#         time.sleep(20)
#         print_msg("Disable_QoS done.")
#     except:
#         print_msg("QoS already disabled.")



def traffic(driver):
    print_msg("Traffic Analyzer流量分析")
    try:
        driver.get("http://www.asusrouter.com/TrafficAnalyzer_Statistic.asp")
        countdown(2)
        btn = driver.find_element("xpath", "//*[@id=\"iphone_switch\"]")
        btn.click()
        countdown(20)
        btn = driver.find_element("xpath", "//*[@id=\"iphone_switch\"]")
        btn.click()
        countdown(30)
        # driver.find_element("xpath", "//div[@onclick=\"switch_content(this);\"]").click()
    except:
        print_msg("失敗")

def usb():
    print_msg("USB相關應用")
    try:
        driver.get(url.usb_url)
        countdown(2)
        print_msg("AiDisk")
        # driver.find_element("xpath", "//*[@id=\"Aidisk_png\"]")
        driver.find_element("xpath", "//div[@onclick=\"location.href='aidisk.asp';\"]").click()
        countdown(2)
        print_msg("回上一頁")
        driver.find_element("xpath", "//div[@onclick=\"go_setting_parent('/APP_Installation.asp')\"]").click()
        countdown(5)
    except:
        print_msg("失敗")

def cloud():
    print_msg("AiCloud 2.0 個人雲2.0應用")
    try:
        driver.get(url.aicloud_url)
        countdown(2)
        print_msg("Try to click Enable")
        btn = driver.find_element("xpath", "//*[@id=\"iphone_switch\"]")
        btn.click()
        countdown(10)
        btn = driver.find_element("xpath", "//*[@id=\"iphone_switch\"]")
        btn.click()
        countdown(10)
    except:
        print_msg("失敗")

def wireless():
    print_msg("無線網路")
    try:
        for test_url in url.wireless_urls:
            driver.get(test_url)
            countdown(1)
    except:
        print_msg("失敗")

def lan_content(driver):
    print_msg("區域網路")
    try:
        for test_url in url.lan_urls:
            driver.get(test_url)
            countdown(1)
    except:
        print_msg("失敗")

def wan_content(driver):
    print_msg("廣域網路")
    try:
        driver.get(url.adv_wan_url)
        countdown(2)
    except:
        print_msg("失敗")

def Smart_Home_Alexa(driver):
    print_msg("廣域網路")
    try:
        driver.get("http://www.asusrouter.com/Advanced_Smart_Home_Alexa.asp")
        countdown(2)
    except:
        print_msg("失敗")

def vpn():
    print_msg("VPN")
    try:
        driver.get(url.vpn_url)
        countdown(1)
    except:
        print_msg("失敗")
def firewall():
    print_msg("防火牆")
    try:
        for test_url in url.firewall_urls:
            driver.get(test_url)
            countdown(1)
    except:
        print_msg("失敗")

def administration():
    print_msg("系統管理")
    print_msg("政策")
    try:
        driver.get(url.administration_urls[5])
        print_msg("讀取")
        countdown(1)
        driver.find_element(By.XPATH, "//*[@onclick=\"show_policy('EULA');\"]").click()
        print_msg("確定")
        driver.find_element(By.XPATH, "//*[@class=\"btn btn-primary btn-block close\"]").click()
        # for test_url in url.administration_urls:
        #     driver.get(test_url)
        #     countdown(1)
    except:
        print_msg("失敗")

def system_log():
    # for test_url in url.system_log_urls:
    #     driver.get(test_url)
    #     countdown(1)
    print_msg("系統紀錄")
    print_msg("一般記錄檔")
    try:
        driver.get(url.system_log_urls[0])
        countdown(1)
        print_msg("清除")
        driver.find_element(By.XPATH, "//*[@onclick=\"onSubmitCtrl(this, ' Clear ')\"]").click()
        countdown(3)
        print_msg("儲存")
        driver.find_element(By.XPATH, "//*[@onclick=\"onSubmitCtrl(this, ' Save ');\"]").click()
        countdown(3)
    except:
        print_msg("失敗")

    print_msg("無線使用者")
    try:
        driver.get(url.system_log_urls[1])
        countdown(1)
        print_msg("更新")
        driver.find_element(By.XPATH, "//*[@onclick=\"location.reload();\"]").click()
    except:
        print_msg("失敗")

    print_msg("DHCP租約")
    try:
        driver.get(url.system_log_urls[2])
        countdown(1)
        print_msg("更新")
        driver.find_element(By.XPATH, "//*[@onclick=\"location.reload();\"]").click()
    except:
        print_msg("失敗")

    print_msg("IPv6")
    try:
        driver.get(url.system_log_urls[3])
        countdown(1)
        print_msg("更新")
        driver.find_element(By.XPATH, "//*[@onclick=\"location.reload();\"]").click()
    except:
        print_msg("失敗")



def network_tool():
    print_msg("網路工具")
    try:
        print_msg("Netstat")
        driver.get(url.net_tool_urls[1])
        countdown(1)
        driver.find_element("xpath", "//*[@id=\"cmdBtn\"]").click()
        # for test_url in url.net_tool_urls:
        #     driver.get(test_url)
        #     countdown(1)
    except:
        print_msg("失敗")

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

def Load_General_Config():

    global http_username
    global http_password
    global ppp_username
    global ppp_password    

    global wan_1_dut_wan_ip
    global wan_pc_1_wan_server_ip
    global wan_pc_1_netmask
    global wan_pc_1_gateway
    global wan_pc_1_ppp_server_ip
    global wan_2_dut_wan_ip
    global wan_pc_2_wan_server_ip
    global wan_pc_2_netmask
    global wan_pc_2_gateway
    global wan_pc_2_ppp_server_ip
    global wan_3_dut_wan_ip
    global wan_pc_3_wan_server_ip
    global wan_pc_3_netmask
    global wan_pc_3_gateway
    global wan_pc_3_ppp_server_ip


    # f = open(dut_common_file)
    lines = f.readlines()
    location = Get_Value(lines, "LOCATION")
    http_username = Get_Value(lines, "HTTP_USERNAME")
    http_password = Get_Value(lines, "HTTP_PASSWORD")
    f.close()
    
    f = open(wan_setting_file)
    lines = f.readlines()
    ppp_username = Get_Value(lines, "PPP_USERNAME")
    ppp_password = Get_Value(lines, "PPP_PASSWORD")
    f.close()

    wan_1_dut_wan_ip = Get_Value(lines, "WAN_1_DUT_WAN_IP")
    wan_pc_1_wan_server_ip = Get_Value(lines, "WAN_PC_1_SERVER_IP")
    wan_pc_1_netmask = Get_Value(lines, "WAN_PC_1_NETMASK")
    wan_pc_1_gateway = Get_Value(lines, "WAN_PC_1_GATEWAY")
    wan_pc_1_ppp_server_ip = Get_Value(lines, "WAN_PC_1_PPP_SERVER_IP")
    
    wan_2_dut_wan_ip = Get_Value(lines, "WAN_2_DUT_WAN_IP")
    wan_pc_2_wan_server_ip = Get_Value(lines, "WAN_PC_2_SERVER_IP")
    wan_pc_2_netmask = Get_Value(lines, "WAN_PC_2_NETMASK")
    wan_pc_2_gateway = Get_Value(lines, "WAN_PC_2_GATEWAY")
    wan_pc_2_ppp_server_ip = Get_Value(lines, "WAN_PC_2_PPP_SERVER_IP")

    wan_3_dut_wan_ip = Get_Value(lines, "WAN_3_DUT_WAN_IP")
    wan_pc_3_wan_server_ip = Get_Value(lines, "WAN_PC_3_SERVER_IP")
    wan_pc_3_netmask = Get_Value(lines, "WAN_PC_3_NETMASK")
    wan_pc_3_gateway = Get_Value(lines, "WAN_PC_3_GATEWAY")
    wan_pc_3_ppp_server_ip = Get_Value(lines, "WAN_PC_3_PPP_SERVER_IP")
    
    f.close()

def Load_DUT_Config(dut_config_file):
    global dut_ip
    global lan_port_list
    global wan_port_list
    global all_port_no
    global connect_dict

    f = open(dut_config_file)
    lines = f.readlines()

    for line in lines:
        print(">"+line)
        print()
        if '=' not in line:
            break
        var_split = line.split('=')
        #print("%s/%s"%(var_split[0], var_split[1]))
        if var_split[0] == "DUT_IP":
            dut_ip = var_split[1].replace('\n','')
        else:
            connect_dict[var_split[0]] = var_split[1].upper().replace(' ','_').replace('-','_').replace('\n','')

    print(connect_dict)
    print("=========================")

def Set_Wan_Port(port):
    msg = ("\nSet_Wan_Port: " +port)
    print_msg(msg)

    for i in range(6):
        try:
            driver.get(url.adv_wan_port_url)
            time.sleep(3)
            move = driver.find_element(By.TAG_NAME, 'body')
            move.send_keys(Keys.CONTROL + Keys.HOME)
            print_msg("Open adv_wan_port_url OK")            
            Try_Login(driver)

            try:
                iframe = driver.find_element("xpath", "//iframe[@id=\"settingsWindow\"]")
                print_msg("Expert UI")
                driver.switch_to.frame(iframe)
                print_msg("switch_to.frame")
            except:
                print_msg("Normal/ROG UI")
            
            try:
                select = Select(driver.find_element("name", "wans_primary"))
                time.sleep(1)
                print_msg("Find 'wans_primary'")
            except:
                print_msg("Can not find 'wans_primary' xpath retry")
            
            try:
                select.select_by_visible_text(port)
                time.sleep(1)
                print_msg("Select port OK")
            except:
                print_msg("select_by_visible_text Fail")

            try:
                driver.find_element("xpath", "//input[@onclick=\"applyRule()\"]").click()
                time.sleep(1)
                print_msg("applyRule OK")

                try:
                    alert = driver.switch_to.alert
                    print("alert:" + alert.text)
                    alert.accept()
                except:
                    print_msg("No alert")
                break                
            except:
                print_msg("applyRule Fail")
        
        except:
            print_msg("Connection refuce, wait 30 sec & try ")
            time.sleep(30)
    
    if i == 5:
        print_msg("Retry 5 times.")
        return False
        
    print_msg("Wait 240 for DUT reboot...")
    time.sleep(240)

    if not Ping(dut_ip, 300, 10):
        msg = 'Can not ping DUT - %s for 5 mins. Stop test'%(dut_ip)
        print_msg(msg)
    else:
        print_msg("ping 192.168.50.1 OK, keep test.")

    return True

def Update_Run_Qis(fun_qis, i):
    global run_qis
    
    if fun_qis.isChecked():
        run_qis = 1
    else:
        run_qis = 0
        
    logger.info("qis= " + str(run_qis))
    
    
def Update_Function_List(fun_cb, i):
    global model_name
    global function_list
    global wan_type_list
    
    if fun_cb.isChecked():
        function_list[i] = fun_cb.text()
    else:
        function_list[i] = ''
        
    logger.info(function_list)


def Update_Wantype_List(wantype, i):
    global model_name
    global function_list
    global wan_type_list
    
    if wantype.isChecked():
        wan_type_list[i] = wantype.text()
        '''
        if wantype.text() == "Dynamic IP":
            wan_type_list[i] = "DYNAMICIP"
        if wantype.text() == "Static IP":
            wan_type_list[i] = "STATICIP"
        if wantype.text() == "PPPoE":
            wan_type_list[i] = "PPPOE"
        '''
    else:
        wan_type_list[i] = ''
        
    logger.info(wan_type_list)


class MyWidget(QtWidgets.QWidget):
    global UI_start
    global model_name
    global chariot_pair
    global function_list
    global wan_type_list
    def __init__(self):
        super().__init__()
        '''
                #Chrome driver check
        if chrome_chk_ret != 'OK':
            #self.btn.setDisabled(True)
            
            self.mbox = QtWidgets.QMessageBox(self)
            warn_msg = chrome_chk_ret + '\nPlease go to \"https://chromedriver.chromium.org/\" & download new chromedriver.'
            self.mbox.information(self, 'info', warn_msg)
        else:
        '''
        self.setWindowTitle('Multi-port NAT Test %s'%(version))
        self.resize(470, 270)
        self.setUpdatesEnabled(True)
        self.ui()

        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-10), 128) 
    def ui(self):     
        # model name content
        self.label1 = QtWidgets.QLabel(self)
        self.label1.setText('Model:')
        self.label1.move(30, 20)
        self.box1 = QtWidgets.QComboBox(self)
        files = listdir(config_path)
        for f in files:
            fullpath = join(config_path, f)
            if isdir(fullpath):
                self.box1.addItem(f)
        self.box1.setGeometry(30, 48, 148, 25)

        # Chariot pair
        self.label2 = QtWidgets.QLabel(self)
        self.label2.setText('Cahriot pair:')
        self.label2.move(30, 80)
        self.box2 = QtWidgets.QComboBox(self)
        # files = listdir(chariot_pair_path)
        # for f in files:
        #     pairpath = join(chariot_pair_path, f)
        #     if isdir(pairpath):
        #         self.box2.addItem(f)
        self.box2.move(110, 80)

        #test time
        self.label3 = QtWidgets.QLabel(self)
        self.label3.setText('Run Chariot:')
        self.label3.move(30, 110)

        self.box3 = QtWidgets.QComboBox(self)
        for t in range(1,4,1):
            st = str(t)
            self.box3.addItem(str(t))
        self.box3.move(145, 110)

        #repeat time
        self.label4 = QtWidgets.QLabel(self)
        self.label4.setText('Repeat:')
        self.label4.move(30, 140)

        self.box4 = QtWidgets.QComboBox(self)
        for t in range(1,4,1):
            self.box4.addItem(str(t))
        self.box4.move(145, 140)

        #Run QIS
        self.fun_q = QtWidgets.QCheckBox(self)
        self.fun_q.move(30, 170)
        self.fun_q.setText('Run QIS')
        self.fun_q.setEnabled(False)
        self.fun_q.clicked.connect(lambda:Update_Run_Qis(self.fun_q, 0))

        #Specify LAN
        self.fun_hw = QtWidgets.QCheckBox(self)
        self.fun_hw.move(30, 200)
        self.fun_hw.setText('Specify LAN port test')
        self.fun_hw.setChecked(False)
        self.fun_hw.clicked.connect(self.Update_HW_Require)

        
        # function content
        self.label2 = QtWidgets.QLabel(self)
        self.label2.setText('Enable Function:')
        self.label2.move(210, 20)
        
        self.fun_a = QtWidgets.QCheckBox(self)
        self.fun_a.move(210, 50)
        self.fun_a.setText('Default')
        self.fun_a.setChecked(True)
        self.fun_a.clicked.connect(lambda:Update_Function_List(self.fun_a, 0))

        self.fun_b = QtWidgets.QCheckBox(self)
        self.fun_b.move(210, 80)
        self.fun_b.setText('AiProtection')
        self.fun_b.setChecked(True)
        self.fun_b.clicked.connect(lambda:Update_Function_List(self.fun_b, 1))
        
        self.fun_c = QtWidgets.QCheckBox(self)
        self.fun_c.move(210, 110)
        self.fun_c.setText('Adaptive_QoS')
        self.fun_c.setChecked(True)
        self.fun_c.clicked.connect(lambda:Update_Function_List(self.fun_c, 2))
        
        self.fun_d = QtWidgets.QCheckBox(self)
        self.fun_d.move(210, 140)
        self.fun_d.setText('Traditional_QoS')
        self.fun_d.setChecked(True)
        self.fun_d.clicked.connect(lambda:Update_Function_List(self.fun_d, 3))
        
        # wan type content
        self.label3 = QtWidgets.QLabel(self)
        self.label3.setText('Wan Type:')
        self.label3.move(350, 20)
        
        self.wantype_a = QtWidgets.QCheckBox(self)
        self.wantype_a.move(350, 50)
        self.wantype_a.setText('Automatic IP')
        self.wantype_a.setChecked(True)
        self.wantype_a.clicked.connect(lambda:Update_Wantype_List(self.wantype_a, 0))
        
        self.wantype_b = QtWidgets.QCheckBox(self)
        self.wantype_b.move(350, 80)
        self.wantype_b.setText('Static IP')
        self.wantype_b.setChecked(True)
        self.wantype_b.clicked.connect(lambda:Update_Wantype_List(self.wantype_b, 1))
        
        self.wantype_c = QtWidgets.QCheckBox(self)
        self.wantype_c.move(350, 110)
        self.wantype_c.setText('PPPoE')
        self.wantype_c.setChecked(True)
        self.wantype_c.clicked.connect(lambda:Update_Wantype_List(self.wantype_c, 2))
        
        self.wantype_d = QtWidgets.QCheckBox(self)
        self.wantype_d.move(350, 140)
        self.wantype_d.setText('PPTP')
        self.wantype_d.setChecked(True)
        self.wantype_d.clicked.connect(lambda:Update_Wantype_List(self.wantype_d, 3))

        self.wantype_e = QtWidgets.QCheckBox(self)
        self.wantype_e.move(350, 170)
        self.wantype_e.setText('L2TP')
        self.wantype_e.setChecked(True)
        self.wantype_e.clicked.connect(lambda:Update_Wantype_List(self.wantype_e, 4))
        
        #start button
        self.btn = QtWidgets.QPushButton(self)
        self.btn.setText('Start')
        self.btn.move(350,230)
        self.btn.clicked.connect(self.ShowBtn)
    
    def ShowBtn(self):
        global UI_start
        self.btn.setDisabled(True)
        QApplication.processEvents()
        UI_start = 1
        Start_Test()
        self.btn.setDisabled(False)

    def Update_HW_Require(self):
        global specify_lan_port_test
        
        if self.fun_hw.isChecked():
            specify_lan_port_test = 1
            
            self.fun_b.setChecked(False)
            self.fun_c.setChecked(False)
            self.fun_d.setChecked(False)
        else:
            specify_lan_port_test = 0
            self.fun_b.setChecked(True)
            self.fun_c.setChecked(True)
            self.fun_d.setChecked(True)

def start():
    global driver
    global now_time
    global log_file
    global result_file
    global function
    global model_name
    global test_time
    global function_list
    global wan_type_list
    global run_qis
    global ping_lan_client_fail
    global report_path

    report_path= "C:\project\Louis_Selenium\log"
    TPT = [['N/A']*3 for _ in range(5)]
    # if os.path.isfile(auto_run_file):
    #         f = open(auto_dut_file)
    #         lines = f.readlines()
    #         #print(lines)
    #         model_name = Get_Value(lines, "MODEL_NAME")
    #         report_path = Get_Value(lines, "REPORT_PATH")
    msg = "model_name: " + model_name
    logger.info(msg)

    config_file = 'info.txt'
    specify_lan_port_file = 'specify_lan_port_test.txt'

    print("\nSelect Function:")
    for func in function_list:
        print(func)
    print("\nSelect WAN type:")
    for wantype in wan_type_list:
        print(wantype)
    
    Load_DUT_Config(config_file)


    if run_qis:
        if not Ping(dut_ip, 300, 10):
            msg = 'Can not ping DUT - %s for 5 mins. Stop test'%(dut_ip)
            print_msg(msg)
            return
        else:
            print_msg("ping 192.168.50.1 OK, keep test.")
                    
            qis_config = 0
            while (qis_config < 3):
                if Run_QIS():
                    print_msg("Run QIS Pass")
                    break
                else:
                    print_msg("Run QIS Fail. Reset DUT & try again.")
                    qis_config += 1
                    # Reset_CAP()

            if qis_config == 3:
                print_msg("DUT is not default & try to reset fail for 3 times. STOP TEST!!!")
                return

    print_msg("test_start")


    Disable_Redirect(driver)
    # Enable_EULA(dut_ip)
def Start_Test():
    # global driver
    global now_time
    global log_file
    global result_file
    global function
    global model_name
    global test_time
    global run_chariot
    global function_list
    global wan_type_list
    global run_qis
    global ping_lan_client_fail
    global report_path
    global chariot_pair
    
    print_msg("UI_start = %d"%(UI_start))

    if UI_start:
        model_name = Form.box1.currentText()
        chariot_pair = Form.box2.currentText()
        run_chariot = Form.box3.currentText()
        test_time = Form.box4.currentText()
    else:
        if os.path.isfile(auto_run_file):
            f = open(auto_dut_file)
            lines = f.readlines()
            #print(lines)
            model_name = Get_Value(lines, "MODEL_NAME")
            report_path = Get_Value(lines, "REPORT_PATH")
            chariot_pair = Get_Value(lines, "CHARIOT_PAIR")
    
    msg = "model_name: " + model_name
    print_msg(msg)    
    msg = "chariot_pair: " + chariot_pair
    print_msg(msg)

    config_file = config_path + model_name + '\\info.txt'
    specify_lan_port_file = config_path + model_name + '\\specify_lan_port_test.txt'

    try:
        os.remove(".\\Chariot\\runtst.log")    
    except:
        msg = "No runtst.log"
        print_msg(msg)
    try:
        os.remove(".\\Chariot\\CHARIOT.LOG")    
    except:
        msg = "No CHARIOT.LOG"

    print_msg("Select Function:")
    for func in function_list:
        print(func)
    print_msg("Select WAN type:")
    for wantype in wan_type_list:
        print(wantype)

    Load_DUT_Config(config_file)

    if run_qis:
        if not Ping(dut_ip, 300, 10):
            msg = 'Can not ping DUT - %s for 5 mins. Stop test'%(dut_ip)
            print_msg(msg)
            return
        else:
            print_msg("ping 192.168.50.1 OK, keep test.")
                    
            qis_config = 0
            while (qis_config < 3):
                if Run_QIS():
                    print_msg("Run QIS Pass")
                    break
                else:
                    print_msg("Run QIS Fail. Reset DUT & try again.")
                    qis_config += 1
                    # Reset_CAP()

            if qis_config == 3:
                print_msg("DUT is not default & try to reset fail for 3 times. STOP TEST!!!")
                return
    

    title = "Tool, Pair, Tool version, Model, FW Version, Enable Function, WAN PORT, LAN PORT, WAN TYPE, Test PC ping DUT, DUT ping WAN PC, Test PC ping WAN PC, Uplink(mbps), Downlink(mbps), Bi-direction(mbps)\n"
    result_file = 'sult_mulit_port_test_result_.csv'
    msg = ('Open: ' + result_file)
    print_msg(msg)
    ret_file = open( result_file, 'w')
    ret_file.write(title)
    ret_file.close()

    # Disable_Redirect()
    
    try:
        driver.get("http://192.168.50.1/")
        Try_Login()
    except:
        print_msg("執行失敗")
    finally:
        countdown(5)
        driver.quit()
        print_msg("結束程式")

def main():
    '''
    Start Test
    '''
    try:
        driver.get("http://192.168.50.1/")
        Try_Login()
    

        qos_type = "Traditional_QoS"
        # Enable_QoS(qos_type)
        # Disable_QoS()
        # if function == 'AiProtection':
        #     Enable_Aiportection(driver)
        # elif function == 'Adaptive_QoS':
        #     Enable_QoS("Adaptive_QoS")
        # elif function == 'Traditional_QoS':
        #     Enable_QoS(driver, "Traditional_QoS")


        # Enable_Qos()
        # Disable_QoS()
        # qis_wizard()
        # index()
        # AIMesh(driver)
        # # guest(driver)
        # Enable_Aiportection()
        # Disable_Aiportection()
        # web_protector()
        # traffic(driver)
        # usb()
        # cloud()
        # wireless()
        # vpn()
        # # lan_content()
        # # wan_content()
        # # Smart_Home_Alexa()
        # firewall()
        administration()
        # system_log()
        # network_tool()
    except:
        print_msg("執行失敗")
    
    # guest(driver)
    # Enable_Aiportection(driver)
    # Disable_Aiportection(driver)
    # Enable_QoS(driver,"Traditional_QoS")
    # Disable_QoS(driver)
    # # WAN()

if __name__ == "__main__":
    global driver
    now  = datetime.now()
    now_time = now.strftime("%Y-%m-%d-%H-%M")
    cur_directory = os.getcwd()
    config_path = cur_directory + '/Config/'
    log_file = cur_directory +'/log/' + now_time + '_process.log'
    qis_file = cur_directory + '\\Config\\qis_setting.txt'
    auto_run_file = cur_directory + '\\Config\\autorun.txt'
    auto_dut_file = cur_directory + '\\Config\\autotest_setting.txt'
    test_case_file = cur_directory + '\\Config\\Test_case.txt'
    f = cur_directory + '\\Config\\DUT_common_setting.txt'
    wan_setting_file = cur_directory + '\\Config\\WAN_server_setting.txt'
    # # Load_General_Config()
    autorun_path = config_path + '\\autorun.txt'
    # chrome_chk_ret = browser_driver_version_check(logger)

    # if chrome_chk_ret != 'OK':
    #     chrome_driver_version = query_chrome_driver_version()
    #     warn_msg = ('Chromedriver version is %s' %(chrome_driver_version))
    #     logger.info(warn_msg)
    #     warn_msg = chrome_chk_ret + '\nPlease go to \"https://chromedriver.chromium.org/\" & download new chromedriver.'
    #     logger.info(warn_msg)
    #     time.sleep(15)
    # else:
    #     logger.info(url.dut_url)
    #     driver = webdriver.Chrome()
    #     driver.maximize_window()
    # try:
    #     driver = webdriver.Chrome()
    #     driver.maximize_window()
    #     main()
    # finally:
    #     countdown(5)
    #     driver.quit()
    #     print_msg("結束程式")
    driver = webdriver.Chrome()
    driver.maximize_window()
    app = QtWidgets.QApplication(sys.argv)
    Form = MyWidget()
    Form.show()
    
    file = open(autorun_path, "r")
    lines = file.readlines()
    file.close()
    print_msg(lines)
    for line in lines:
        print_msg(line)
        if "Run" in line:
            print_msg('Run test by trigger.')
            os._exit(0)
            # main(driver)
            Start_Test()   
    sys.exit(app.exec())
    
        
            
