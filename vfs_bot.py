from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import subprocess
import os
import winsound  # En üste eklenecek

def play_error_sound():
    # 1000 Hz'de 1000ms (1 saniye) süreyle hata sesi çal
    winsound.Beep(1000, 1000)

def play_success_sound():
    # 3 kez 2000 Hz'de başarı sesi çal
    for _ in range(3):
        winsound.Beep(2000, 500)
        time.sleep(0.1)

def start_chrome_debug():
    try:
        chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        if not os.path.exists(chrome_path):
            chrome_path = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
        
        # Farklı port ve profil dizini kullan
        user_data_dir = os.path.join(os.path.expanduser("~"), "chrome_debug_profile")
        
        # Chrome argümanlarını genişlet
        chrome_args = [
            chrome_path,
            f"--remote-debugging-port=9223",  # Farklı port
            f"--user-data-dir={user_data_dir}",
            "--disable-blink-features=AutomationControlled",  # Otomasyon belirtecini gizle
            "--disable-web-security",
            "--disable-features=IsolateOrigins,site-per-process",
            "--no-sandbox",
            "--window-size=1920,1080"
        ]
        
        # Önceki profili temizle
        if os.path.exists(user_data_dir):
            try:
                import shutil
                shutil.rmtree(user_data_dir)
                time.sleep(1)
            except:
                pass
        
        subprocess.Popen(chrome_args)
        print("Chrome debug modunda başlatıldı")
        time.sleep(5)  # Bekleme süresini artır
        return True
        
    except Exception as e:
        print(f"Chrome başlatma hatası: {e}")
        return False

def connect_to_existing_browser():
    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9223")
    
    # Basitleştirilmiş options - sadece gerekli olanlar
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    
    # ChromeDriver'ı otomatik indir
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def fill_form(driver, user_data, input_start_id, base_select_id):
    try:
        print("\nForm doldurma işlemi başlıyor...")
        print(f"Kullanılan ID'ler - Input: {input_start_id}, Select: {base_select_id}")
        time.sleep(5)

        # Text input alanları - XPath ile
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
                print(f"[ID: {input_start_id + id_offset}] {field_name} alanı dolduruluyor (Element ID: {current_id})...")
                
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
                print(f"[ID: {input_start_id + id_offset}] {field_name} alanı dolduruldu")
                
            except Exception as e:
                error_msg = f"[ID: {input_start_id + id_offset}] {field_name} doldurulurken hata: Message: {str(e)}"
                print(error_msg)
                play_error_sound()  # Hata sesi çal
                raise Exception(error_msg)

        # Dropdown menüler için yeni işlem
        dropdowns = {
            'gender': {
                'button': f'//*[@id="mat-select-value-1"]',  # ID'yi dinamik hale getir
                'value': user_data['gender'],
                'select_id': base_select_id  # base_select_id global değişkeninden gelecek
            },
            'nationality': {
                'button': f'//*[@id="mat-select-value-3"]',  # ID'yi dinamik hale getir
                'value': 'Turkiye',
                'select_id': base_select_id + 2  # gender'dan 2 fazla
            }
        }
        
        for dropdown_name, data in dropdowns.items():
            try:
                print(f"[ID: {data['select_id']}] {dropdown_name} seçimi yapılıyor...")
                # Dropdown'ı aç
                dropdown = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, f'//*[@id="mat-select-value-{data["select_id"]}"]'))
                )
                driver.execute_script("arguments[0].click();", dropdown)
                time.sleep(2)
                
                # JavaScript ile seçeneği bul ve tıkla
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
                
                # Gender için tam metin eşleşmesi kullan
                value_to_search = data['value']
                if dropdown_name == 'gender':
                    print(f"Gender değeri aranıyor: {value_to_search}")
                    found = driver.execute_script(js_script, value_to_search)
                else:
                    # Nationality için alternatif değerleri dene
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
                                    print(f"{dropdown_name} için alternatif değer {alt_value} seçildi")
                                    break

                if not found:
                    raise Exception(f"{value_to_search} seçeneği bulunamadı")
                
                print(f"{dropdown_name} seçimi tamamlandı")
                time.sleep(1)
                
            except Exception as e:
                error_msg = f"[ID: {data['select_id']}] {dropdown_name} seçilirken hata: {str(e)}"
                print(error_msg)
                play_error_sound()  # Hata sesi çal
                raise Exception(error_msg)

        # Save butonu - CSS Selector ile
        try:
            print("Form kaydediliyor...")
            
            # Sayfanın en altına scroll yapma işlemini iyileştir
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)
            driver.execute_script("window.scrollBy(0, -150);")  # Biraz yukarı kaydır
            time.sleep(1)
            
            # Save butonunu CSS Selector ile bul
            save_button_css = "button.mdc-button.btn-brand-orange"
            save_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, save_button_css))
            )
            
            # Butona görünür olana kadar scroll yap
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", save_button)
            time.sleep(2)
            
            # Farklı tıklama yöntemlerini dene
            try:
                # JavaScript ile tıkla
                driver.execute_script("arguments[0].click();", save_button)
                time.sleep(2)
                
                # URL değişimini bekle
                WebDriverWait(driver, 5).until(
                    lambda driver: "applicationdetails" in driver.current_url
                )
                print("Form başarıyla kaydedildi")
                return True
                
            except Exception as e:
                print(f"Tıklama hatası, farklı seçici deneniyor: {str(e)}")
                play_error_sound()  # Tıklama hatası için ses çal
                
                # Alternatif CSS selector dene
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
            print(f"Kaydetme hatası: {str(e)}")
            play_error_sound()  # Kaydetme hatası için ses çal
            raise
            
    except Exception as e:
        print(f"Form doldurma hatası: {str(e)}")
        play_error_sound()  # Form doldurma hatası için ses çal
        return False

