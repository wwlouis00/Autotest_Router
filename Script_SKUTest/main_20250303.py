import tkinter as tk
from tkinter import messagebox, scrolledtext, font, Canvas, Frame, Scrollbar
from datetime import datetime
from ftplib import FTP
import os
import threading
import py7zr
import re
import shutil
import subprocess
import zipfile
import logging
import requests
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import psutil
import socket
from requests.exceptions import RequestException
import contextlib
import json
# Initialize logger
logging.basicConfig(level=logging.INFO, format="[%(asctime)s - %(levelname)s] - %(message)s")
logger = logging.getLogger()

# Global flag for matrix.xlsx detection
matrix_detected = threading.Event()

# Global parameters
BATCH_FILE_NAME = "ExecuteTestCase_SQ_AutoQuery.bat"
CURRENT_TIME = datetime.now().strftime("%Y%m%d")
CHROMEDRIVER_FOLDER = "chromedriver"
CHROMEDRIVER_FILE_test = "chromedriver-win64/chromedriver.exe"
FTP_HOST = "vendorftp.asus.com"
FTP_USER = "WLRD_ReadOnly"
FTP_PASS = "D226#BCTC626#BCTC626#BCT"
TARGET_FOLDER = "/WLRD/ATE/sku test tool"
VERSION_REGEX = r"\d{8} SkuTool SKUDependentTest_AsusQt_V\d+\.\d+\.\d+\.\d+"

# Gmail configuration
sender_email = "jenkins.wireless@gmail.com"
sender_password = "vbnslfmnslutyzyf"  # Replace with your app-specific password
LOG_FILE = "email_log.json"

stop_event = threading.Event()
active_threads = []  # 用來存儲執行緒
# 自訂 Logger 類別
class CustomLogger(logging.Handler):
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget

    def emit(self, record):
        log_entry = self.format(record)
        self.text_widget.configure(state='normal')  # 啟用編輯狀態
        self.text_widget.insert(tk.END, log_entry + '\n')  # 插入日誌內容
        self.text_widget.see(tk.END)  # 自動滾動到最新行
        self.text_widget.update_idletasks()  # 即時更新畫面
        self.text_widget.configure(state='disabled')  # 禁用編輯狀態

# 新增收件人欄位
def add_recipient():
    logger.info("新增收件人")
    email = entry_email.get()
    if email and email not in email_history:
        email_history.append(email)
        save_emails()
    if email:
        recipient_entries.append(email)
        update_recipient_list()
        entry_email.delete(0, tk.END)  # 清空輸入框
    logger.info(f"收件人列表: {recipient_entries}")
# 刪除收件人欄位
def delete_recipient(email):
    # 檢查 email 是否在 recipient_entries 中
    logger.info("刪除收件人")
    if email in recipient_entries:
        recipient_entries.remove(email)  # 從列表中刪除該 email
        update_recipient_list()  # 更新 UI 或顯示的收件人列表
    logger.info(f"收件人列表: {recipient_entries}")

