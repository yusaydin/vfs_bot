from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import subprocess
import os
import winsound  # For playing alert sounds

def play_error_sound():
    """Play error sound (1000Hz for 1 second) to alert user of an error"""
    winsound.Beep(1000, 1000)

def play_success_sound():
    """Play success sound (2000Hz, 3 times) to alert user when appointment is found"""
    for _ in range(3):
        winsound.Beep(2000, 500)
        time.sleep(0.1)

def start_chrome_debug():
    """
    Start Chrome in debug mode with custom profile and security settings.
    Returns:
        bool: True if Chrome started successfully, False otherwise
    """
    try:
        # Try to find Chrome executable in both Program Files locations
        chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        if not os.path.exists(chrome_path):
            chrome_path = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
        
        # Create unique profile directory for debugging session
        user_data_dir = os.path.join(os.path.expanduser("~"), "chrome_debug_profile")
        
        # Configure Chrome launch arguments for automation
        chrome_args = [
            chrome_path,
            f"--remote-debugging-port=9223",  # Custom debugging port
            f"--user-data-dir={user_data_dir}",
            "--disable-blink-features=AutomationControlled",  # Hide automation flags
            "--disable-web-security",  # Required for VFS site
            "--disable-features=IsolateOrigins,site-per-process",
            "--no-sandbox",
            "--window-size=1920,1080"  # Full HD resolution
        ]
        
        # Clean up old profile if exists
        if os.path.exists(user_data_dir):
            try:
                import shutil
                shutil.rmtree(user_data_dir)
                time.sleep(1)  # Wait for cleanup
            except:
                pass
        
        # Launch Chrome with debug options
        subprocess.Popen(chrome_args)
        print("Chrome started in debug mode")
        time.sleep(5)  # Wait for Chrome to initialize
        return True
        
    except Exception as e:
        print(f"Failed to start Chrome: {e}")
        return False