def check_appointment_loop(driver):
    checkbox_base_ids = [1, 2, 3]  # İlk checkbox ID'leri
    input_base_id = 6     # Input'lar için başlangıç ID'si
    base_select_id = 1    # Select'ler için başlangıç ID'si (değiştirildi)
    
    while True:
        try:
            # Dashboard butonuna tıkla
            dashboard_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "/html/body/app-root/div/main/div/app-dashboard/section[1]/div/div[1]/div[2]/button/span[2]"))
            )
            dashboard_button.click()
            print("Dashboard butonuna tıklandı")
            time.sleep(2)
            
            # İlk sayfa checkbox'larını işaretle
            print("\nİlk sayfa checkbox işlemleri başlıyor...")
            checkbox_names = ["Conditions and Terms of Use", "Privacy Policy"]
            for i in range(2):
                checkbox_id = f"mat-mdc-checkbox-{checkbox_base_ids[i]}-input"
                print(f"[ID: {checkbox_base_ids[i]}] {checkbox_names[i]} checkbox'ı aranıyor (Element ID: {checkbox_id})...")
                checkbox = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, f'//*[@id="{checkbox_id}"]'))
                )
                driver.execute_script("arguments[0].click();", checkbox)
                time.sleep(1)
                print(f"[ID: {checkbox_base_ids[i]}] {checkbox_names[i]} checkbox'ı işaretlendi")
            
            # Start New Booking butonuna tıkla
            start_booking = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(.,'Start New Booking')]"))
            )
            driver.execute_script("arguments[0].click();", start_booking)
            print("Start New Booking tıklandı")
            time.sleep(2)
            
            # İkinci sayfa - Üçüncü checkbox
            checkbox_id = f"mat-mdc-checkbox-{checkbox_base_ids[2]}-input"
            print(f"\n[ID: {checkbox_base_ids[2]}] İkinci sayfa Terms and Conditions checkbox'ı aranıyor (Element ID: {checkbox_id})...")
            checkbox3 = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, f'//*[@id="{checkbox_id}"]'))
            )
            driver.execute_script("arguments[0].click();", checkbox3)
            time.sleep(1)
            print(f"[ID: {checkbox_base_ids[2]}] İkinci sayfa Terms and Conditions checkbox'ı işaretlendi")
            
            # İkinci sayfa Continue butonuna tıkla
            continue_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Continue')]"))
            )
            driver.execute_script("arguments[0].click();", continue_button)
            print("İkinci sayfa Continue butonuna tıklandı")
            time.sleep(2)
            
            # Form sayfasındaki işlemler - input ID'leri 6'şar artıyor
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
                    print("Form dolduruldu")
            
            # Randevu seçim sayfası
            if "applicationdetails" in driver.current_url:
                try:
                    print("\nRandevu seçim işlemi başlıyor...")
                    time.sleep(2)
                    
                    # İlk dropdown (Uzun Dönem) - base_select_id + 4
                    first_dropdown = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, f"#mat-select-value-{base_select_id + 4}"))
                    )
                    first_dropdown.click()
                    time.sleep(1)
                    
                    # "1 - Uzun Donem" seçeneğini seç
                    long_term_option = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), '1 - Uzun Donem')]"))
                    )
                    long_term_option.click()
                    time.sleep(2)
                    
                    # İkinci dropdown (ERASMUS/NAWA/ECS) - base_select_id + 6
                    second_dropdown = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, f"#mat-select-value-{base_select_id + 6}"))
                    )
                    second_dropdown.click()
                    time.sleep(1)
                    
                    # "5-ERASMUS/NAWA/ECS" seçeneğini seç
                    erasmus_option = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), '5-ERASMUS/NAWA/ECS')]"))
                    )
                    erasmus_option.click()
                    time.sleep(2)
                    
                    # Hata mesajını kontrol et
                    try:
                        error_message = WebDriverWait(driver, 3).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, "div.errorMessage.c-brand-error"))
                        )
                        print("Randevu bulunamadı, tekrar deneniyor...")
                        
                        # Dashboard'a dön
                        account_button = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.XPATH, '//*[@id="navbarDropdown"]'))
                        )
                        account_button.click()
                        time.sleep(1)
                        
                        dashboard_link = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.XPATH, '//*[@id="navbarToggle"]/ul/li/div/a[1]'))
                        )
                        dashboard_link.click()
                        print("Dashboard'a dönülüyor...")
                        time.sleep(5)
                        
                        # ID'leri güncelle (6 yerine 10 artır)
                        checkbox_base_ids = [x + 3 for x in checkbox_base_ids]  # Her ID'ye 3 ekle
                        input_base_id += 6     # Input ID'leri 6'şar artıyor
                        base_select_id += 10   # Select ID'leri 10'ar artıyor
                        continue
                        
                    except:
                        # Hata mesajı yoksa üçüncü dropdown'ı kontrol et
                        third_dropdown = WebDriverWait(driver, 5).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, f"#mat-select-value-{base_select_id + 8}"))
                        )
                        if "Uygulama merkezinizi seçin" in third_dropdown.text:
                            print("Randevu bulundu!")
                            play_success_sound()  # Added success sound
                            input("İşleme devam etmek için Enter'a basın...")  # Kullanıcının kontrol etmesi için bekle
                            return True
                
                except Exception as e:
                    print(f"Randevu seçim hatası: {e}")
                    checkbox_base_ids = [x + 3 for x in checkbox_base_ids]  # Her ID'ye 3 ekle
                    input_base_id += 6     # Input ID'leri 6'şar artıyor
                    base_select_id += 10   # Select ID'leri 10'ar artıyor
                    # Dashboard'a dön
                    try:
                        account_button = driver.find_element(By.XPATH, '//*[@id="navbarDropdown"]')
                        account_button.click()
                        time.sleep(1)
                        dashboard_link = driver.find_element(By.XPATH, '//*[@id="navbarToggle"]/ul/li/div/a[1]')
                        dashboard_link.click()
                        print("Hata sonrası dashboard'a dönülüyor...")
                        time.sleep(5)
                    except:
                        print("Dashboard'a dönüş başarısız, yeniden deneniyor...")
                    continue
                    
        except Exception as e:
            print(f"Genel hata: {e}")
            time.sleep(5)
            continue

