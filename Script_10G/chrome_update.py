from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time

def check_chrome_update_status():
    # 配置 Chrome Driver
    chrome_options = Options()
    chrome_options.add_argument("--remote-allow-origins=*")  # 避免跨源問題
    chrome_options.add_argument("--start-maximized")  # 最大化窗口
    
    # 使用 WebDriver Manager 自動下載和配置最新版本的 ChromeDriver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    try:
        # 打開 Chrome 的幫助頁面
        driver.get("chrome://settings/help")
        print("已導航到 chrome://settings/help")

        # 等待頁面加載
        time.sleep(5)

        # 檢查是否顯示 "Chrome 目前是最新版本"
        try:
            # 找到更新狀態消息
            update_status_message = driver.find_element(By.ID, "updateStatusMessage")
            alert_message = update_status_message.find_element(By.XPATH, ".//div[@role='alert']").text
            if "Chrome 目前是最新版本" in alert_message:
                print("Chrome 已是最新版本")
            else:
                print("Chrome 可能需要更新或出現錯誤")
        except Exception as e:
            print(f"檢查更新狀態時發生錯誤: {e}")

    except Exception as e:
        print(f"自動檢查失敗: {e}")

    finally:
        # 關閉瀏覽器
        driver.quit()
        print("任務完成，瀏覽器已關閉。")

if __name__ == "__main__":
    check_chrome_update_status()