def connect_to_existing_browser():
    """
    Connect to the running Chrome instance in debug mode.
    Returns:
        webdriver: Configured Chrome WebDriver instance
    """
    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9223")
    
    # Simplified options - only necessary ones
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    
    # Automatically download ChromeDriver
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def fill_form(driver, user_data, input_start_id, base_select_id):
    """
    Fill the VFS application form with user data.
    
    Args:
        driver: Selenium WebDriver instance
        user_data (dict): User's personal information
        input_start_id (int): Base ID for input fields
        base_select_id (int): Base ID for dropdown fields
    
    Returns:
        bool: True if form filled successfully, False otherwise
    """
    try:
        print("\nForm filling process starts...")
        print(f"Used IDs - Input: {input_start_id}, Select: {base_select_id}")
        time.sleep(5)

        # Text input fields - with XPath
        for field_name, id_offset in {
            'first_name': 0,
            'last_name': 1,
            'passport': 2,
            'country_code': 3,
            'phone': 4,
            'email': 5
        }.items():
            try:
                current_id = f"mat-input-{input_start_id + id_offset}"
                print(f"[ID: {input_start_id + id_offset}] Filling {field_name} field (Element ID: {current_id})...")
                
                element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, f'//*[@id="{current_id}"]'))
                )
                element.clear()
                time.sleep(0.5)
                
                if field_name == 'country_code':
                    element.send_keys('90')
                else:
                    element.send_keys(user_data[field_name])
                time.sleep(1)
                print(f"[ID: {input_start_id + id_offset}] {field_name} field filled")
                
            except Exception as e:
                error_msg = f"[ID: {input_start_id + id_offset}] Error filling {field_name}: Message: {str(e)}"
                print(error_msg)
                play_error_sound()  # Play error sound
                raise Exception(error_msg)

        # New process for dropdown menus
        dropdowns = {
            'gender': {
                'button': f'//*[@id="mat-select-value-1"]',  # Make ID dynamic
                'value': user_data['gender'],
                'select_id': base_select_id  # Will come from base_select_id global variable
            },
            'nationality': {
                'button': f'//*[@id="mat-select-value-3"]',  # Make ID dynamic
                'value': 'Turkiye',
                'select_id': base_select_id + 2  # 2 more than gender
            }
        }
        
        for dropdown_name, data in dropdowns.items():
            try:
                print(f"[ID: {data['select_id']}] Selecting {dropdown_name}...")
                # Open dropdown
                dropdown = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, f'//*[@id="mat-select-value-{data["select_id"]}"]'))
                )
                driver.execute_script("arguments[0].click();", dropdown)
                time.sleep(2)
                
                # Find and click option with JavaScript
                js_script = """
                function selectOption(searchText) {
                    const panel = document.querySelector('.mat-mdc-select-panel');
                    if (!panel) return false;
                    
                    const options = Array.from(panel.querySelectorAll('mat-option'));
                    for (let option of options) {
                        if (option.textContent.trim().toLowerCase() === searchText.toLowerCase()) {
                            option.scrollIntoView({behavior: 'smooth', block: 'center'});
                            setTimeout(() => option.click(), 500);
                            return true;
                        }
                    }
                    return false;
                }
                return selectOption(arguments[0]);
                """
                
                # Use exact text match for gender
                value_to_search = data['value']
                if (dropdown_name == 'gender'):
                    print(f"Searching for gender value: {value_to_search}")
                    found = driver.execute_script(js_script, value_to_search)
                else:
                    # Try alternative values for nationality
                    found = driver.execute_script(js_script, value_to_search)
                    if not found:
                        alternate_values = {
                            'Turkiye': ['Turkey', 'Turkish', 'Türkiye'],
                            'Turkey': ['Turkiye', 'Turkish', 'Türkiye']
                        }
                        if value_to_search in alternate_values:
                            for alt_value in alternate_values[value_to_search]:
                                found = driver.execute_script(js_script, alt_value)
                                if found:
                                    print(f"Alternative value {alt_value} selected for {dropdown_name}")
                                    break

                if not found:
                    raise Exception(f"Option {value_to_search} not found")
                
                print(f"{dropdown_name} selection completed")
                time.sleep(1)
                
            except Exception as e:
                error_msg = f"[ID: {data['select_id']}] Error selecting {dropdown_name}: {str(e)}"
                print(error_msg)
                play_error_sound()  # Play error sound
                raise Exception(error_msg)

        # Save button - with CSS Selector
        try:
            print("Saving form...")
            
            # Improve scroll to bottom of the page
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)
            driver.execute_script("window.scrollBy(0, -150);")  # Scroll up a bit
            time.sleep(1)
            
            # Find save button with CSS Selector
            save_button_css = "button.mdc-button.btn-brand-orange"
            save_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, save_button_css))
            )
            
            # Scroll to button until visible
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", save_button)
            time.sleep(2)
            
            # Try different click methods
            try:
                # Click with JavaScript
                driver.execute_script("arguments[0].click();", save_button)
                time.sleep(2)
                
                # Wait for URL change
                WebDriverWait(driver, 5).until(
                    lambda driver: "applicationdetails" in driver.current_url
                )
                print("Form saved successfully")
                return True
                
            except Exception as e:
                print(f"Click error, trying different selector: {str(e)}")
                play_error_sound()  # Play error sound for click error
                
                # Try alternative CSS selector
                try:
                    alt_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, "button.mat-mdc-outlined-button.btn-brand-orange"))
                    )
                    driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", alt_button)
                    time.sleep(2)
                    driver.execute_script("arguments[0].click();", alt_button)
                    time.sleep(3)
                    return True
                except:
                    raise
            
        except Exception as e:
            print(f"Save error: {str(e)}")
            play_error_sound()  # Play error sound for save error
            raise
            
    except Exception as e:
        print(f"Form filling error: {str(e)}")
        play_error_sound()  # Play error sound for form filling error
        return False

