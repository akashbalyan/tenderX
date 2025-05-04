import os
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from storage.s3_uploader import upload_to_s3
from captcha_solver import solve_captcha


def process_tenders(browser, tender_links):
    base_url = "https://eprocure.gov.in"
    download_dir = os.path.join(os.getcwd(), "downloads")
    original_window = browser.current_window_handle
    for index, tender_link in enumerate(tender_links):
        try:
            print(f"Processing tender {index + 1}/{len(tender_links)}")

            # Open link in new tab
            browser.execute_script("window.open(arguments[0]);", tender_link)
            browser.switch_to.window(browser.window_handles[-1])
            

            # Wait for tender ID element (update the selector as needed)
            tender_id_elem = WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="content"]/table/tbody/tr[2]/td/table/tbody/tr/td[2]/table/tbody/tr[4]/td/table[2]/tbody/tr/td/table/tbody/tr[2]/td/table/tbody/tr[3]/td[2]/b'))
            )
            tender_id = tender_id_elem.text.strip()
            print(f"Tender ID: {tender_id}")

            # Check for 'Download as Zip' link
            try:
                download_link_elem = WebDriverWait(browser, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Download as zip file')]"))
                )
                print("Found download link. Clicking to navigate to captcha page...")
                download_link_elem.click()
                time.sleep(2)  # Wait for the page to load

                # Check if CAPTCHA is present (which means it didn't go straight to download)
                is_captcha_present = False
                try:
                    WebDriverWait(browser, 3).until(
                        EC.presence_of_element_located((By.ID, "captchaImage"))
                    )
                    is_captcha_present = True
                    print("[🔒] CAPTCHA page detected. Proceeding to solve CAPTCHA...")
                except:
                    print("[🔓] CAPTCHA page not detected. Assuming download started directly.")
                if is_captcha_present:
                    # Now solve captcha on download page
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
                        if len(captcha_text.strip()) != 6:
                            print(f"[!] CAPTCHA length doesnt match to 6 ('{captcha_text}'). Retrying...")
                            continue

                        # Fill CAPTCHA input
                        captcha_input = browser.find_element(By.ID, "captchaText")
                        captcha_input.clear()
                        captcha_input.send_keys(captcha_text)

                        # Click Search button
                        search_button = browser.find_element(By.ID, "Submit")
                        search_button.click()
                        time.sleep(2)

                        # Check for error message (instead of relying on alert)
                        try:
                            error_element = browser.find_element(
                                By.XPATH, "//td[@class='td_space']//b[contains(text(), 'Invalid Captcha')]"
                            )
                            print("[!] Invalid CAPTCHA detected. Retrying...")
                            continue
                        except:
                            print("[✓] CAPTCHA accepted.")
                            break

                    # Wait and click download button (adjust selector as needed)
                    download_link_elem = WebDriverWait(browser, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Download as zip file')]"))
                    )
                    print("Found download link. Clicking to initiate download...")
                    download_link_elem.click()
                    print("Download initiated...")

                # OPTIONAL: wait for file to appear in downloads
                time.sleep(5)  # or use logic to confirm file is downloaded

                zip_file_path = wait_for_zip_file(download_dir)
                print(f"[📦] Downloaded file path: {zip_file_path}")

                upload_to_s3(zip_file_path, tender_id)
                print(f"[✅] Uploaded {zip_file_path} to S3 with ID: {tender_id}")

            except Exception as e:
                print(f"No 'Download as Zip' link found or captcha solving failed: {e}")

            

            # Close tab
            browser.close()
            browser.switch_to.window(original_window)

        except Exception as e:
            print(f"Error processing tender at {tender_link}: {e}")
            # Close tab and return to main window
            if len(browser.window_handles) > 1:
                browser.close()
                browser.switch_to.window(original_window)



def wait_for_zip_file(download_dir, timeout=30):
    print("[⏳] Waiting for zip file to appear in downloads...")
    end_time = time.time() + timeout
    while time.time() < end_time:
        files = [f for f in os.listdir(download_dir) if f.endswith(".zip")]
        if files:
            latest_file = max(files, key=lambda f: os.path.getctime(os.path.join(download_dir, f)))
            return os.path.join(download_dir, latest_file)
        time.sleep(1)
    raise TimeoutError("ZIP file not downloaded within the timeout.")