import tkinter as tk
from tkinter import ttk
import pyautogui
import time
import threading

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Automation Tool")

        self.action_var = tk.StringVar(value="click")
        self.keys_var1 = tk.StringVar(value="F1")
        self.keys_var2 = tk.StringVar(value="")
        self.keys_var3 = tk.StringVar(value="")
        self.string_var = tk.StringVar()
        self.x_var = tk.StringVar()
        self.y_var = tk.StringVar()

        self.create_widgets()

    def create_widgets(self):
        actions = [("Click", "click"), ("Dbl. Click", "dbl_click"), ("R. Click", "r_click"), ("Key", "key"), ("Type", "type")]
        keys = ["", "F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12",
                "esc", "tab", "capslock", "shift", "ctrl", "win", "alt", "space", "altgr", "enter", "backspace", "delete"]

        for text, value in actions:
            rb = tk.Radiobutton(self.root, text=text, variable=self.action_var, value=value, command=self.update_ui)
            rb.pack(anchor="w")

        self.x_label = tk.Label(self.root, text="X:")
        self.x_entry = tk.Entry(self.root, textvariable=self.x_var)
        self.y_label = tk.Label(self.root, text="Y:")
        self.y_entry = tk.Entry(self.root, textvariable=self.y_var)
        
        self.key_label1 = tk.Label(self.root, text="Key 1:")
        self.key_dropdown1 = ttk.Combobox(self.root, values=keys, textvariable=self.keys_var1)
        
        self.key_label2 = tk.Label(self.root, text="Key 2:")
        self.key_dropdown2 = ttk.Combobox(self.root, values=keys, textvariable=self.keys_var2)

        self.key_label3 = tk.Label(self.root, text="Key 3:")
        self.key_dropdown3 = ttk.Combobox(self.root, values=keys, textvariable=self.keys_var3)
        
        self.string_label = tk.Label(self.root, text="String:")
        self.string_entry = tk.Entry(self.root, textvariable=self.string_var)

        self.start_button = tk.Button(self.root, text="Start", command=self.start_action)
        self.start_button.pack()

        self.update_ui()

    def update_ui(self):
        self.x_label.pack_forget()
        self.x_entry.pack_forget()
        self.y_label.pack_forget()
        self.y_entry.pack_forget()
        self.key_label1.pack_forget()
        self.key_dropdown1.pack_forget()
        self.key_label2.pack_forget()
        self.key_dropdown2.pack_forget()
        self.key_label3.pack_forget()
        self.key_dropdown3.pack_forget()
        self.string_label.pack_forget()
        self.string_entry.pack_forget()

        action = self.action_var.get()
        if action in ("click", "dbl_click", "r_click"):
            self.x_label.pack()
            self.x_entry.pack()
            self.y_label.pack()
            self.y_entry.pack()
        elif action == "key":
            self.key_label1.pack()
            self.key_dropdown1.pack()
            self.key_label2.pack()
            self.key_dropdown2.pack()
            self.key_label3.pack()
            self.key_dropdown3.pack()
        elif action == "type":
            self.string_label.pack()
            self.string_entry.pack()

    def start_action(self):
        threading.Thread(target=self.execute_action).start()

    def execute_action(self):
        time.sleep(3)  # 3 seconds delay
        action = self.action_var.get()
        if action in ("click", "dbl_click", "r_click"):
            x = int(self.x_var.get())
            y = int(self.y_var.get())
            if action == "click":
                pyautogui.click(x, y)
            elif action == "dbl_click":
                pyautogui.doubleClick(x, y)
            elif action == "r_click":
                pyautogui.rightClick(x, y)
        elif action == "key":
            keys = [self.keys_var1.get(), self.keys_var2.get(), self.keys_var3.get()]
            keys = [key for key in keys if key]  # Filter out empty strings
            pyautogui.hotkey(*keys)
        elif action == "type":
            pyautogui.typewrite(self.string_var.get())

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