def load_emails():
    try:
        with open(LOG_FILE, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []
    
def save_emails():
    with open(LOG_FILE, "w") as file:
        json.dump(email_history, file)

def log_email():
    email = entry_email.get()
    if email and email not in email_history:
        email_history.append(email)
        save_emails()
    logger.insert(tk.END, f"輸入的信箱: {email}\n")
    logger.yview(tk.END)  # 滾動到底部
    entry_email.delete(0, tk.END)  # 清空輸入框

def open_email_selection(root):
    selection_window = tk.Toplevel(root)
    selection_window.title("選擇歷史信箱")
    selection_window.geometry("300x200")
    
    for email in email_history:
        tk.Button(selection_window, text=email, command=lambda e=email: select_email(e, selection_window)).pack(fill=tk.X, padx=5, pady=2)

def select_email(email, window):
    entry_email.delete(0, tk.END)
    entry_email.insert(0, email)
    window.destroy()

def update_recipient_list():
    # 定義字型
    # bold_font = font.Font(family='Arial', size=20, weight='bold')
    button_font = font.Font(family='Arial', size=20, weight='bold')
    # 清空收件人框架內的所有內容
    for widget in frame_recipients.winfo_children():
        widget.destroy()

    # 重新顯示所有收件人
    for email in recipient_entries:
        recipient_frame = tk.Frame(frame_recipients, bg="#444444", pady=5, padx=5)
        recipient_frame.pack(fill=tk.X, pady=2)

        label_email = tk.Label(recipient_frame, text=email, font=button_font, bg="#555555", fg="white", anchor="w")
        label_email.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        btn_delete = tk.Button(
            recipient_frame, text="刪除", font=button_font, fg="red", bg="#666666",
            command=lambda e=email: delete_recipient(e)
        )
        btn_delete.pack(side=tk.RIGHT, padx=5)


def start_process(start_button,stop_button,local_folder):
    """發送郵件給所有收件人"""
    recipients = [email.strip() for email in recipient_entries if email.strip()]
    
    if not recipients:
        messagebox.showerror("錯誤", "請輸入至少一個收件人！")
        return  # 直接返回，避免繼續執行
    
    logger.info(f"驗證後的收件人列表: {recipients} (共 {len(recipients)} 人)")

     # 按鈕狀態切換
    start_button.configure(state='disabled')
    stop_button.configure(state='normal')
    stop_event.clear()

    # 啟動下載與處理的執行緒
    thread = threading.Thread(
        target=download_and_process_files, args=(start_button,recipients,local_folder), daemon=True
    )
    thread.start()
    active_threads.append(thread)  # 記錄執行中的執行緒

# 新增停止處理按鈕的函數
def stop_process(start_button,stop_button):
    """停止所有下載與處理執行緒"""
    global active_threads
    # 恢復按鈕狀態
    stop_button.configure(state='disabled')
    start_button.configure(state='normal')
    logger.info("請求中止處理...")
    stop_event.set()  # 設置停止標記

    # 等待所有執行緒結束
    for thread in active_threads:
        thread.join()  # 等待執行緒完全結束
    active_threads.clear()  # 清空執行緒列表
    logger.info("所有執行緒已停止。")
    
    

# 清除日誌的函數
def clear_log(log_text):
    logger.info("Clean Log")
    log_text.configure(state='normal')  # 解除只讀狀態
    log_text.delete(1.0, tk.END)        # 刪除所有內容
    log_text.configure(state='disabled')  # 設定為只讀狀態

# 設定 Logger
def setup_logger(log_widget):
    logger = logging.getLogger('ProcessLogger')
    logger.setLevel(logging.DEBUG)

    handler = CustomLogger(log_widget)
    formatter = logging.Formatter(
        '[%(asctime)s] - %(message)s', datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger

def get_default_gateway():
    """Fetch the default gateway."""
    try:
        gateways = psutil.net_if_addrs()  # Get network interfaces' addresses
        for iface, addrs in psutil.net_if_addrs().items():
            for addr in addrs:
                if addr.family == socket.AF_INET:  # Look for IPv4 addresses
                    gateway = addr.address
                    logger.info(f"Found Default Gateway: {gateway}")
                    return gateway
    except Exception as e:
        logger.error(f"Error fetching the default gateway: {e}")
    return None

####################################################################################
def set_ip_metric_for_gateway(ip_address, i):
    logger.info(f"正在更新網路階段: {i}")

    # 查找指定 IP 地址對應的網路介面
    interface_name = None
    for iface, addrs in psutil.net_if_addrs().items():
        for addr in addrs:
            if addr.family == socket.AF_INET and addr.address == ip_address:
                interface_name = iface
                break
        if interface_name:
            break

    if not interface_name:
        raise ValueError(f"未找到 IP 地址 {ip_address} 對應的網路介面")

    # 判斷是 DUT 還是外網
    is_dut = "192.168.50" in ip_address
    logger.info(f"找到網路介面: {interface_name}，是否為 DUT: {is_dut}")

# 動態設置主介面和次介面
    if "乙太網路" in interface_name:
        primary_interface = interface_name
        secondary_interface = None

        # 查找其他 "乙太網路" 開頭的次要介面
        for iface in psutil.net_if_addrs().keys():
            if iface.startswith("乙太網路") and iface != primary_interface:
                secondary_interface = iface
                break

        if not secondary_interface:
            logger.info(f"未找到次要網路介面，僅更新主網路介面: {primary_interface}")
            secondary_interface = primary_interface  # 如果沒有找到次要介面，設置與主介面相同
    else:
        logger.info(f"未知網路介面: {interface_name}")
        return

    # 根據模式設置 metric
    if i == 0:  # 開啟外網，外網 metric=1，DUT metric=6000
        primary_metric, secondary_metric = (1, 6000) if not is_dut else (6000, 1)
    elif i == 1:  # 關閉外網，外網 metric=6000，DUT metric=1
        primary_metric, secondary_metric = (6000, 1) if not is_dut else (1, 6000)
    else:
        raise ValueError("無效的模式，i 必須是 0 或 1")

    # 設置 IP metric
    set_metric(primary_interface, primary_metric)
    set_metric(secondary_interface, secondary_metric)

def set_metric(interface_name, metric):
    command = f"netsh interface ip set interface \"{interface_name}\" metric={metric}"
    try:
        logger.info(f"執行命令: {command}")
        result = os.system(command)
        if result == 0:
            logger.info(f"成功設置 IP metric，命令: {command}")
        else:
            logger.error(f"命令執行失敗: {command}，返回值: {result}")
    except Exception as e:
        logger.error(f"執行命令時發生錯誤: {e}")
########################################################################################################

# 驗證信箱
def validate_email(email):
    return "@asus.com" in email

def delete_old_versions(local_folder):
    """Delete old version folders."""
    logger.info("Scanning local folder for old version directories.")
    version_folder_pattern = r"\d{8} SkuTool"  # 可抽象为配置变量
    for folder_name in os.listdir(local_folder):
        folder_path = os.path.join(local_folder, folder_name)

        # 检查是否是文件夹
        if not os.path.isdir(folder_path):
            logger.debug(f"Skipping non-folder item: {folder_name}")
            continue

        # 检查是否符合版本文件夹的命名规则
        if not re.match(version_folder_pattern, folder_name):
            logger.debug(f"Skipping non-version folder: {folder_name}")
            continue
        
        try:
            # 删除文件夹
            shutil.rmtree(folder_path)
            logger.info(f"Successfully deleted old version folder: {folder_path}")
        except Exception as e:
            # 在日志中记录详细的错误信息
            logger.error(f"Failed to delete folder {folder_path}. Error: {e}")
            logger.debug(f"Contents of folder {folder_path}: {os.listdir(folder_path)}")

def get_latest_chromedriver_version():
    """Fetch the latest ChromeDriver version."""
    url = "https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json"
    retries=3
    attempt = 0
    while attempt < retries:
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)

            # Parse JSON data
            data = response.json()
            if "channels" in data and "Stable" in data["channels"]:
                stable_channel = data["channels"]["Stable"]
                version = stable_channel.get("version")
                downloads = stable_channel.get("downloads", {}).get("chromedriver", [])
                
                if version and downloads:
                    return version, downloads
                else:
                    raise ValueError("Missing version or downloads in response data.")
            else:
                raise ValueError("Unexpected response format.")
        
        except RequestException as e:
            attempt += 1
            if attempt >= retries:
                raise Exception(f"Failed to fetch ChromeDriver version after {retries} attempts.") from e
            else:
                print(f"Retrying... ({attempt}/{retries})")
                
        except (ValueError, KeyError) as e:
            raise Exception(f"Invalid response data: {e}") from e

def download_chromedriver(download_url, download_path=CHROMEDRIVER_FOLDER):
    """Download the ChromeDriver."""
    try:
        if not os.path.exists(download_path):
            os.makedirs(download_path)

        file_name = os.path.join(download_path, download_url.split("/")[-1])

        logger.info(f"Downloading ChromeDriver: {download_url}")
        response = requests.get(download_url, stream=True)
        if response.status_code == 200:
            with open(file_name, 'wb') as file:
                for chunk in response.iter_content(chunk_size=1024):
                    file.write(chunk)
            logger.info(f"ChromeDriver downloaded to: {file_name}")
        else:
            raise Exception("Failed to download ChromeDriver.")
        return file_name
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Network error while downloading ChromeDriver: {e}")
        raise Exception("Network error occurred during ChromeDriver download.") from e
    
    except Exception as e:
        logger.error(f"Error occurred while downloading ChromeDriver: {e}")
        raise Exception("An error occurred during ChromeDriver download.") from e
    

def extract_chromedriver(file_path, extract_to=CHROMEDRIVER_FOLDER):
    """Extract the downloaded ChromeDriver."""
    if file_path.endswith(".zip"):
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
        logger.info(f"ChromeDriver extracted to: {extract_to}")
        # Delete the zip file after extraction
        os.remove(file_path)
        logger.info(f"Deleted ChromeDriver zip file: {file_path}")
    else:
        raise Exception("Only ZIP files are supported for extraction.")

def replace_chromedriver(directory):
    """Replace ChromeDriver in the specified directory."""
    try:
        # Step 1: Get the latest ChromeDriver version
        version, downloads = get_latest_chromedriver_version()
        logger.info(f"Latest ChromeDriver version: {version}")

        platform = os.name
        if platform == "nt":
            driver_info = next(item for item in downloads if "win64" in item["url"])
        elif platform == "posix" and os.uname().sysname == "Linux":
            driver_info = next(item for item in downloads if "linux64" in item["url"])
        elif platform == "posix" and os.uname().sysname == "Darwin":
            driver_info = next(item for item in downloads if "mac-x64" in item["url"])
        else:
            raise Exception("Unsupported platform.")

        download_url = driver_info["url"]
        downloaded_file = download_chromedriver(download_url)
        extract_chromedriver(downloaded_file)

        logger.info("Checking and replacing ChromeDriver in SkuTool directory.")
        logger.info("Replacing ChromeDriver in specified directories...")
        
         # Step 2: Replace ChromeDriver in all subdirectories
        for root, _, files in os.walk(directory):
            try:
                file_path = os.path.join(root, "chromedriver.exe")
                if "chromedriver.exe" in files:
                    os.remove(file_path)
                    logger.info(f"Removed ChromeDriver: {file_path}")
                else:
                    logger.warning(f"ChromeDriver not found in {root}, adding a new one.")

                shutil.copy(os.path.join(CHROMEDRIVER_FOLDER, CHROMEDRIVER_FILE_test), file_path)
                logger.info(f"Replaced or added ChromeDriver at: {file_path}")

            except Exception as e:
                logger.error(f"Failed to replace ChromeDriver at {file_path}: {e}")

        # Step 3: Clean up downloaded ChromeDriver ZIP file and extracted files
        try:
            if os.path.exists(downloaded_file):
                os.remove(downloaded_file)
                logger.info(f"Deleted downloaded ChromeDriver ZIP file: {downloaded_file}")

            if os.path.exists(CHROMEDRIVER_FOLDER):
                shutil.rmtree(CHROMEDRIVER_FOLDER)
                logger.info(f"Deleted extracted ChromeDriver folder: {CHROMEDRIVER_FOLDER}")
        except Exception as e:
            logger.error(f"Failed to clean up ChromeDriver files: {e}")
    except Exception as e:
        logger.error(f"Error occurred while replacing ChromeDriver: {e}")

def delete_temp_log_files(directory):
    """Delete all TempLog folders and their contents."""
    for root, dirs, _ in os.walk(directory):
        if "TempLog" in dirs:
            temp_log_path = os.path.join(root, "TempLog")
            try:
                # Remove all contents inside the TempLog folder
                for item in os.listdir(temp_log_path):
                    item_path = os.path.join(temp_log_path, item)
                    if os.path.isfile(item_path) or os.path.islink(item_path):
                        os.unlink(item_path)  # Remove file or link
                    elif os.path.isdir(item_path):
                        shutil.rmtree(item_path)  # Remove directory
                logger.info(f"Cleared contents of TempLog folder: {temp_log_path}")
            except Exception as e:
                logger.error(f"Failed to clear contents of TempLog folder {temp_log_path}: {e}")

def safe_remove(file_path):
    """安全刪除文件，避免異常導致崩潰。"""
    with contextlib.suppress(FileNotFoundError, PermissionError):
        os.remove(file_path)

def is_valid_extracted(extract_path):
    """檢查解壓後的目錄是否有效（存在且非空）。"""
    return os.path.isdir(extract_path) and os.listdir(extract_path)

def download_and_extract(ftp, local_folder):
    """下載並解壓 FTP 伺服器上的有效文件。"""
    def download_file(ftp, remote_filename, local_path):
        """下載 FTP 文件。"""
        logger.info(f"Downloading: {remote_filename} -> {local_path}")
        with open(local_path, 'wb') as f:
            ftp.retrbinary(f"RETR {remote_filename}", f.write)
        logger.info(f"Download completed: {local_path}")

    def extract_file(local_path, extract_path):
        """解壓 7z 文件到指定文件夾。"""
        logger.info(f"Extracting: {local_path} -> {extract_path}")
        os.makedirs(extract_path, exist_ok=True)
        with py7zr.SevenZipFile(local_path, mode='r') as z:
            z.extractall(path=extract_path)

        if is_valid_extracted(extract_path):
            safe_remove(local_path)
            logger.info(f"Extraction successful: {extract_path}")
        else:
            logger.warning(f"Extraction failed: {extract_path} is empty.")
    
    def handle_existing_version(extract_path):
        """處理已存在的版本。"""
        logger.info(f"Version exists: {extract_path}, updating ChromeDriver.")
        delete_temp_log_files(extract_path)
        replace_chromedriver(extract_path)
    
    try:
        with contextlib.suppress(Exception):  # 防止 `ftp.nlst()` 失敗
            filenames = ftp.nlst()

        if not filenames:
            logger.warning("No files found on FTP.")
            return

        logger.info(f"Files on FTP: {filenames}")

        for filename in filenames:
            if not re.match(VERSION_REGEX, filename):
                logger.debug(f"Skipping: {filename} (pattern mismatch)")
                continue

            local_path = os.path.join(local_folder, filename)
            extract_path = os.path.join(local_folder, filename.replace('.7z', ''))

            if os.path.isdir(extract_path) or os.path.exists(local_path):
                handle_existing_version(extract_path)
                continue
            
            delete_old_versions(local_folder)
            download_file(ftp, filename, local_path)
            extract_file(local_path, extract_path)

            if is_valid_extracted(extract_path):
                replace_chromedriver(extract_path)

    except Exception as e:
        logger.error(f"Error during download and extraction: {e}")

def monitor_templog_for_matrix(gateway_ip,local_folder, recipients):
    """Monitor the TempLog folder for the creation of matrix.xlsx."""
    logger.info("Starting monitor for matrix.xlsx in TempLog folder.")
    while not matrix_detected.is_set():
        matrix_file_path = os.path.join(local_folder, "TempLog\matrix.xlsx")
        logger.info("測試中...")
        time.sleep(1)
        if os.path.exists(matrix_file_path):
            logger.info(f"Detected matrix.xlsx at: {matrix_file_path}")
            create_zip_and_send_email(gateway_ip,recipients)
            matrix_detected.set()
        time.sleep(1)  # Poll every second

def execute_batch_file(gateway_ip,directory,recipients):
    """Execute the batch file in the directory."""
    matrix_detected.clear()

    def start_monitor_thread(root, recipients):
        """啟動監視暫存日誌的執行緒，以偵測 Matrix 訊號。"""
        monitor_thread = threading.Thread(
            target=monitor_templog_for_matrix, args=(gateway_ip, root, recipients), daemon=True
        )
        monitor_thread.start()
        return monitor_thread
    
    def execute_command(command):
        """執行 Shell 命令，並返回 Process 物件。"""
        try:
            logger.info(f"Executing command: {command}")
            return subprocess.Popen(command, shell=True)
        except Exception as e:
            logger.error(f"Failed to start process: {e}")
            return None

    def terminate_process(process):
        """若 Process 存在且仍在執行中，則終止。"""
        if process and process.poll() is None:
            logger.info("Terminating process...")
            process.terminate()

    try:
        # 找到第一個符合條件的批次文件
        batch_file_path = next(
            (os.path.join(root, BATCH_FILE_NAME) for root, _, files in os.walk(directory) if BATCH_FILE_NAME in files),
            None
        )

        if not batch_file_path:
            logger.warning("Batch file not found in the directory.")
            return None

        root = os.path.dirname(batch_file_path)
        os.chdir(root)
        logger.info(f"Found batch file: {batch_file_path}")

        # 定義執行命令
        # 可再優化----------------------------------------------------
        # command = (
        #     '@echo off & (echo. & echo. & echo. & echo.) | '
        #     'SkuTest ".\\localization\\Dummy_V5-0.json" -db -aq -dltl'
        # )
        
        # 精簡測試
        command = (
            '@echo off & (echo. & echo. & echo. & echo.) | '
            'SkuTest ".\\localization\\Dummy_V5-0.json" -db -aq -dltl -reg -rmbl -rmsg'
        )
        ## SkuTest ".\localization\Dummy_V5-0.json" -db -aq -awbip -dltl -reg -rmbl -rmsg
        #  ----------------------------------------------------------
        # 啟動監視執行緒
        monitor_thread = start_monitor_thread(root, recipients)
                
        # 執行批次文件
        logger.info("Starting batch process...")
        process = execute_command(command)
        if not process:
            return None
        
         # 切換網路設定
        time.sleep(5)
        set_ip_metric_for_gateway(gateway_ip, 1)

        logger.info("正在測試.......................")

        # 監視執行狀態
        while process.poll() is None:
            if matrix_detected.is_set():
                logger.info("Matrix detected. Terminating batch process.")
                terminate_process(process)
                break
            time.sleep(0.5)  # 避免忙等 (busy waiting)
        
        logger.info("Batch process completed successfully.")


    except Exception as e:
        logger.error(f"Unexpected error occurred: {e}")
            
    finally:
            # 確保批次進程已終止
            terminate_process(process)
            logger.info("Resources cleaned up.")

    return root


def create_zip_and_send_email(gateway_ip,recipients):
   # 檢查所需檔案是否存在
    set_ip_metric_for_gateway(gateway_ip, 0)
    source_dir = "Templog"
    if not os.path.exists(source_dir):
        logger.info(f"Directory not found: {source_dir}")
        return
    
    # 使用正則表達式匹配檔案名稱中是否包含 [PASS] 或 [FAIL] 字串，不區分大小寫
    file_name_pattern = r'[pP][aA][sS][sS]|\[fF][aA][iI][lL]'  # 匹配 [PASS] 或 [FAIL] 字串

    # 用來存放找到的檔案名稱
    found_file_name = None

    # 搜索資料夾中的檔案
    for root, dirs, files in os.walk(source_dir):
        for file in files:
            # 檢查檔案名稱是否包含 [PASS] 或 [FAIL]，不區分大小寫
            if re.search(file_name_pattern, file):
                found_file_name = file  # 記錄找到的檔案名稱
                break  # 只抓取第一個符合條件的檔案

        if found_file_name:
            break  # 一旦找到第一個檔案，就跳出外層迴圈

    # 顯示找到的檔案名稱
    if found_file_name:
        logger.info(f"找到的檔案名稱是: {found_file_name}")
        
        # 設定壓縮檔案名稱為找到的檔案名稱並加上 .zip
        zip_file_name = found_file_name + '.zip'
        zip_file_path = os.path.join(os.path.dirname(source_dir), zip_file_name)

        # 壓縮資料夾
        shutil.make_archive(zip_file_path.replace('.zip', ''), 'zip', source_dir)
        logger.info(f"資料夾已經壓縮成 {zip_file_path}")
        
        # 確保檔案名稱正確，避免多加 .zip
        zip_filename = zip_file_path.replace('.zip.zip', '.zip')
        
        # 發送郵件
        subject = f"SKU Test Result Report - {found_file_name} {CURRENT_TIME}"

        send_email(recipients, subject, zip_filename)

def check_stop(ftp=None):
    """檢查是否中止，若是則清理資源並返回 True"""
    if stop_event.is_set():
        logger.info("操作已中止")
        if ftp:
            with contextlib.suppress(Exception):  # 確保 ftp.quit() 不會導致新的錯誤
                ftp.quit()
        return True
    return False
# 處理檔案的主函數
def download_and_process_files(start_button,recipients,local_folder):
    ftp = None  # 先定義 ftp，以防發生錯誤時無法關閉
    try:
        if check_stop():
            return
        
        gateway_ip = get_default_gateway()
        set_ip_metric_for_gateway(gateway_ip, 0)

        logger.info("Connecting to the FTP server")
        ftp = FTP(FTP_HOST)
        ftp.login(user=FTP_USER, passwd=FTP_PASS)
        ftp.cwd(TARGET_FOLDER)

        # **步驟 1: 下載並解壓文件**
        if check_stop(ftp):
            return
        
        download_and_extract(ftp, local_folder)

        if check_stop(ftp):
            return
        
        # **步驟 2: 執行批次檔案**
        extract_path = execute_batch_file(gateway_ip, local_folder, recipients)

        if check_stop():
            return
    
    except Exception as e:
        logger.error(f"發生錯誤：{e}")
    
    finally:
        # 無論如何都要確保 FTP 連線關閉，並重新啟用按鈕
        if ftp:
            with contextlib.suppress(Exception):
                ftp.quit()
        start_button.configure(state='normal')


        
def send_email(recipients, subject, attachment_path):
    """Send an email with the given attachment."""
    if not os.path.exists(attachment_path):
        logger.error(f"Attachment not found: {attachment_path}")
        return
    try:
        body = (
            f"Hi,\n\nPlease find the attached test result report.\n\n"
            f"Test Date: {CURRENT_TIME}\n"
            f"If further assistance is needed, contact support.\n\n"
            f"Best Regards,\nTest Automation System"
        )
        recipients = recipient_entries
        logger.info(f"收件人列表: {recipient_entries}")
        # Create the email
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = ", ".join(recipient_entries)
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        # Add attachment if provided
        if attachment_path:
            try:
                with open(attachment_path, 'rb') as attachment:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment.read())
                    encoders.encode_base64(part)
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename={os.path.basename(attachment_path)}'
                    )
                    msg.attach(part)
            except Exception as e:
                logger.error(f"Failed to attach file: {e}")
                return
        # Send the email using Gmail SMTP server
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        text = msg.as_string()
        server.sendmail(sender_email, recipients, text)
        time.sleep(20)
        server.quit()
        logger.info("Email sent successfully.")
        
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
# 按鈕觸發的函數

