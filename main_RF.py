import os
import re
import time
import logging
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import threading

# Channel options
channel_options = ["自動","100", "104", "108", "112", 
                "116", "120", "124", "128", 
                "132", "136", "140", "144", 
                "149", "153", "157", "161", "165"]

# 設定基本資訊
dut_url = "http://192.168.50.1/Main_Login.asp"
dut_url_wifi = "http://192.168.50.1/Advanced_Wireless_Content.asp"
esg_url = "http://192.168.50.18/display"
wave_url = "http://192.168.50.14/remote_fp.html"
http_username = "admin"
http_password = "admin"

logging.basicConfig(level=logging.INFO, format="[%(asctime)s - %(levelname)s] - %(message)s")
logger = logging.getLogger()

# 輸出訊息到日誌和 GUI
def print_msg(msg):
    logger.info(msg)
    log_text.config(state='normal')  # 設為可寫入
    log_text.insert(tk.END, msg + "\n")  # 插入訊息
    log_text.see(tk.END)  # 自動滾動到底部
    log_text.config(state='disabled')  # 再設回不可寫入
    root.update()  # 更新 UI，確保即時顯示

# 倒數計時
def countdown(seconds):
    for i in range(seconds, 0, -1):
        print_msg(f"倒數: {i}秒")
        root.after(i * 1000, print_msg, f"倒數: {i}秒")  # 用after方法避免阻塞
        time.sleep(1)

# 優化：使用 WebDriverWait 等待元素
def wait_for_element(driver, xpath, timeout=10):
    try:
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
        print_msg(f"元素 {xpath} 已經加載完成")
    except Exception as e:
        print_msg(f"等待元素 {xpath} 失敗: {e}")

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

# 登入路由器
def login(driver, retries=3):
    print_msg("[嘗試登入路由器]")
    for attempt in range(retries):
        try:
            driver.get(dut_url)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "login_username"))
            ).send_keys(http_username)
            driver.find_element(By.NAME, "login_passwd").send_keys(http_password)
            
            # 嘗試不同登入方式
            try:
                driver.find_element(By.XPATH, "//div[@onclick='login();']").click()
            except:
                driver.find_element(By.XPATH, "//div[@onclick='preLogin();']").click()

            print_msg("登入成功")
            return True  # 成功就返回
        except Exception as e:
            print_msg(f"登入失敗 (嘗試 {attempt+1}/{retries}): {e}")
            time.sleep(2)  # 等待 2 秒後重試
    return False  # 全部嘗試後仍失敗

# 獲取當前控制頻道
def get_dfs_channel(driver):
    print_msg("[前往 WiFi 設定頁面]")
    try:
        driver.get(dut_url_wifi)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), '當前控制頻道')]"))
        )
        
        elements = driver.find_elements(By.XPATH, "//*[contains(text(), '當前控制頻道')]")
        for element in elements:
            match = re.search(r'\d+', element.text)
            if match:
                channel_number = int(match.group())
                print_msg(f"5 GHz 當前控制頻道: {channel_number}")
                return channel_number

        # 若 XPath 方式未成功，則嘗試透過下拉選單讀取
        select_element = Select(driver.find_element(By.NAME, "wl_channel"))
        channel_number = select_element.first_selected_option.text
        print_msg(f"5 GHz 當前控制頻道: {channel_number}")
        return channel_number
    except Exception as e:
        print_msg(f"提取控制頻道失敗: {e}")
        return None

# 更改頻道
def change_channel(driver, channel):
    if channel not in channel_options:
        print_msg(f"無效的頻道: {channel}")
        return False
    
    print_msg(f"[嘗試更改頻道為 {channel}]")
    try:
        select = Select(driver.find_element(By.NAME, "wl_channel"))
        current_channel = select.first_selected_option.text.strip()
        
        if current_channel == channel:
            print_msg(f"目前頻道已是 {channel}，無需變更")
            return True  # 不需要變更
        
        select.select_by_visible_text(channel)
        print_msg(f"頻道已更改為: {channel}")
        
        driver.find_element("xpath", "//input[@onclick=\"applyRule();\"]").click()
        WebDriverWait(driver, 5).until(EC.alert_is_present())  
        alert = driver.switch_to.alert  
        print_msg(f"套用設定: {alert.text}")
        alert.accept()  
        print_msg("設定已套用！")
        
        # 點擊確認按鈕
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "confirm_button_gen_long_left"))
        ).click()
        
        wait_for_completion(driver)
        return True
    except Exception as e:
        print_msg(f"頻道更改失敗: {e}")
        return False


# 找到「重新開機」按鈕
def reboot_router(driver):
    print_msg("[嘗試重新啟動路由器]")
    try:
        reboot_span = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//span[text()='重新開機']"))
        )
        reboot_button = reboot_span.find_element(By.XPATH, "./parent::*")
        driver.execute_script("arguments[0].click();", reboot_button)
        print_msg("成功點擊重新開機按鈕")

        WebDriverWait(driver, 5).until(EC.alert_is_present())
        alert = driver.switch_to.alert  
        print_msg(f"提示訊息: {alert.text}")  
        alert.accept()  
        print_msg("提示框已被消除！")

        wait_for_completion(driver)
        return True
    except Exception as e:
        print_msg(f"重新開機失敗: {e}")
        return False

