import tkinter as tk

def setup_logger(log_widget):
    """ 設定 Logger 來顯示日誌輸出 """
    def log(message):
        log_widget.config(state=tk.NORMAL)
        log_widget.insert(tk.END, message + "\n")
        log_widget.config(state=tk.DISABLED)
        log_widget.yview(tk.END)
    return log

def start_process(start_button, stop_button, local_folder, selected_value, log_text):
    """ 開始執行測試，顯示選擇的測試項目 """
    log_text.config(state=tk.NORMAL)
    log_text.insert(tk.END, f"執行測試: {selected_value}\n")
    log_text.config(state=tk.DISABLED)
    log_text.yview(tk.END)

    start_button.config(state=tk.DISABLED)
    stop_button.config(state=tk.NORMAL)

def stop_process(start_button, stop_button, log_text):
    """ 停止執行測試 """
    log_text.config(state=tk.NORMAL)
    log_text.insert(tk.END, "測試停止\n")
    log_text.config(state=tk.DISABLED)
    log_text.yview(tk.END)

    start_button.config(state=tk.NORMAL)
    stop_button.config(state=tk.DISABLED)

def clear_log(log_widget):
    """ 清除日誌 """
    log_widget.config(state=tk.NORMAL)
    log_widget.delete("1.0", tk.END)
    log_widget.config(state=tk.DISABLED)
