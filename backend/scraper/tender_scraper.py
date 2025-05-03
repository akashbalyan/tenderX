import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from captcha_solver import solve_captcha
from selenium.common.exceptions import NoAlertPresentException

def initialize_browser():
    chrome_options = Options()
    #chrome_options.add_argument("--headless")  # Optional: run in headless mode
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")

    # Correct way to use ChromeDriverManager with Service
    service = Service(ChromeDriverManager().install())
    browser = webdriver.Chrome(service=service, options=chrome_options)

    return browser

def open_website(browser):
    url = "https://etenders.gov.in/eprocure/app"
    browser.get(url)
    #time.sleep(3)  # wait for page to load

def search_open_tenders(browser):
    """Perform search for Open Tenders with captcha handling and retries."""
    try:
        # Step 1: Wait for the search link to be clickable
        search_link = WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Search"))
        )
        search_link.click()

        # Step 2: Wait for the tender type form to be available
        tender_type_dropdown = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.ID, "TenderType"))  
        )
        select = Select(tender_type_dropdown)
        select.select_by_visible_text("Open Tender")

        MAX_ATTEMPTS = 10
        attempts = 0

        while attempts < MAX_ATTEMPTS:
            attempts += 1
            print(f"[Attempt {attempts}] Solving CAPTCHA...")

            # Click the refresh button to get a new CAPTCHA
            try:
                refresh_button = WebDriverWait(browser, 5).until(
                    EC.element_to_be_clickable((By.ID, "captcha"))
                )
                refresh_button.click()
                time.sleep(1)  # Allow time for new image to load
            except Exception as e:
                print("[!] Failed to click CAPTCHA refresh button:", e)
                break

            # Solve the CAPTCHA
            captcha_element = WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.ID, "captchaImage")) 
            )
            captcha_text = solve_captcha(browser, captcha_element)
            print(f"[✓] CAPTCHA text: '{captcha_text}'")
            # Check if CAPTCHA text length is valid
            if len(captcha_text.strip()) < 6:
                print(f"[!] CAPTCHA too short ('{captcha_text}'). Retrying...")
                continue

            # Fill CAPTCHA input
            captcha_input = browser.find_element(By.ID, "captchaText")
            captcha_input.clear()
            captcha_input.send_keys(captcha_text)

            # Click Search button
            search_button = browser.find_element(By.ID, "submit")
            search_button.click()
            time.sleep(2)

            # Check for error message (instead of relying on alert)
            try:
                error_element = browser.find_element(
                    By.XPATH, "//td[@class='alerttext']//b[contains(text(),'Invalid Captcha')]"
                )
                print("[!] Invalid CAPTCHA detected. Retrying...")
                continue
            except:
                print("[✓] CAPTCHA accepted.")
                break


        


    except Exception as e:
        print(f"Error during search: {e}")




if __name__ == "__main__":
    browser = initialize_browser()
    open_website(browser)
    search_open_tenders(browser)
    
    input("Press Enter to close browser...")
    browser.quit()
