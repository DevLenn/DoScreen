import numpy as np
import cv2
import pyautogui
import time

def load_image_to_gray_array(filepath):
    image = cv2.imread(filepath, cv2.IMREAD_GRAYSCALE)
    return image

def screenshot_to_gray_array():
    screenshot = pyautogui.screenshot()
    screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2GRAY)
    return screenshot

def find_image_on_screen(screen_array, image_array, threshold):
    result = cv2.matchTemplate(screen_array, image_array, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, _ = cv2.minMaxLoc(result)
    return max_val >= threshold

def main():
    test1_array = load_image_to_gray_array(/path/to/file) #NEED TO EDIT
    test2_array = load_image_to_gray_array(/path/to/file) #NEED TO EDIT

    # Set thresholds for each image
    threshold_test1 = 0.995  # Threshold for test1.png
    threshold_test2 = 0.992  # Threshold for test2.png

    while True:
        screen_array = screenshot_to_gray_array()

        test1_found = find_image_on_screen(screen_array, test1_array, threshold_test1)
        test2_found = find_image_on_screen(screen_array, test2_array, threshold_test2)

        if test1_found and test2_found:
            print("Both images are visible on the screen.")
        elif test1_found:
            print("Test1 image is visible on the screen.")
        elif test2_found:
            print("Test2 image is visible on the screen.")
        else:
            print("None of the images are visible on the screen.")

        time.sleep(1)

if __name__ == "__main__":
    main()