def check_appointment_loop(driver):
    """
    Main loop for checking appointment availability.
    Handles the entire flow from dashboard to appointment selection.
    """
    # Initialize ID trackers for dynamic elements
    checkbox_base_ids = [1, 2, 3]  # Base IDs for checkboxes
    input_base_id = 6     # Base ID for input fields
    base_select_id = 1    # Base ID for select/dropdown fields
    
    while True:
        try:
            # Dashboard button click
            dashboard_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "/html/body/app-root/div/main/div/app-dashboard/section[1]/div/div[1]/div[2]/button/span[2]"))
            )
            dashboard_button.click()
            print("Clicked on Dashboard button")
            time.sleep(2)
            
            # Check first page checkboxes
            print("\nFirst page checkbox operations start...")
            checkbox_names = ["Conditions and Terms of Use", "Privacy Policy"]
            for i in range(2):
                checkbox_id = f"mat-mdc-checkbox-{checkbox_base_ids[i]}-input"
                print(f"[ID: {checkbox_base_ids[i]}] Searching for {checkbox_names[i]} checkbox (Element ID: {checkbox_id})...")
                checkbox = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, f'//*[@id="{checkbox_id}"]'))
                )
                driver.execute_script("arguments[0].click();", checkbox)
                time.sleep(1)
                print(f"[ID: {checkbox_base_ids[i]}] {checkbox_names[i]} checkbox checked")
            
            # Click Start New Booking button
            start_booking = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(.,'Start New Booking')]"))
            )
            driver.execute_script("arguments[0].click();", start_booking)
            print("Clicked on Start New Booking")
            time.sleep(2)
            
            # Second page - Third checkbox
            checkbox_id = f"mat-mdc-checkbox-{checkbox_base_ids[2]}-input"
            print(f"\n[ID: {checkbox_base_ids[2]}] Searching for second page Terms and Conditions checkbox (Element ID: {checkbox_id})...")
            checkbox3 = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, f'//*[@id="{checkbox_id}"]'))
            )
            driver.execute_script("arguments[0].click();", checkbox3)
            time.sleep(1)
            print(f"[ID: {checkbox_base_ids[2]}] Second page Terms and Conditions checkbox checked")
            
            # Click Continue button on second page
            continue_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Continue')]"))
            )
            driver.execute_script("arguments[0].click();", continue_button)
            print("Clicked on Continue button on second page")
            time.sleep(2)
            
            # Form page operations - input IDs increase by 6
            if "your-details" in driver.current_url:
                user_data = {
                    'first_name': 'Yusuf',
                    'last_name': 'Aydin',  # AYDIN -> Aydin
                    'gender': 'Male',
                    'nationality': 'Turkey',
                    'passport': 'U123456',
                    'country_code': '90',  # Removed +
                    'phone': '5551234567',
                    'email': 'yusufaydin620@gmail.com'
                }
                inputs = {
                    'first_name': f'//*[@id="mat-input-{input_base_id}"]',
                    'last_name': f'//*[@id="mat-input-{input_base_id + 1}"]',
                    'passport': f'//*[@id="mat-input-{input_base_id + 2}"]',
                    'country_code': f'//*[@id="mat-input-{input_base_id + 3}"]',
                    'phone': f'//*[@id="mat-input-{input_base_id + 4}"]',
                    'email': f'//*[@id="mat-input-{input_base_id + 5}"]'
                }
                if fill_form(driver, user_data, input_base_id, base_select_id):
                    print("Form filled")
            
            # Appointment selection page
            if "applicationdetails" in driver.current_url:
                try:
                    print("\nAppointment selection process starts...")
                    time.sleep(2)
                    
                    # First dropdown (Long Term) - base_select_id + 4
                    first_dropdown = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, f"#mat-select-value-{base_select_id + 4}"))
                    )
                    first_dropdown.click()
                    time.sleep(1)
                    
                    # Select "1 - Uzun Donem" option
                    long_term_option = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), '1 - Uzun Donem')]"))
                    )
                    long_term_option.click()
                    time.sleep(2)
                    
                    # Second dropdown (ERASMUS/NAWA/ECS) - base_select_id + 6
                    second_dropdown = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, f"#mat-select-value-{base_select_id + 6}"))
                    )
                    second_dropdown.click()
                    time.sleep(1)
                    
                    # Select "5-ERASMUS/NAWA/ECS" option
                    erasmus_option = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), '5-ERASMUS/NAWA/ECS')]"))
                    )
                    erasmus_option.click()
                    time.sleep(2)
                    
                    # Check for error message
                    try:
                        error_message = WebDriverWait(driver, 3).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, "div.errorMessage.c-brand-error"))
                        )
                        print("No appointment found, retrying...")
                        
                        # Return to dashboard
                        account_button = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.XPATH, '//*[@id="navbarDropdown"]'))
                        )
                        account_button.click()
                        time.sleep(1)
                        
                        dashboard_link = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.XPATH, '//*[@id="navbarToggle"]/ul/li/div/a[1]'))
                        )
                        dashboard_link.click()
                        print("Returning to dashboard...")
                        time.sleep(5)
                        
                        # Update IDs (increase by 10 instead of 6)
                        checkbox_base_ids = [x + 3 for x in checkbox_base_ids]  # Add 3 to each ID
                        input_base_id += 6     # Input IDs increase by 6
                        base_select_id += 10   # Select IDs increase by 10
                        continue
                        
                    except:
                        # If no error message, check third dropdown
                        third_dropdown = WebDriverWait(driver, 5).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, f"#mat-select-value-{base_select_id + 8}"))
                        )
                        if "Uygulama merkezinizi seçin" in third_dropdown.text:
                            print("Appointment found!")
                            play_success_sound()  # Added success sound
                            input("Press Enter to continue...")  # Wait for user to check
                            return True
                
                except Exception as e:
                    print(f"Appointment selection error: {e}")
                    checkbox_base_ids = [x + 3 for x in checkbox_base_ids]  # Add 3 to each ID
                    input_base_id += 6     # Input IDs increase by 6
                    base_select_id += 10   # Select IDs increase by 10
                    # Return to dashboard
                    try:
                        account_button = driver.find_element(By.XPATH, '//*[@id="navbarDropdown"]')
                        account_button.click()
                        time.sleep(1)
                        dashboard_link = driver.find_element(By.XPATH, '//*[@id="navbarToggle"]/ul/li/div/a[1]')
                        dashboard_link.click()
                        print("Returning to dashboard after error...")
                        time.sleep(5)
                    except:
                        print("Failed to return to dashboard, retrying...")
                    continue
                    
        except Exception as e:
            print(f"General error: {e}")
            time.sleep(5)
            continue

