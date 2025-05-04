import time
import os
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

from urllib.parse import urljoin
from downloader import process_tenders

def initialize_browser():
    chrome_options = Options()
    #chrome_options.add_argument("--headless")  # Optional: run in headless mode
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    
    # Set up download directory
    download_dir = os.path.join(os.getcwd(), "downloads")
    os.makedirs(download_dir, exist_ok=True)

    prefs = {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    }
    chrome_options.add_experimental_option("prefs", prefs)

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
            #captcha_text = solve_captcha(browser, captcha_element)
            # For testing purposes, we will use manual input
            captcha_text = input("[🧑‍💻] Enter CAPTCHA manually as seen in the browser: ")

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


def extract_all_tender_links(browser):
    """
    Extracts all tender detail links from paginated results.
    Returns a list of full tender URLs.
    """
    base_url = "https://eprocure.gov.in"
    tender_links = []
    MAX_PAGES = 1 # Set to 1 for testing; change to a higher number for full scraping
    current_page = 0

    while current_page < MAX_PAGES:
        try:
            # Wait until at least one tender link is present
            WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.XPATH, "//td/a[contains(@title, 'View Tender Information')]"))
            )

            # Get all anchor tags inside <td> with matching title
            link_elements = browser.find_elements(By.XPATH, "//td/a[contains(@title, 'View Tender Information')]")

            for link in link_elements:
                relative_href = link.get_attribute("href")
                full_url = urljoin(base_url, relative_href)
                tender_links.append(full_url)

            print(f"[Page {current_page}] Found {len(link_elements)} links.")

            if current_page == MAX_PAGES:
                break  # Stop if we've reached max allowed pages

            # Try to go to the next page if available
            next_button = browser.find_element(By.ID, "linkFwd")
            if "disabled" in next_button.get_attribute("class").lower():
                break

            next_button.click()
            #next_page = current_page + 1
            #WebDriverWait(browser, 10).until(
            #EC.text_to_be_present_in_element((By.XPATH, '//*[@id="informal_19"]/b'), str(next_page)))
            time.sleep(2)  # Wait for the next page to load


            current_page += 1
            
        except Exception as e:
            print(f"No more pages or error: {e}")
            break

    return tender_links


def main_function():
    # Initialize the browser
    browser = initialize_browser()

    # Open the website
    open_website(browser)

    # Search for open tenders
    search_open_tenders(browser)

    # Extract all tender links
    #tender_links = extract_all_tender_links(browser)
    tender_links = [
    "https://etenders.gov.in/eprocure/app?component=%24DirectLink_0&page=FrontEndAdvancedSearchResult&service=direct&session=T&sp=SJF6CyWn8RggyMYtNn0%2BHhw%3D%3D",
    "https://etenders.gov.in/eprocure/app?component=%24DirectLink_0&page=FrontEndAdvancedSearchResult&service=direct&session=T&sp=SBxt1NZPECd9xxZB8ZLBoZw%3D%3D",
    "https://etenders.gov.in/eprocure/app?component=%24DirectLink_0&page=FrontEndAdvancedSearchResult&service=direct&session=T&sp=SU7MPQbIeqQLOYxuhFyYBGA%3D%3D",
    "https://etenders.gov.in/eprocure/app?component=%24DirectLink_0&page=FrontEndAdvancedSearchResult&service=direct&session=T&sp=SWrhuhHbz4IM55Ys06%2FezHQ%3D%3D"
    ]

    print(f"\nTotal tenders found: {len(tender_links)}")
    for i, link in enumerate(tender_links, start=1):
        print(f"{i}. {link}")

    # Process the tenders
    process_tenders(browser, tender_links)

    input("Press Enter to close browser...")
    browser.quit()

if __name__ == "__main__":
    main_function()
