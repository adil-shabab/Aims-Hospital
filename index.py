import time
import pyautogui

# Delay to switch to the email window
time.sleep(3)

# Move to 'Select All' checkbox (Adjust X, Y based on screen)
pyautogui.moveTo(100, 200, duration=1)  
pyautogui.click()

# Wait for emails to be selected
time.sleep(1)

# Move to 'Mark as Read' button (Adjust X, Y based on screen)
pyautogui.moveTo(300, 100, duration=1)  
pyautogui.click()

# Wait for action to complete
time.sleep(2)

print("✅ All emails marked as read!")
