from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
import time
import random
import string
import os
import traceback

# --- Configuration ---
BASE_URL = "http://13.201.96.168"  # Ensure this matches your running frontend
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--window-size=1920,1080')
chrome_options.add_argument('--disable-gpu')

# Global credentials
TEST_USER = {
    "username": "User_" + ''.join(random.choices(string.ascii_letters, k=5)),
    "email": f"test_{random.randint(10000, 99999)}@example.com",
    "password": "Password123!"
}

def setup_driver():
    chromedriver_path = '/usr/local/bin/chromedriver'
    if os.path.exists(chromedriver_path):
        service = Service(chromedriver_path)
        return webdriver.Chrome(service=service, options=chrome_options)
    else:
        return webdriver.Chrome(options=chrome_options)

def safe_click(driver, element):
    """Robust click handler for headless mode"""
    try:
        WebDriverWait(driver, 2).until(EC.element_to_be_clickable(element))
        element.click()
    except (TimeoutException, ElementClickInterceptedException):
        driver.execute_script("arguments[0].click();", element)

def find_toggle_button(driver):
    """
    Tries multiple strategies to find the Login/Signup toggle button
    """
    selectors = [
        (By.CLASS_NAME, "switch-button"),
        (By.CSS_SELECTOR, ".switch-mode span"),
        (By.CSS_SELECTOR, ".switch-mode button"),
        (By.CSS_SELECTOR, ".toggle-text span"),
        (By.XPATH, "//span[contains(text(), 'Sign Up')]"),
        (By.XPATH, "//button[contains(text(), 'Sign Up')]"),
        (By.XPATH, "//a[contains(text(), 'Sign Up')]")
    ]
    for by, selector in selectors:
        try:
            element = driver.find_element(by, selector)
            if element.is_displayed():
                return element
        except NoSuchElementException:
            continue
    raise NoSuchElementException("Could not find the Sign Up toggle using any known selector.")

# --- Tests ---
def test_1_redirect():
    driver = setup_driver()
    try:
        driver.get(BASE_URL)
        WebDriverWait(driver, 5).until(EC.url_contains("/auth"))
        print("✓ Test 1 Passed: Redirect to login works")
    except Exception as e:
        print(f"✗ Test 1 Failed: {str(e)}")
        traceback.print_exc()
    finally:
        driver.quit()

def test_2_login_ui():
    driver = setup_driver()
    try:
        driver.get(f"{BASE_URL}/auth")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "email")))
        assert driver.find_element(By.NAME, "password")
        try:
            driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        except:
            driver.find_element(By.CLASS_NAME, "submit-button")
        print("✓ Test 2 Passed: Login UI loaded")
    except Exception as e:
        print(f"✗ Test 2 Failed: {str(e)}")
        traceback.print_exc()
    finally:
        driver.quit()

def test_3_toggle_interaction():
    driver = setup_driver()
    try:
        driver.get(f"{BASE_URL}/auth")
        toggle = WebDriverWait(driver, 10).until(lambda d: find_toggle_button(d))
        safe_click(driver, toggle)
        WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located((By.NAME, "username"))
        )
        print("✓ Test 3 Passed: Toggle switched to Sign Up")
    except Exception as e:
        print(f"✗ Test 3 Failed: {str(e)}")
        traceback.print_exc()
    finally:
        driver.quit()

def test_4_registration():
    driver = setup_driver()
    try:
        driver.get(f"{BASE_URL}/auth")
        # 1. Switch to Sign Up
        toggle = WebDriverWait(driver, 10).until(lambda d: find_toggle_button(d))
        safe_click(driver, toggle)
        # 2. Wait for form update
        WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.NAME, "username")))
        # 3. Fill form
        driver.find_element(By.NAME, "username").send_keys(TEST_USER["username"])
        driver.find_element(By.NAME, "email").send_keys(TEST_USER["email"])
        driver.find_element(By.NAME, "password").send_keys(TEST_USER["password"])
        # 4. Submit
        try:
            submit_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        except NoSuchElementException:
            submit_btn = driver.find_element(By.CLASS_NAME, "submit-button")
        safe_click(driver, submit_btn)
        # 5. Wait for success redirect
        WebDriverWait(driver, 10).until(EC.url_contains("/clubs"))
        print(f"✓ Test 4 Passed: Registered {TEST_USER['username']}")
    except Exception as e:
        print(f"✗ Test 4 Failed: {str(e)}")
        print(f"Current URL: {driver.current_url}")
        print(f"Page source preview: {driver.page_source[:500]}")
        traceback.print_exc()
    finally:
        driver.quit()

def test_5_invalid_login():
    driver = setup_driver()
    try:
        driver.get(f"{BASE_URL}/auth")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "email")))
        driver.find_element(By.NAME, "email").send_keys("fake@notexist.com")
        driver.find_element(By.NAME, "password").send_keys("wrongpass")
        try:
            submit_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        except NoSuchElementException:
            submit_btn = driver.find_element(By.CLASS_NAME, "submit-button")
        safe_click(driver, submit_btn)
        error = WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "error-message"))
        )
        assert error.is_displayed()
        print("✓ Test 5 Passed: Error message shown")
    except Exception as e:
        print(f"✗ Test 5 Failed: {str(e)}")
        traceback.print_exc()
    finally:
        driver.quit()

