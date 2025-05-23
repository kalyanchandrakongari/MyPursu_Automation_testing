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
    # Step 1: Go to login page
    driver.get("https://dev.mypursu.com/sign-in")

    # Step 2: Enter email
    email_input = wait.until(EC.visibility_of_element_located((By.ID, "emailID")))
    # email_input = wait.until(EC.visibility_of_element_located((By.ID, "email")))
    email_input.send_keys("nane@yopmail.com")

    # Wait for the checkbox to be present
    terms_checkbox = wait.until(EC.presence_of_element_located((By.ID, "termsConditions")))

    # Scroll into view if necessary
    driver.execute_script("arguments[0].scrollIntoView(true);", terms_checkbox)

    # Check if the checkbox is not already selected
    if not terms_checkbox.is_selected():
        terms_checkbox.click()
        print("✅ Terms and Conditions accepted.")
    else:
        print("ℹ Terms and Conditions were already accepted.")


    time.sleep(1)

    continue_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Continue')]")
    continue_btn.click()



    # Step 3: Open Yopmail to get OTP
    driver.execute_script("window.open('');")
    driver.switch_to.window(driver.window_handles[1])
    driver.get("https://yopmail.com/?login=nane")


    # Step 4: Read OTP from email
    driver.switch_to.default_content()
    wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, "ifmail")))
    mail_body = wait.until(EC.presence_of_element_located((By.TAG_NAME, "body"))).text

    otp_match = re.search(r"\b(\d{6})\b", mail_body)
    if not otp_match:
        raise Exception("OTP not found in email")

    otp = otp_match.group(1)
    print("✅ OTP:", otp)

    # Step 5: Return to login tab and enter OTP
    driver.switch_to.default_content()
    driver.switch_to.window(driver.window_handles[0])

    # Wait for the OTP fields to be present
    wait.until(EC.presence_of_element_located((By.ID, "inputs")))

    # Get all 6 OTP input boxes
    otp_inputs = driver.find_elements(By.XPATH, "//*[@id='inputs']//input[@type='text']")

    # Ensure you got exactly 6 input fields
    if len(otp_inputs) != 6:
        raise Exception(f"Expected 6 OTP fields, found {len(otp_inputs)}")

    time.sleep(1)  # Optional wait for animation/loading

    # Fill each input with its corresponding OTP digit
    for i, digit in enumerate(otp):
        driver.execute_script("""
            const input = arguments[0];
            input.value = arguments[1];
            input.dispatchEvent(new Event('input', { bubbles: true }));
            input.dispatchEvent(new Event('change', { bubbles: true }));
        """, otp_inputs[i], digit)

    print("✅ OTP digits filled in all fields.")
    verify_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "submit_otpbtn")))
    #verify_button.click()
    time.sleep(1)
    verify_button.click()


except Exception as e:
    print("Test failed:", e)

finally:
    input("Press Enter to close the browser...")
    driver.quit()