def check_appointments(driver):
    """
    Alternative implementation of appointment checking with better error handling
    and ID management using dictionary-based tracking.
    """
    # Initialize global ID trackers
    global_ids = {
        'checkbox_start': 1,  # Base ID for checkboxes, increments by 3
        'input_start': 6,     # Base ID for inputs, increments by 6
        'select_start': 1     # Base ID for dropdowns, increments by 10
    }
    
    while True:
        try:
            print("\nDashboard operations start...")
            print(f"Current IDs - Checkbox: {global_ids['checkbox_start']}, Input: {global_ids['input_start']}, Select: {global_ids['select_start']}")
            
            # Check first two checkboxes
            checkbox_names = ["Conditions and Terms of Use", "Privacy Policy"]
            for i in range(2):
                try:
                    current_id = global_ids['checkbox_start'] + (i * 1)  # Increase by 1 for each checkbox
                    checkbox_id = f"mat-mdc-checkbox-{current_id}-input"
                    print(f"[ID: {current_id}] Searching for {checkbox_names[i]} checkbox (Element ID: {checkbox_id})...")
                    
                    checkbox = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, f'//*[@id="{checkbox_id}"]'))
                    )
                    driver.execute_script("arguments[0].click();", checkbox)
                    time.sleep(1)
                    print(f"[ID: {current_id}] {checkbox_names[i]} checkbox checked")
                    
                except Exception as e:
                    print(f"[ID: {current_id}] Error checking {checkbox_names[i]} checkbox: {str(e)}")
                    # Update IDs and retry
                    global_ids['checkbox_start'] += 3  # Increase by 3 after each error
                    global_ids['input_start'] += 6    # Increase input IDs by 6
                    global_ids['select_start'] += 10  # Increase select IDs by 10
                    continue

            # Start New Booking button
            print("\nSearching for Start New Booking button...")
            start_booking = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "button.btn-brand-orange"))
            )
            driver.execute_script("arguments[0].click();", start_booking)
            print("Clicked on Start New Booking")
            time.sleep(3)
            
            # Second page operations
            print("\nSecond page operations start...")
            try:
                # Wait for and click new checkbox
                print("Waiting for second page checkbox...")
                current_id = global_ids['checkbox_start'] + 2  # For third checkbox
                checkbox_id = f"mat-mdc-checkbox-{current_id}-input"
                checkbox3 = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, f'//*[@id="{checkbox_id}"]'))
                )
                driver.execute_script("arguments[0].click();", checkbox3)
                time.sleep(1)
                print("Second page checkbox checked")
                
                # Click Continue button
                continue_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button.mdc-button"))
                )
                driver.execute_script("arguments[0].click();", continue_button)
                print("Clicked on Continue button")
                time.sleep(3)
                
                # Form page check and fill
                if "your-details" in driver.current_url:
                    print("\nReached form page, filling form...")
                    user_data = {
                        'first_name': 'Yusuf',
                        'last_name': 'Aydin',  # AYDIN -> Aydin
                        'gender': 'Male',
                        'nationality': 'Turkiye',  # Turkey -> Turkiye
                        'passport': 'U123456',
                        'country_code': '90',  # Removed +
                        'phone': '5551234567',
                        'email': 'yusufaydin620@gmail.com'
                    }
                    inputs = {
                        'first_name': f'//*[@id="mat-input-{global_ids["input_start"]}"]',
                        'last_name': f'//*[@id="mat-input-{global_ids["input_start"] + 1}"]',
                        'passport': f'//*[@id="mat-input-{global_ids["input_start"] + 2}"]',
                        'country_code': f'//*[@id="mat-input-{global_ids["input_start"] + 3}"]',
                        'phone': f'//*[@id="mat-input-{global_ids["input_start"] + 4}"]',
                        'email': f'//*[@id="mat-input-{global_ids["input_start"] + 5}"]'
                    }
                    
                    if fill_form(driver, user_data, global_ids['input_start'], global_ids['select_start']):
                        print("Form filled and saved")
                    else:
                        print("Form filling failed")
                        raise Exception("Form filling error")
                    
            except Exception as e:
                print(f"Second page operation error: {str(e)}")
                raise

            # Continue with appointment selection after form is filled
            if "applicationdetails" in driver.current_url:
                try:
                    print("\nAppointment selection process starts...")
                    print(f"Used Select ID: {global_ids['select_start']}")
                    time.sleep(3)  # Wait for page to fully load
                    
                    # Wait for page to load
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, ".mat-mdc-form-field"))
                    )
                    
                    # First dropdown (Long Term)
                    try:
                        print(f"Searching for first dropdown (ID: {global_ids['select_start'] + 4})...")
                        first_dropdown = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, f"[id='mat-select-value-{global_ids['select_start'] + 4}']"))
                        )
                        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", first_dropdown)
                        time.sleep(1)
                        driver.execute_script("arguments[0].click();", first_dropdown)
                        time.sleep(2)
                        
                        # Select "1 - Uzun Donem" option
                        long_term_option = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, "//span[normalize-space()='1 - Uzun Donem']"))
                        )
                        driver.execute_script("arguments[0].click();", long_term_option)
                        time.sleep(2)
                        
                    except Exception as e:
                        print(f"First dropdown error: {str(e)}")
                        raise
                    
                    # Second dropdown (ERASMUS/NAWA/ECS)
                    try:
                        print(f"Searching for second dropdown (ID: {global_ids['select_start'] + 6})...")
                        second_dropdown = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, f"[id='mat-select-value-{global_ids['select_start'] + 6}']"))
                        )
                        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", second_dropdown)
                        time.sleep(1)
                        driver.execute_script("arguments[0].click();", second_dropdown)
                        time.sleep(2)
                        
                        # Select "5-ERASMUS/NAWA/ECS" option
                        erasmus_option = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, "//span[normalize-space()='5-ERASMUS/NAWA/ECS']"))
                        )
                        driver.execute_script("arguments[0].click();", erasmus_option)
                        time.sleep(2)
                        
                    except Exception as e:
                        print(f"Second dropdown error: {str(e)}")
                        raise
                    
                    while True:  # Continue loop until appointment is found
                        try:
                            error_message = WebDriverWait(driver, 3).until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, "div.errorMessage.c-brand-error"))
                            )
                            print("No appointment found, retrying...")
                            
                            # Return to dashboard
                            account_button = WebDriverWait(driver, 10).until(
                                EC.element_to_be_clickable((By.XPATH, '//*[@id="navbarDropdown"]'))
                            )
                            account_button.click()
                            time.sleep(1)
                            
                            dashboard_link = WebDriverWait(driver, 10).until(
                                EC.element_to_be_clickable((By.XPATH, '//*[@id="navbarToggle"]/ul/li/div/a[1]'))
                            )
                            dashboard_link.click()
                            print("Returning to dashboard...")
                            time.sleep(5)
                            
                            # Update IDs and restart
                            global_ids['checkbox_start'] += 3  # Add 3 to each ID
                            global_ids['input_start'] += 6     # Input IDs increase by 6
                            global_ids['select_start'] += 10   # Select IDs increase by 10
                            print(f"IDs updated - New values: Checkbox: {global_ids['checkbox_start']}, Input: {global_ids['input_start']}, Select: {global_ids['select_start']}")
                            break  # Exit inner while loop, return to outer while loop
                            
                        except:
                            print("Checking appointment...")
                            # If no error message, check third dropdown
                            third_dropdown = WebDriverWait(driver, 5).until(
                                EC.element_to_be_clickable((By.CSS_SELECTOR, f"#mat-select-value-{global_ids['select_start'] + 8}"))
                            )
                            if "Uygulama merkezinizi seçin" in third_dropdown.text:
                                print("Appointment found!")
                                play_success_sound()  # Already exists
                                input("Press Enter to continue...")  # Already exists
                                return True
                
                except Exception as e:
                    print(f"Appointment selection error: {e}")
                    play_error_sound()  # Play error sound for general error
                    # Update IDs and retry in case of error
                    global_ids['checkbox_start'] += 3
                    global_ids['input_start'] += 6
                    global_ids['select_start'] += 10
                    print(f"IDs updated after error - New values: Checkbox: {global_ids['checkbox_start']}, Input: {global_ids['input_start']}, Select: {global_ids['select_start']}")
                    continue

        except Exception as e:
            print(f"\nERROR DETAILS:")
            print(f"Type: {type(e).__name__}")
            print(f"Message: {str(e)}")
            play_error_sound()  # Play error sound for general error
            # Update IDs and retry in case of error
            global_ids['checkbox_start'] += 3
            global_ids['input_start'] += 6
            global_ids['select_start'] += 10
            print(f"IDs updated after general error - New values: Checkbox: {global_ids['checkbox_start']}, Input: {global_ids['input_start']}, Select: {global_ids['select_start']}")
            continue

def start_bot():
    """
    Main entry point for the VFS appointment booking bot.
    Handles initialization and main program flow.
    """
    print("Starting Chrome in debug mode...")
    if not start_chrome_debug():
        print("Failed to start Chrome!")
        return
        
    print("\n1. Log in to the VFS site in the opened Chrome window")
    print("2. After reaching the Dashboard page, press Enter...")
    input()

    try:
        driver = connect_to_existing_browser()
        print("Connected to existing Chrome session")
        
        # Check appointments
        check_appointments(driver)
        
    except Exception as e:        
        print(f"Connection error: {e}")
    
    finally:
        print("\nProcess completed. Press Enter to exit...")
        input()

if __name__ == "__main__":
    # Ensure webdriver-manager is installed for automatic ChromeDriver management
    # pip install webdriver-manager
    start_bot()