# 監測進度條直到達到 100%
def wait_for_completion(driver):
    """監測進度條直到達到 100%"""
    try:
        while True:
            # 等待進度條出現
            progress_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "proceeding_txt"))
            )
            
            progress_text = progress_element.text.strip()  # 讀取當前進度
            print_msg(f"處理中: {progress_text}")

            # 檢查是否達到 100%
            if "100%" in progress_text:
                print_msg("處理完成！")
                break
            
            time.sleep(1)  # 每秒檢查一次
            
    except Exception as e:
        print_msg("監測進度時發生錯誤")

def open_esg_web(driver,channel_number):
    print_msg("前往 ESG 設定頁面")
    channel_number = int(channel_number)
    test_hz = (channel_number * 5 + 5001) / 1000
    print_msg(f'FREQUENCY: {test_hz} GHZ')
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

def open_wave_web(driver):
    print_msg("前往 WAVE 設定頁面")
    try:
        driver.get(wave_url)
        countdown(3)
        try:
            update_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//input[@type='BUTTON' and @name='Update']"))
            )
            update_button.click()
            print_msg("成功點擊 Update！")
            countdown(2)
            img_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//img[@src='StoreRclKey.gif']"))
            )
            img_button.click()
            print_msg("成功點擊Store/Recall！")
            countdown(2)
            driver.execute_script("doSubmit(37);")
            print_msg("成功點擊Recall State！")
            driver.execute_script("doSubmit(22);")
            print_msg("成功點擊Recall State！")
            for i in range(3):
                driver.execute_script("doSubmit(1);")
                print_msg("按下trigger")
        except Exception as e:
            print("未找到按鈕:", e)
        except:
            print_msg("ESG 啟動失敗")
    except:
        print_msg("前往 WAVE 設定頁面失敗")

def start_test(channel):
    print_msg("[開始測試]")
    
    if not login(driver):
        print_msg("登入失敗，無法繼續測試")
        return
    
    channel_number = get_dfs_channel(driver)
    print_msg(f"5 GHz 當前控制頻道: {channel_number}")
    
    if not change_channel(driver, channel):
        print_msg(f"變更頻道失敗，測試中止")
        return
    
    countdown(3)
    
    if not reboot_router(driver):
        print_msg("重新開機失敗，請手動檢查")
    
    countdown(3)

    open_esg_web(driver,channel_number)
    open_wave_web(driver)
        

if __name__ == "__main__":
    global driver
    driver = webdriver.Chrome()
    driver.maximize_window()
    # GUI 介面
    root = tk.Tk()
    root.title("路由器測試工具")
    # root.geometry("500x750")
    # root.configure(bg="#2c3e50")

    # 設置進度條
    progress_bar = ttk.Progressbar(root, length=300, mode="indeterminate")
    progress_bar.pack(pady=20)

    # 設定字型和顏色
    style = ttk.Style()
    style.configure("TButton", font=("Helvetica", 12), padding=10)
    style.configure("TLabel", font=("Helvetica", 12), background="#2c3e50", foreground="white")
    style.configure("TButtonStartTest", font=("Helvetica", 12, "bold"), foreground="green")

    frame = ttk.Frame(root, padding=15)
    frame.pack(fill=tk.BOTH, expand=True)

    # 登入按鈕
    login_btn = ttk.Button(frame, text="登入路由器", command=lambda:login(driver))
    login_btn.pack(fill=tk.X, pady=10)

    # 獲取頻道按鈕
    get_channel_btn = ttk.Button(frame, text="獲取當前控制頻道", command=lambda: get_dfs_channel(driver))
    get_channel_btn.pack(fill=tk.X, pady=10)

    # 頻道選擇欄
    channel_label = ttk.Label(frame, text="選擇 WiFi 頻道:")
    channel_label.pack(pady=5)

    channel_var = tk.StringVar()
    channel_dropdown = ttk.Combobox(frame, textvariable=channel_var, values=channel_options, state="readonly")
    channel_dropdown.pack(fill=tk.X, pady=5)

    # 更改頻道按鈕
    change_channel_btn = ttk.Button(frame, text="更改頻道", command=lambda: change_channel(driver,channel_var.get()))
    change_channel_btn.pack(fill=tk.X, pady=5)

    # 重新開機路由器按鈕
    reboot_btn = ttk.Button(frame, text="重新開機路由器", command=lambda:reboot_router(driver))
    reboot_btn.pack(fill=tk.X, pady=5)
    
    # E4438C按鈕
    esg_btn = ttk.Button(frame, text="E4438C", command=lambda:open_esg_web(driver,channel_var.get()))
    esg_btn.pack(fill=tk.X, pady=5)

    # 33220A按鈕
    esg_btn = ttk.Button(frame, text="33220A", command=lambda:open_wave_web(driver))
    esg_btn.pack(fill=tk.X, pady=5)
    # **新增 "開始測試" 按鈕**
    start_test_btn = ttk.Button(frame, text="開始測試", command=lambda: start_test(channel_var.get()))
    start_test_btn.pack(fill=tk.X, pady=5)

    # 日誌顯示區域
    log_text = scrolledtext.ScrolledText(
        root, wrap=tk.WORD, state='disabled', bg="#000000", fg="#39ff14", font=("Courier New", 12)
    )
    log_text.pack(fill=tk.X, pady=5)
    log_text.configure(bg="black", fg="#39ff14")  # 設定黑底綠字

    
    root.mainloop()

    if driver:
        driver.quit()
