import tkinter as tk
from tkinter import ttk, filedialog
import pyautogui
import time
import threading
import json
import cv2
import numpy as np
from PIL import Image, ImageTk

class ImageActionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Bild-Erkennungs und Aktions-Werkzeug")
        self.root.configure(bg='#2E2E2E')
        
        self.config = []

        self.canvas = tk.Canvas(root, bg='#2E2E2E')
        self.scrollable_frame = tk.Frame(self.canvas, bg='#2E2E2E')
        
        self.scrollbar = ttk.Scrollbar(root, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.status_label = tk.Label(root, text="Status: Pausiert", bg='#2E2E2E', fg='white')
        self.status_label.pack(side=tk.TOP, anchor='e', padx=10, pady=10)

        self.button_frame = tk.Frame(root, bg='#2E2E2E')
        self.button_frame.pack(fill=tk.X, pady=10)

        self.add_row_button = tk.Button(self.button_frame, text="Bild hinzufügen", command=self.add_image_row, bg='#5E5E5E', fg='white')
        self.add_row_button.pack(side=tk.LEFT, padx=5)
        
        self.start_button = tk.Button(self.button_frame, text="Start", command=self.start_search, bg='#5E5E5E', fg='white')
        self.start_button.pack(side=tk.LEFT, padx=5)

        self.pause_button = tk.Button(self.button_frame, text="Pause", command=self.pause_search, bg='#5E5E5E', fg='white')
        self.pause_button.pack(side=tk.LEFT, padx=5)

        self.save_button = tk.Button(self.button_frame, text="Speichern", command=self.save_config, bg='#5E5E5E', fg='white')
        self.save_button.pack(side=tk.LEFT, padx=5)

        self.load_button = tk.Button(self.button_frame, text="Laden", command=self.load_config, bg='#5E5E5E', fg='white')
        self.load_button.pack(side=tk.LEFT, padx=5)

        self.running = False
        self.paused = True
        self.thread = None

    def add_image_row(self, img_path=None, threshold=None, actions=None):
        frame = tk.Frame(self.scrollable_frame, bg='#3E3E3E', pady=5, padx=5, relief=tk.RIDGE, borderwidth=2)
        frame.pack(fill=tk.X, pady=5)
        
        img_path_var = tk.StringVar(value=img_path if img_path else "")
        threshold_var = tk.DoubleVar(value=threshold if threshold else 0.8)
        action_vars = []

        def browse_image():
            path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])
            img_path_var.set(path)
            img_label.image = ImageTk.PhotoImage(Image.open(path).resize((50, 50)))
            img_label.config(image=img_label.image)

        tk.Button(frame, text="Bild wählen", command=browse_image, bg='#5E5E5E', fg='white').grid(row=0, column=0, padx=5, pady=5)
        tk.Entry(frame, textvariable=img_path_var, width=50).grid(row=0, column=1, padx=5, pady=5)
        img_label = tk.Label(frame, bg='#3E3E3E')
        img_label.grid(row=0, column=2, padx=5, pady=5)

        tk.Label(frame, text="Schwellwert:", bg='#3E3E3E', fg='white').grid(row=1, column=0, padx=5, pady=5)
        tk.Entry(frame, textvariable=threshold_var, width=5).grid(row=1, column=1, padx=5, pady=5)

        actions_frame = tk.Frame(frame, bg='#3E3E3E')
        actions_frame.grid(row=2, column=0, columnspan=3, pady=5)

        if actions:
            for action in actions:
                action_var = {'type': tk.StringVar(value=action['type']), 'x': tk.StringVar(value=action['x']), 'y': tk.StringVar(value=action['y']), 'key': tk.StringVar(value=action['key']), 'text': tk.StringVar(value=action['text'])}
                action_vars.append(action_var)
                self.add_action_row(actions_frame, action_var)
        else:
            action_var = {'type': tk.StringVar(value='click'), 'x': tk.StringVar(), 'y': tk.StringVar(), 'key': tk.StringVar(), 'text': tk.StringVar()}
            action_vars.append(action_var)
            self.add_action_row(actions_frame, action_var)

        tk.Button(frame, text="Aktion hinzufügen", command=lambda: self.add_action_row(actions_frame, action_var), bg='#5E5E5E', fg='white').grid(row=3, column=0, columnspan=3, pady=5)
        tk.Button(frame, text="Bild entfernen", command=lambda: self.remove_image_row(frame), bg='#5E5E5E', fg='white').grid(row=3, column=1, columnspan=3, pady=5)

        self.config.append({'img_path': img_path_var, 'threshold': threshold_var, 'actions': action_vars, 'frame': frame})

    def add_action_row(self, parent_frame, action_var):
        action_frame = tk.Frame(parent_frame, bg='#4E4E4E', pady=2, padx=2, relief=tk.SUNKEN)
        action_frame.pack(fill=tk.X, pady=2)

        tk.Label(action_frame, text="Aktion:", bg='#4E4E4E', fg='white').pack(side=tk.LEFT, padx=5)
        tk.OptionMenu(action_frame, action_var['type'], 'click', 'dbl_click', 'r_click', 'key', 'type').pack(side=tk.LEFT, padx=5)
        tk.Label(action_frame, text="X:", bg='#4E4E4E', fg='white').pack(side=tk.LEFT, padx=5)
        tk.Entry(action_frame, textvariable=action_var['x'], width=5).pack(side=tk.LEFT, padx=5)
        tk.Label(action_frame, text="Y:", bg='#4E4E4E', fg='white').pack(side=tk.LEFT, padx=5)
        tk.Entry(action_frame, textvariable=action_var['y'], width=5).pack(side=tk.LEFT, padx=5)
        tk.Label(action_frame, text="Taste:", bg='#4E4E4E', fg='white').pack(side=tk.LEFT, padx=5)
        tk.Entry(action_frame, textvariable=action_var['key'], width=10).pack(side=tk.LEFT, padx=5)
        tk.Label(action_frame, text="Text:", bg='#4E4E4E', fg='white').pack(side=tk.LEFT, padx=5)
        tk.Entry(action_frame, textvariable=action_var['text'], width=10).pack(side=tk.LEFT, padx=5)
        tk.Button(action_frame, text="Aktion entfernen", command=lambda: self.remove_action_row(parent_frame, action_frame, action_var), bg='#5E5E5E', fg='white').pack(side=tk.LEFT, padx=5)

    def remove_image_row(self, frame):
        frame.destroy()
        self.config = [item for item in self.config if item['frame'] != frame]

    def remove_action_row(self, parent_frame, action_frame, action_var):
        action_frame.destroy()
        for item in self.config:
            if item['frame'] == parent_frame:
                item['actions'].remove(action_var)
                break

    def start_search(self):
        self.running = True
        self.paused = False
        self.update_status_label()
        if not self.thread or not self.thread.is_alive():
            self.thread = threading.Thread(target=self.search_loop)
            self.thread.start()

    def pause_search(self):
        self.paused = not self.paused
        self.update_status_label()

    def update_status_label(self):
        status_text = "Status: Laufend" if self.running and not self.paused else "Status: Pausiert"
        self.status_label.config(text=status_text)

    def search_loop(self):
        seen_images = {config['img_path'].get(): False for config in self.config}
        while self.running:
            if self.paused:
                time.sleep(1)
                continue
            screen_array = self.screenshot_to_gray_array()
            for item in self.config:
                img_array = self.load_image_to_gray_array(item['img_path'].get())
                threshold = item['threshold'].get()
                img_path = item['img_path'].get()
                found = self.find_image_on_screen(screen_array, img_array, threshold)
                if found:
                    if not seen_images[img_path]:
                        self.execute_actions(item['actions'])
                        seen_images[img_path] = True
                else:
                    seen_images[img_path] = False
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

    def execute_actions(self, actions):
        for action in actions:
            action_type = action['type'].get()
            x = action['x'].get()
            y = action['y'].get()
            key = action['key'].get()
            text = action['text'].get()
            if action_type == 'click':
                pyautogui.click(int(x), int(y))
            elif action_type == 'dbl_click':
                pyautogui.doubleClick(int(x), int(y))
            elif action_type == 'r_click':
                pyautogui.rightClick(int(x), int(y))
            elif action_type == 'key':
                pyautogui.press(key)
            elif action_type == 'type':
                pyautogui.typewrite(text)

    def save_config(self):
        config = []
        for item in self.config:
            config.append({
                'img_path': item['img_path'].get(),
                'threshold': item['threshold'].get(),
                'actions': [{'type': action['type'].get(), 'x': action['x'].get(), 'y': action['y'].get(), 'key': action['key'].get(), 'text': action['text'].get()} for action in item['actions']]
            })
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if file_path:
            with open(file_path, 'w') as file:
                json.dump(config, file, indent=4)

    def load_config(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if file_path:
            with open(file_path, 'r') as file:
                config = json.load(file)
            for widget in self.scrollable_frame.winfo_children():
                widget.destroy()
            self.config = []
            for item in config:
                self.add_image_row(item['img_path'], item['threshold'], item['actions'])

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageActionApp(root)
    root.mainloop()
