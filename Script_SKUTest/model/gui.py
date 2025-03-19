import tkinter as tk
from tkinter import font, scrolledtext
from functions import clear_log


def create_gui(root):
    """ 建立 GUI 介面 """
    bold_font = font.Font(family='Arial', size=14, weight='bold')
    checkbox_font = font.Font(family='Arial', size=12, weight='bold')

    # 建立主框架
    main_frame = tk.Frame(root, bg="#2e2e2e")
    main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # 選項區
    checkbox_frame = tk.Frame(main_frame, bg="#333333")
    checkbox_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

    selected_option = tk.IntVar()

    label_recipient_list = tk.Label(checkbox_frame, text="執行列表", font=bold_font, bg="#222222", fg="white")
    label_recipient_list.pack(anchor="w", padx=5, pady=5)

    checkbox_options = [
        ("ExecuteTestCase_SQ_SkuSetting", 1),
        ("ExecuteTestCase_SQ_AutoQuery(AcAxQuickRelease)", 2),
        ("ExecuteTestCase_SQ_AutoQuery", 3),
        ("ExecuteTestCase_UI_AutoQuery", 4),
    ]

    for text, value in checkbox_options:
        tk.Radiobutton(checkbox_frame, text=text, variable=selected_option, value=value,
                       font=checkbox_font, bg="#333333", fg="white", selectcolor="#444444", anchor='w'
        ).pack(fill=tk.X, padx=5, pady=1)

    # 日誌區
    log_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, state='disabled', height=10, width=100,
                                         bg="black", fg="#39ff14", font=("Courier New", 10))
    log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    # 按鈕框架
    button_frame = tk.Frame(root, bg="#2e2e2e")
    button_frame.pack(pady=10)

    start_button = tk.Button(button_frame, text="START", font=bold_font, fg="green", bg="#444444")
    start_button.grid(row=0, column=0, padx=10, pady=5)

    stop_button = tk.Button(button_frame, text="STOP", font=bold_font, fg="orange", bg="#444444", state='disabled')
    stop_button.grid(row=0, column=1, padx=10, pady=5)

    clear_button = tk.Button(button_frame, text="CLEAN", font=bold_font, fg="red", bg="#444444")
    clear_button.grid(row=0, column=2, padx=10, pady=5)
    
    # 清除日誌按鈕事件
    clear_button.config(command=lambda: clear_log(log_text))

    return selected_option, log_text, start_button, stop_button
