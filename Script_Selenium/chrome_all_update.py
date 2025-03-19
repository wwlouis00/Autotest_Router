import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup

def auto_update_chrome():
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

        # 取得頁面的 HTML
        page_source = driver.page_source

        # 使用 BeautifulSoup 解析頁面內容
        soup = BeautifulSoup(page_source, "html.parser")

        # 查找是否有包含 "Chrome is up to date" 的提示
        update_status_div = soup.find("div", id="updateStatusMessage")
        if update_status_div and "Chrome is up to date" in update_status_div.get_text():
            print("Chrome 已是最新版本。")
        else:
            print("Chrome 可能需要更新。")

        # 繼續檢查更新狀態
        while True:
            try:
                # 檢查是否有 "正在檢查更新" 的提示
                updating_text = driver.find_element(By.XPATH, "//*[contains(text(), '正在檢查更新')]")
                print("正在更新，請稍候...")
            except:
                # 如果沒有更新提示，則顯示可能已經是最新版本
                print("未檢測到更新提示，可能已是最新版本。")
                break

            # 每隔 5 秒檢查一次更新狀態
            time.sleep(5)

    except Exception as e:
        print(f"自動更新失敗: {e}")

    finally:
        # 關閉瀏覽器
        driver.quit()
        print("任務完成，瀏覽器已關閉。")

if __name__ == "__main__":
    auto_update_chrome()
