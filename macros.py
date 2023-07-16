import pyautogui
import time

x = int(input())
i = 0
while i < x:
    pyautogui.click(1484, 305)
    time.sleep(4)
    pyautogui.click(262, 419)
    pyautogui.click(1633, 372)
    pyautogui.click(961, 656)
    time.sleep(25)
    i = i + 1
    print(i)

