from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re

# Setup
options = Options()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 15)

try:
    # Step 1: Go to MyPursu login page
    driver.get("https://dev.mypursu.com/sign-in")

    # Step 2: Enter email
    email_input = wait.until(EC.visibility_of_element_located((By.ID, "emailID")))
    email_input.send_keys("nane@yopmail.com")

    # Step 3: Accept Terms and Conditions
    terms_checkbox = wait.until(EC.presence_of_element_located((By.ID, "termsConditions")))
    driver.execute_script("arguments[0].scrollIntoView(true);", terms_checkbox)
    if not terms_checkbox.is_selected():
        terms_checkbox.click()
        print("✅ Terms and Conditions accepted.")

    time.sleep(1)

    # Step 4: Click Continue
    continue_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Continue')]")
    continue_btn.click()

    # Step 5: Open YOPMAIL in new tab
    driver.execute_script("window.open('');")
    driver.switch_to.window(driver.window_handles[1])
    driver.get("https://yopmail.com/?login=nane")
    time.sleep(2)

    # Step 6: Read OTP from email
    driver.switch_to.default_content()
    wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, "ifmail")))
    mail_body = wait.until(EC.presence_of_element_located((By.TAG_NAME, "body"))).text

    otp_match = re.search(r"\b(\d{6})\b", mail_body)
    if not otp_match:
        raise Exception("❌ OTP not found in email.")
    otp = otp_match.group(1)
    print("✅ OTP Received:", otp)

    # Step 7: Switch back to MyPursu tab
    driver.switch_to.default_content()
    driver.switch_to.window(driver.window_handles[0])

    # Wait for OTP fields to appear
    wait.until(EC.presence_of_element_located((By.ID, "inputs")))
    otp_inputs = driver.find_elements(By.XPATH, "//*[@id='inputs']//input[@type='text']")

    if len(otp_inputs) != 6:
        raise Exception(f"❌ Expected 6 OTP fields, but found {len(otp_inputs)}")

    time.sleep(1)

    # Step 8: Enter OTP slowly like a human
    for i, digit in enumerate(otp):
        otp_inputs[i].click()
        time.sleep(0.3)
        otp_inputs[i].send_keys(digit)
        time.sleep(0.3)

    print("✅ OTP filled successfully.")

    # Step 9: Click Verify button with slight delay
    time.sleep(2)
    verify_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "submit_otpbtn")))
    verify_button.click()
    print("✅ Verify button clicked.")

    # Optional Step 10: Confirm successful login
    time.sleep(3)
    if "dashboard" in driver.current_url or "success" in driver.page_source.lower():
        print("🎉 Login successful.")
    else:
        print("⚠ Login flow continued, check manually.")

except Exception as e:
    print("❌ Test failed:", e)

finally:
    input("Press Enter to close browser...")
    driver.quit()
