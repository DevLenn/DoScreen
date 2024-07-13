import tkinter as tk
from tkinter import ttk, filedialog, messagebox, PhotoImage
import pyautogui
import time
import threading
import numpy as np
import cv2
import json
from PIL import Image, ImageTk
import os

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("DoScreen")

        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icon.png')
        if os.path.exists(icon_path):
            icon = PhotoImage(file=icon_path)
            self.root.iconphoto(False, icon)

        self.images = {}
        self.running = False
        self.paused = False
        self.thread = None

        self.create_widgets()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.bind_all("<MouseWheel>", self.on_mouse_wheel)

    def create_widgets(self):
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(self.main_frame)
        self.scroll_frame = ttk.Frame(self.canvas)
        self.scroll_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        self.h_scroll = ttk.Scrollbar(self.main_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.v_scroll = ttk.Scrollbar(self.main_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.canvas.configure(xscrollcommand=self.h_scroll.set, yscrollcommand=self.v_scroll.set)

        self.h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")

        self.add_image_button = tk.Button(self.root, text="Add Image", command=self.add_image)
        self.add_image_button.pack(side=tk.LEFT, padx=10, pady=10)

        self.start_button = tk.Button(self.root, text="Start", command=self.start)
        self.start_button.pack(side=tk.BOTTOM, pady=10)

        self.pause_button = tk.Button(self.root, text="Pause", command=self.toggle_pause)
        self.pause_button.pack(side=tk.BOTTOM, pady=10)

        self.save_button = tk.Button(self.root, text="Save", command=self.save_config)
        self.save_button.pack(side=tk.BOTTOM, pady=10)

        self.load_button = tk.Button(self.root, text="Load", command=self.load_config)
        self.load_button.pack(side=tk.BOTTOM, pady=10)

        self.status_label = tk.Label(self.root, text="Status: Stopped")
        self.status_label.pack(side=tk.BOTTOM, pady=10)

    def on_closing(self):
        if self.thread:
            self.running = False
            self.thread.join()
        self.root.destroy()

    def on_mouse_wheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def add_image(self):
        filepath = filedialog.askopenfilename()
        if filepath:
            image_name = filepath.split("/")[-1]
            self.images[image_name] = {
                "filepath": filepath,
                "actions": [],
                "threshold": 99.0,  # Default value in %
                "delay": 1.0,
                "visible_status": False
            }
            self.update_image_list()

    def update_image_list(self):
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        max_columns = 8
        row = 0
        col = 0

        for image_name, data in self.images.items():
            frame = tk.Frame(self.scroll_frame, bd=2, relief=tk.SUNKEN)
            frame.grid(row=row, column=col, padx=5, pady=5)

            image_label = tk.Label(frame, text=image_name)
            image_label.pack()

            threshold_label = tk.Label(frame, text="Threshold:")
            threshold_label.pack()
            threshold_var = tk.DoubleVar(value=data["threshold"])
            threshold_entry = tk.Entry(frame, textvariable=threshold_var)
            threshold_entry.pack()

            delay_label = tk.Label(frame, text="Delay (seconds):")
            delay_label.pack()
            delay_var = tk.DoubleVar(value=data["delay"])
            delay_entry = tk.Entry(frame, textvariable=delay_var)
            delay_entry.pack()

            action_listbox = tk.Listbox(frame)
            action_listbox.pack()
            action_listbox.bind('<Double-Button-1>', lambda e, image_name=image_name, listbox=action_listbox: self.edit_action(image_name, listbox))

            for action in data["actions"]:
                action_listbox.insert(tk.END, action)

            def add_action(image_name=image_name):
                action_dialog = ActionDialog(self.root)
                self.root.wait_window(action_dialog.top)
                if action_dialog.result:
                    self.images[image_name]["actions"].append(action_dialog.result)
                    self.update_image_list()

            def remove_action(image_name=image_name):
                selected_action_index = action_listbox.curselection()
                if selected_action_index:
                    del self.images[image_name]["actions"][selected_action_index[0]]
                    self.update_image_list()

            add_action_button = tk.Button(frame, text="Add Action", command=add_action)
            add_action_button.pack()

            remove_action_button = tk.Button(frame, text="Remove Action", command=remove_action)
            remove_action_button.pack()

            def remove_image(image_name=image_name):
                del self.images[image_name]
                self.update_image_list()

            remove_image_button = tk.Button(frame, text="Remove Image", command=remove_image)
            remove_image_button.pack()

            img = Image.open(data["filepath"])
            img = img.resize((100, 100), Image.LANCZOS)
            img = ImageTk.PhotoImage(img)
            img_label = tk.Label(frame, image=img)
            img_label.image = img
            img_label.pack()

            col += 1
            if col >= max_columns:
                col = 0
                row += 1

    def start(self):
        if not self.running or self.paused:
            self.running = True
            self.paused = False
            self.status_label.config(text="Status: Running")
            self.thread = threading.Thread(target=self.monitor_screen)
            self.thread.start()

    def toggle_pause(self):
        if self.running:
            self.paused = not self.paused
            self.status_label.config(text="Status: Paused" if self.paused else "Status: Running")
            if not self.paused:
                self.update_image_list()

    def monitor_screen(self):
        while self.running:
            if not self.paused:
                screen_array = self.screenshot_to_gray_array()
                for image_name, data in self.images.items():
                    image_array = self.load_image_to_gray_array(data["filepath"])
                    threshold = data["threshold"] / 100.0
                    found = self.find_image_on_screen(screen_array, image_array, threshold)

                    if found and not data["visible_status"]:
                        for action in data["actions"]:
                            self.execute_action(action)
                            time.sleep(action["delay"])
                        data["visible_status"] = True
                    elif not found:
                        data["visible_status"] = False

                time.sleep(1)

    def load_image_to_gray_array(self, filepath):
        image = cv2.imread(filepath, cv2.IMREAD_GRAYSCALE)
        return image

    def screenshot_to_gray_array(self):
        screenshot = pyautogui.screenshot()
        screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2GRAY)
        return screenshot

    def find_image_on_screen(self, screen_array, image_array, threshold):
        result = cv2.matchTemplate(screen_array, image_array, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, _ = cv2.minMaxLoc(result)
        return max_val >= threshold

    def execute_action(self, action):
        action_type = action["type"]
        if action_type in ("click", "dbl_click", "r_click"):
            x, y = action["x"], action["y"]
            if action_type == "click":
                pyautogui.click(x, y)
            elif action_type == "dbl_click":
                pyautogui.doubleClick(x, y)
            elif action_type == "r_click":
                pyautogui.rightClick(x, y)
        elif action_type == "key":
            keys = action["keys"]
            pyautogui.hotkey(*keys)
        elif action_type == "type":
            pyautogui.typewrite(action["string"])

    def save_config(self):
        config = {"images": self.images}
        filepath = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if filepath:
            with open(filepath, "w") as f:
                json.dump(config, f)
            messagebox.showinfo("Save", "Configuration saved.")

    def load_config(self):
        filepath = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if filepath:
            try:
                with open(filepath, "r") as f:
                    config = json.load(f)
                self.images = config.get("images", {})
                self.update_image_list()
                messagebox.showinfo("Load", "Configuration loaded.")
            except FileNotFoundError:
                messagebox.showwarning("Load", "No configuration file found.")

    def edit_action(self, image_name, listbox):
        selected_action_index = listbox.curselection()
        if selected_action_index:
            action = self.images[image_name]["actions"][selected_action_index[0]]
            action_dialog = ActionDialog(self.root, action)
            self.root.wait_window(action_dialog.top)
            if action_dialog.result:
                self.images[image_name]["actions"][selected_action_index[0]] = action_dialog.result
                self.update_image_list()

class ActionDialog:
    def __init__(self, parent, action=None):
        top = self.top = tk.Toplevel(parent)
        top.title("Edit Action" if action else "Add Action")

        self.action_var = tk.StringVar(value=action["type"] if action else "click")
        self.keys_var1 = tk.StringVar(value=action["keys"][0] if action and action["type"] == "key" else "F1")
        self.keys_var2 = tk.StringVar(value=action["keys"][1] if action and action["type"] == "key" and len(action["keys"]) > 1 else "")
        self.keys_var3 = tk.StringVar(value=action["keys"][2] if action and action["type"] == "key" and len(action["keys"]) > 2 else "")
        self.string_var = tk.StringVar(value=action["string"] if action and action["type"] == "type" else "")
        self.x_var = tk.StringVar(value=action["x"] if action and action["type"] in ("click", "dbl_click", "r_click") else "")
        self.y_var = tk.StringVar(value=action["y"] if action and action["type"] in ("click", "dbl_click", "r_click") else "")
        self.delay_var = tk.StringVar(value=action["delay"] if action else "1.0")

        self.create_widgets()

    def create_widgets(self):
        actions = [("Click", "click"), ("Dbl. Click", "dbl_click"), ("R. Click", "r_click"), ("Key", "key"), ("Type", "type")]
        keys = ["", "F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12", "esc", "tab", "capslock", "shift", "ctrl", "win", "alt", "space", "altgr", "enter", "backspace", "delete"]

        for text, value in actions:
            rb = tk.Radiobutton(self.top, text=text, variable=self.action_var, value=value, command=self.update_ui)
            rb.pack(anchor="w")

        self.x_label = tk.Label(self.top, text="X:")
        self.x_entry = tk.Entry(self.top, textvariable=self.x_var)
        self.y_label = tk.Label(self.top, text="Y:")
        self.y_entry = tk.Entry(self.top, textvariable=self.y_var)

        self.key_label1 = tk.Label(self.top, text="Key 1:")
        self.key_dropdown1 = ttk.Combobox(self.top, values=keys, textvariable=self.keys_var1)

        self.key_label2 = tk.Label(self.top, text="Key 2:")
        self.key_dropdown2 = ttk.Combobox(self.top, values=keys, textvariable=self.keys_var2)

        self.key_label3 = tk.Label(self.top, text="Key 3:")
        self.key_dropdown3 = ttk.Combobox(self.top, values=keys, textvariable=self.keys_var3)

        self.string_label = tk.Label(self.top, text="String:")
        self.string_entry = tk.Entry(self.top, textvariable=self.string_var)

        self.delay_label = tk.Label(self.top, text="Delay (seconds):")
        self.delay_entry = tk.Entry(self.top, textvariable=self.delay_var)

        self.ok_button = tk.Button(self.top, text="OK", command=self.on_ok)
        self.ok_button.pack()

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
        self.delay_label.pack_forget()
        self.delay_entry.pack_forget()

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
        self.delay_label.pack()
        self.delay_entry.pack()

    def on_ok(self):
        result = {
            "type": self.action_var.get(),
            "delay": float(self.delay_var.get())
        }
        if result["type"] in ("click", "dbl_click", "r_click"):
            result["x"] = int(self.x_var.get())
            result["y"] = int(self.y_var.get())
        elif result["type"] == "key":
            result["keys"] = [key for key in (self.keys_var1.get(), self.keys_var2.get(), self.keys_var3.get()) if key]
        elif result["type"] == "type":
            result["string"] = self.string_var.get()

        self.result = result
        self.top.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