def check_appointments(driver):
    # Global değişkenler tanımlayalım
    global_ids = {
        'checkbox_start': 1,  # Her döngüde checkbox ID'leri buradan başlayacak
        'input_start': 6,     # Input ID'leri buradan başlayacak
        'select_start': 1     # Select ID'leri 1'den başlayacak (değiştirildi)
    }
    
    while True:
        try:
            print("\nDashboard sayfası işlemleri başlıyor...")
            print(f"Mevcut ID'ler - Checkbox: {global_ids['checkbox_start']}, Input: {global_ids['input_start']}, Select: {global_ids['select_start']}")
            
            # İlk iki checkbox'ı işaretle
            checkbox_names = ["Conditions and Terms of Use", "Privacy Policy"]
            for i in range(2):
                try:
                    current_id = global_ids['checkbox_start'] + (i * 1)  # Her checkbox için 1 artır
                    checkbox_id = f"mat-mdc-checkbox-{current_id}-input"
                    print(f"[ID: {current_id}] {checkbox_names[i]} checkbox'ı aranıyor (Element ID: {checkbox_id})...")
                    
                    checkbox = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, f'//*[@id="{checkbox_id}"]'))
                    )
                    driver.execute_script("arguments[0].click();", checkbox)
                    time.sleep(1)
                    print(f"[ID: {current_id}] {checkbox_names[i]} checkbox'ı işaretlendi")
                    
                except Exception as e:
                    print(f"[ID: {current_id}] {checkbox_names[i]} checkbox hatası: {str(e)}")
                    # ID'leri güncelle ve yeniden dene
                    global_ids['checkbox_start'] += 3  # Her hata sonrası 3 artır
                    global_ids['input_start'] += 6    # Input ID'leri 6 artır
                    global_ids['select_start'] += 10  # Select ID'leri 10 artır
                    continue

            # Start New Booking butonu
            print("\nStart New Booking butonu aranıyor...")
            start_booking = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "button.btn-brand-orange"))
            )
            driver.execute_script("arguments[0].click();", start_booking)
            print("Start New Booking tıklandı")
            time.sleep(3)
            
            # İkinci sayfa işlemleri
            print("\nİkinci sayfa işlemleri başlıyor...")
            try:
                # Yeni checkbox'ı bekle ve tıkla
                print("İkinci sayfa checkbox'ı bekleniyor...")
                current_id = global_ids['checkbox_start'] + 2  # Üçüncü checkbox için
                checkbox_id = f"mat-mdc-checkbox-{current_id}-input"
                checkbox3 = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, f'//*[@id="{checkbox_id}"]'))
                )
                driver.execute_script("arguments[0].click();", checkbox3)
                time.sleep(1)
                print("İkinci sayfa checkbox'ı işaretlendi")
                
                # Continue butonuna tıkla
                continue_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button.mdc-button"))
                )
                driver.execute_script("arguments[0].click();", continue_button)
                print("Continue butonuna tıklandı")
                time.sleep(3)
                
                # Form sayfası kontrolü ve doldurma
                if "your-details" in driver.current_url:
                    print("\nForm sayfasına ulaşıldı, form dolduruluyor...")
                    user_data = {
                        'first_name': 'Yusuf',
                        'last_name': 'Aydin',  # AYDIN -> Aydin
                        'gender': 'Male',
                        'nationality': 'Turkiye',  # Turkey -> Turkiye olarak değiştirildi
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
                        print("Form dolduruldu ve kaydedildi")
                    else:
                        print("Form doldurma başarısız")
                        raise Exception("Form doldurma hatası")
                    
            except Exception as e:
                print(f"İkinci sayfa işlem hatası: {str(e)}")
                raise

            # Form doldurulduktan sonra randevu seçim işlemlerine devam et
            if "applicationdetails" in driver.current_url:
                try:
                    print("\nRandevu seçim işlemi başlıyor...")
                    print(f"Kullanılan Select ID: {global_ids['select_start']}")
                    time.sleep(3)  # Sayfanın tam yüklenmesini bekle
                    
                    # Sayfanın yüklenmesini bekle
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, ".mat-mdc-form-field"))
                    )
                    
                    # İlk dropdown (Uzun Dönem)
                    try:
                        print(f"İlk dropdown aranıyor (ID: {global_ids['select_start'] + 4})...")
                        first_dropdown = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, f"[id='mat-select-value-{global_ids['select_start'] + 4}']"))
                        )
                        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", first_dropdown)
                        time.sleep(1)
                        driver.execute_script("arguments[0].click();", first_dropdown)
                        time.sleep(2)
                        
                        # "1 - Uzun Donem" seçeneğini seç
                        long_term_option = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, "//span[normalize-space()='1 - Uzun Donem']"))
                        )
                        driver.execute_script("arguments[0].click();", long_term_option)
                        time.sleep(2)
                        
                    except Exception as e:
                        print(f"İlk dropdown hatası: {str(e)}")
                        raise
                    
                    # İkinci dropdown (ERASMUS/NAWA/ECS)
                    try:
                        print(f"İkinci dropdown aranıyor (ID: {global_ids['select_start'] + 6})...")
                        second_dropdown = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, f"[id='mat-select-value-{global_ids['select_start'] + 6}']"))
                        )
                        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", second_dropdown)
                        time.sleep(1)
                        driver.execute_script("arguments[0].click();", second_dropdown)
                        time.sleep(2)
                        
                        # "5-ERASMUS/NAWA/ECS" seçeneğini seç
                        erasmus_option = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, "//span[normalize-space()='5-ERASMUS/NAWA/ECS']"))
                        )
                        driver.execute_script("arguments[0].click();", erasmus_option)
                        time.sleep(2)
                        
                    except Exception as e:
                        print(f"İkinci dropdown hatası: {str(e)}")
                        raise
                    
                    while True:  # Randevu bulunana kadar döngüye devam et
                        try:
                            error_message = WebDriverWait(driver, 3).until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, "div.errorMessage.c-brand-error"))
                            )
                            print("Randevu bulunamadı, tekrar deneniyor...")
                            
                            # Dashboard'a dön
                            account_button = WebDriverWait(driver, 10).until(
                                EC.element_to_be_clickable((By.XPATH, '//*[@id="navbarDropdown"]'))
                            )
                            account_button.click()
                            time.sleep(1)
                            
                            dashboard_link = WebDriverWait(driver, 10).until(
                                EC.element_to_be_clickable((By.XPATH, '//*[@id="navbarToggle"]/ul/li/div/a[1]'))
                            )
                            dashboard_link.click()
                            print("Dashboard'a dönülüyor...")
                            time.sleep(5)
                            
                            # ID'leri güncelle ve yeniden başla
                            global_ids['checkbox_start'] += 3  # Her ID'ye 3 ekle
                            global_ids['input_start'] += 6     # Input ID'leri 6'şar artıyor
                            global_ids['select_start'] += 10   # Select ID'leri 10'ar artıyor
                            print(f"ID'ler güncellendi - Yeni değerler: Checkbox: {global_ids['checkbox_start']}, Input: {global_ids['input_start']}, Select: {global_ids['select_start']}")
                            break  # İç while döngüsünden çık, dış while döngüsüne dön
                            
                        except:
                            print("Randevu kontrol ediliyor...")
                            # Hata mesajı yoksa üçüncü dropdown'ı kontrol et
                            third_dropdown = WebDriverWait(driver, 5).until(
                                EC.element_to_be_clickable((By.CSS_SELECTOR, f"#mat-select-value-{global_ids['select_start'] + 8}"))
                            )
                            if "Uygulama merkezinizi seçin" in third_dropdown.text:
                                print("Randevu bulundu!")
                                play_success_sound()  # Already exists
                                input("İşleme devam etmek için Enter'a basın...")  # Already exists
                                return True
                
                except Exception as e:
                    print(f"Randevu seçim hatası: {e}")
                    play_error_sound()  # Genel hata durumunda da ses çal
                    # Hata durumunda da ID'leri güncelle ve tekrar dene
                    global_ids['checkbox_start'] += 3
                    global_ids['input_start'] += 6
                    global_ids['select_start'] += 10
                    print(f"Hata sonrası ID'ler güncellendi - Yeni değerler: Checkbox: {global_ids['checkbox_start']}, Input: {global_ids['input_start']}, Select: {global_ids['select_start']}")
                    continue

        except Exception as e:
            print(f"\nHATA DETAYI:")
            print(f"Tip: {type(e).__name__}")
            print(f"Mesaj: {str(e)}")
            play_error_sound()  # Genel hata durumunda da ses çal
            # Hata durumunda da ID'leri güncelle ve tekrar dene
            global_ids['checkbox_start'] += 3
            global_ids['input_start'] += 6
            global_ids['select_start'] += 10
            print(f"Genel hata sonrası ID'ler güncellendi - Yeni değerler: Checkbox: {global_ids['checkbox_start']}, Input: {global_ids['input_start']}, Select: {global_ids['select_start']}")
            continue

def start_bot():
    print("Chrome otomatik olarak debug modunda başlatılacak...")
    if not start_chrome_debug():
        print("Chrome başlatılamadı!")
        return
        
    print("\n1. Açılan Chrome penceresinde VFS sitesine giriş yapın")
    print("2. Dashboard sayfasına geldikten sonra Enter'a basın...")
    input()

    try:
        driver = connect_to_existing_browser()
        print("Mevcut Chrome oturumuna bağlanıldı")
        
        # Randevu kontrolü yap
        check_appointments(driver)
        
    except Exception as e:        print(f"Bağlantı hatası: {e}")
    
    finally:
        print("\nİşlem tamamlandı. Çıkmak için Enter'a basın...")
        input()

if __name__ == "__main__":
    # Önce gerekli kütüphaneyi yükle
    # pip install webdriver-manager
    start_bot()