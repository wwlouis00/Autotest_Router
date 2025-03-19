import os
import tkinter as tk
from gui import create_gui
from functions import start_process, stop_process, clear_log

# 啟動 GUI
def main():
    root = tk.Tk()
    root.title("SKU Test Tool")
    root.geometry("900x600")
    root.config(bg="#2e2e2e")

    selected_option, log_text, start_button, stop_button = create_gui(root)

    # 綁定按鈕事件
    start_button.config(command=lambda: start_process(start_button, stop_button, os.getcwd(), selected_option.get(), log_text))
    stop_button.config(command=lambda: stop_process(start_button, stop_button, log_text))
    
    root.mainloop()

if __name__ == "__main__":
    main()