def main():
    global recipient_entries
    global logger
    global entry_email
    global frame_recipients
    global email_history
    recipient_entries = []
    local_folder = os.getcwd()

    
    # 主視窗設定
    root = tk.Tk()
    root.title("SKU Test Tool") 
    root.geometry("1440x900")  # 設定視窗大小，範例：800x600
    root.config(bg="#2e2e2e")  # 設置背景顏色

    # 定義字型
    bold_font = font.Font(family='Arial', size=14, weight='bold')
    button_font = font.Font(family='Arial', size=14, weight='bold')
    checkbox_font = font.Font(family='Arial', size=12, weight='bold')

    # 建立滾動區域來顯示收件人
    frame_recipients = tk.Frame(root, bg="#333333")
    frame_recipients.pack(pady=5, fill=tk.X)

    # 儲存所有收件人輸入欄位的列表
    email_frame = tk.Frame(root, bg="#333333")
    email_frame.pack(pady=5)

    entry_email = tk.Entry(email_frame, font=button_font, width=40)
    entry_email.grid(row=0, column=0, padx=5, pady=5)

    # 新增按鈕
    btn_add_recipient = tk.Button(
        email_frame, text="新增收件人", font=button_font, fg="blue", bg="#444444", command=add_recipient
    )
    btn_add_recipient.grid(row=0, column=1, padx=5, pady=5)

    # 歷史收件人按鈕
    history_button = tk.Button(
        email_frame, text="選擇歷史信箱", font=button_font, fg="blue", bg="#444444", command=lambda: open_email_selection(root)
    )
    history_button.grid(row=0, column=2, padx=5, pady=5)

    # 主內容框架（Checkbox 在左，收件人列表在右）
    main_frame = tk.Frame(root, bg="#2e2e2e")
    main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    # Checkbox 框架
    checkbox_frame = tk.Frame(main_frame, bg="#333333")
    checkbox_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

    selected_option = tk.IntVar()

    checkbox1 = tk.Radiobutton(checkbox_frame, text="ExecuteTestCase_SQ_SkuSetting", variable=selected_option, value=1, font=checkbox_font, bg="#333333", fg="white", selectcolor="#444444", anchor='w')
    checkbox1.pack(fill=tk.X, padx=10, pady=2)
    
    checkbox2 = tk.Radiobutton(checkbox_frame, text="ExecuteTestCase_SQ_AutoQuery(AcAxQuickRelease)", variable=selected_option, value=2, font=checkbox_font, bg="#333333", fg="white", selectcolor="#444444", anchor='w')
    checkbox2.pack(fill=tk.X, padx=10, pady=2)
    
    checkbox3 = tk.Radiobutton(checkbox_frame, text="ExecuteTestCase_SQ_AutoQuery", variable=selected_option, value=3, font=checkbox_font, bg="#333333", fg="white", selectcolor="#444444", anchor='w')
    checkbox3.pack(fill=tk.X, padx=10, pady=2)

    checkbox4 = tk.Radiobutton(checkbox_frame, text="ExecuteTestCase_SQ_SkuSetting", variable=selected_option, value=4, font=checkbox_font, bg="#333333", fg="white", selectcolor="#444444", anchor='w')
    checkbox4.pack(fill=tk.X, padx=10, pady=2)
    
    checkbox5 = tk.Radiobutton(checkbox_frame, text="ExecuteTestCase_SQ_SkuSetting", variable=selected_option, value=5, font=checkbox_font, bg="#333333", fg="white", selectcolor="#444444", anchor='w')
    checkbox5.pack(fill=tk.X, padx=10, pady=2)
    
    checkbox6 = tk.Radiobutton(checkbox_frame, text="ExecuteTestCase_UI_AutoQuery", variable=selected_option, value=6, font=checkbox_font, bg="#333333", fg="white", selectcolor="#444444", anchor='w')
    checkbox6.pack(fill=tk.X, padx=10, pady=2)

    # 收件人列表框架（增加滾動條）
    recipient_frame_container = Frame(main_frame, bg="#222222", bd=2, relief=tk.GROOVE)
    recipient_frame_container.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    label_recipient_list = tk.Label(
        recipient_frame_container, text="收件人列表", font=bold_font, bg="#222222", fg="white"
    )
    label_recipient_list.pack(anchor="w", padx=5, pady=5)
    
    canvas = Canvas(recipient_frame_container, bg="#333333")
    scrollbar = Scrollbar(recipient_frame_container, orient="vertical", command=canvas.yview)
    frame_recipients = Frame(canvas, bg="#333333")
    
    frame_recipients.bind(
        "<Configure>", lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )
    
    canvas.create_window((0, 0), window=frame_recipients, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # 日誌顯示區域
    log_text = scrolledtext.ScrolledText(
        root, wrap=tk.WORD, state='disabled', height=20, width=200, bg="#000000", fg="#39ff14", font=("Courier New", 10)
    )
    log_text.pack(padx=10, pady=10)
    log_text.configure(bg="black", fg="#39ff14")  # 設定黑底綠字

    # 設定 Logger
    logger = setup_logger(log_text)

    # 按鈕區域框架，置中顯示
    button_frame = tk.Frame(root, bg="#2e2e2e")
    button_frame.pack(pady=10)

    # START 按鈕
    start_button = tk.Button(
        button_frame, text="START", font=bold_font, fg="green", bg="#444444",
        command=lambda: start_process(start_button, stop_button,local_folder)
    )
    start_button.grid(row=0, column=0, padx=10, pady=5)

    # 停止按鈕
    stop_button = tk.Button(
        button_frame, text="STOP", font=bold_font, fg="orange", bg="#444444",
        command=lambda: stop_process(start_button, stop_button),
        state='disabled'  # 初始化為禁用狀態
    )
    stop_button.grid(row=0, column=1, padx=10, pady=5)

    # 清除日誌按鈕
    clear_button = tk.Button(
        button_frame, text="CLEAN", font=bold_font, fg="red", bg="#444444",
        command=lambda: clear_log(log_text)
    )
    clear_button.grid(row=0, column=2, padx=10, pady=5)

    # 使行和列自動擴展
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)
    root.protocol("WM_DELETE_WINDOW", lambda: (save_emails(), root.destroy()))
    root.mainloop()

email_history = load_emails()
# 主程式 GUI
if __name__ == "__main__":
    main()