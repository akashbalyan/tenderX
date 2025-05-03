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


        


    except Exception as e:
        print(f"Error during search: {e}")




if __name__ == "__main__":
    browser = initialize_browser()
    open_website(browser)
    search_open_tenders(browser)
    
    input("Press Enter to close browser...")
    browser.quit()