def test_6_valid_login():
    driver = setup_driver()
    try:
        driver.get(f"{BASE_URL}/auth")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "email")))
        driver.find_element(By.NAME, "email").send_keys(TEST_USER["email"])
        driver.find_element(By.NAME, "password").send_keys(TEST_USER["password"])
        try:
            submit_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        except NoSuchElementException:
            submit_btn = driver.find_element(By.CLASS_NAME, "submit-button")
        safe_click(driver, submit_btn)
        WebDriverWait(driver, 10).until(EC.url_contains("/clubs"))
        print("✓ Test 6 Passed: Login successful")
    except Exception as e:
        print(f"✗ Test 6 Failed: Check if Registration (Test 4) passed first. {str(e)}")
        traceback.print_exc()
    finally:
        driver.quit()

def test_7_navbar_visibility():
    driver = setup_driver()
    try:
        driver.get(f"{BASE_URL}/auth")
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.NAME, "email")))
        driver.find_element(By.NAME, "email").send_keys(TEST_USER["email"])
        driver.find_element(By.NAME, "password").send_keys(TEST_USER["password"])
        try:
            submit_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        except:
            submit_btn = driver.find_element(By.CLASS_NAME, "submit-button")
        safe_click(driver, submit_btn)
        WebDriverWait(driver, 5).until(EC.url_contains("/clubs"))
        nav = WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "navbar"))
        )
        assert nav.is_displayed()
        print("✓ Test 7 Passed: Navbar visible")
    except Exception as e:
        print(f"✗ Test 7 Failed: {str(e)}")
        traceback.print_exc()
    finally:
        driver.quit()

def test_8_clubs_load():
    driver = setup_driver()
    try:
        driver.get(f"{BASE_URL}/auth")
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.NAME, "email")))
        driver.find_element(By.NAME, "email").send_keys(TEST_USER["email"])
        driver.find_element(By.NAME, "password").send_keys(TEST_USER["password"])
        try:
            submit_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        except:
            submit_btn = driver.find_element(By.CLASS_NAME, "submit-button")
        safe_click(driver, submit_btn)
        WebDriverWait(driver, 10).until(EC.url_contains("/clubs"))
        clubs = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "club-card"))
        )
        assert len(clubs) > 0
        print(f"✓ Test 8 Passed: Found {len(clubs)} clubs")
    except Exception as e:
        print(f"✗ Test 8 Failed: {str(e)}")
        traceback.print_exc()
    finally:
        driver.quit()

def test_9_view_details():
    driver = setup_driver()
    try:
        driver.get(f"{BASE_URL}/auth")
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.NAME, "email")))
        driver.find_element(By.NAME, "email").send_keys(TEST_USER["email"])
        driver.find_element(By.NAME, "password").send_keys(TEST_USER["password"])
        try:
            submit_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        except:
            submit_btn = driver.find_element(By.CLASS_NAME, "submit-button")
        safe_click(driver, submit_btn)
        WebDriverWait(driver, 5).until(EC.url_contains("/clubs"))
        view_btns = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "view-button"))
        )
        safe_click(driver, view_btns[0])
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, "back-button"))
        )
        print("✓ Test 9 Passed: Club details loaded")
    except Exception as e:
        print(f"✗ Test 9 Failed: {str(e)}")
        traceback.print_exc()
    finally:
        driver.quit()

def test_10_logout():
    driver = setup_driver()
    try:
        driver.get(f"{BASE_URL}/auth")
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.NAME, "email")))
        driver.find_element(By.NAME, "email").send_keys(TEST_USER["email"])
        driver.find_element(By.NAME, "password").send_keys(TEST_USER["password"])
        try:
            submit_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        except:
            submit_btn = driver.find_element(By.CLASS_NAME, "submit-button")
        safe_click(driver, submit_btn)
        WebDriverWait(driver, 5).until(EC.url_contains("/clubs"))
        logout_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Log Out')]"))
        )
        safe_click(driver, logout_btn)
        WebDriverWait(driver, 5).until(EC.url_contains("/auth"))
        print("✓ Test 10 Passed: Logout successful")
    except Exception as e:
        print(f"✗ Test 10 Failed: {str(e)}")
        traceback.print_exc()
    finally:
        driver.quit()

if __name__ == "__main__":
    print("Starting 10 Essential Selenium Tests for BookVerse\n")
    test_1_redirect()
    test_2_login_ui()
    test_3_toggle_interaction()
    test_4_registration()
    test_5_invalid_login()
    test_6_valid_login()
    test_7_navbar_visibility()
    test_8_clubs_load()
    test_9_view_details()
    test_10_logout()
    print("\nAll 10 tests completed.")
