from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import subprocess
import os

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

def fill_form(driver, user_data):
    try:
        print("\nForm doldurma işlemi başlıyor...")
        time.sleep(5)  # Sayfa tam yüklenene kadar bekle
        
        # Text input alanları - XPath ile
        inputs = {
            'first_name': '//*[@id="mat-input-6"]',
            'last_name': '//*[@id="mat-input-7"]',
            'passport': '//*[@id="mat-input-8"]',
            'country_code': '//*[@id="mat-input-9"]',
            'phone': '//*[@id="mat-input-10"]',
            'email': '//*[@id="mat-input-11"]'
        }
        
        # Her bir input alanını doldur
        for field_name, xpath in inputs.items():
            try:
                print(f"{field_name} alanı dolduruluyor...")
                element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, xpath))
                )
                element.clear()
                time.sleep(0.5)
                
                # Ülke kodu ve telefon numarası için özel işlem
                if field_name == 'country_code':
                    element.send_keys('+90')
                else:
                    element.send_keys(user_data[field_name])
                time.sleep(1)
                print(f"{field_name} alanı dolduruldu")
            except Exception as e:
                print(f"{field_name} doldurulurken hata: {str(e)}")
                raise

        # Dropdown menüler için yeni işlem
        dropdowns = {
            'gender': {
                'button': '//*[@id="mat-select-value-1"]',
                'value': user_data['gender']
            },
            'nationality': {
                'button': '//*[@id="mat-select-value-3"]',
                'value': 'Turkiye'  # Sabit değer olarak Turkiye kullanıyoruz
            }
        }
        
        for dropdown_name, data in dropdowns.items():
            try:
                print(f"{dropdown_name} seçimi yapılıyor...")
                # Dropdown'ı aç
                dropdown = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, data['button']))
                )
                driver.execute_script("arguments[0].click();", dropdown)
                time.sleep(2)
                
                user_data = {
                    # ...other fields...
                    'nationality': 'Turkish',  # veya 'Turkey' ya da 'Türkiye' deneyebilirsiniz
                    # ...other fields...
                }                # Scroll ve seçim için JavaScript kullan
                js_script = """
                function selectOption(searchText) {
                    const panel = document.querySelector('.mat-mdc-select-panel');
                    const options = Array.from(panel.querySelectorAll('mat-option'));
                    
                    for (let option of options) {
                        if (option.textContent.toLowerCase().includes(searchText.toLowerCase())) {
                            // Scroll to option
                            option.scrollIntoView({behavior: 'smooth', block: 'center'});
                            
                            // Wait a bit and click
                            setTimeout(() => {
                                option.click();
                            }, 500);
                            
                            return true;
                        }
                    }
                    return false;
                }
                return selectOption(arguments[0]);
                """
                
                # JavaScript ile seçeneği bul ve tıkla
                found = driver.execute_script(js_script, data['value'])
                time.sleep(2)  # Scroll ve tıklama için bekle
                
                if not found:
                    # Alternatif değerler dene
                    alternate_values = {
                        'Turkiye': ['Turkey', 'Turkish', 'Türkiye'],
                        'Turkey': ['Turkiye', 'Turkish', 'Türkiye']
                    }
                    
                    if data['value'] in alternate_values:
                        for alt_value in alternate_values[data['value']]:
                            found = driver.execute_script(js_script, alt_value)
                            if found:
                                print(f"{dropdown_name} için alternatif değer {alt_value} seçildi")
                                break
                
                if not found:
                    raise Exception(f"{data['value']} seçeneği bulunamadı")
                
                print(f"{dropdown_name} seçimi tamamlandı")
                time.sleep(1)
            except Exception as e:
                print(f"{dropdown_name} seçilirken hata: {str(e)}")
                raise

        # Save butonu - Kesin XPath ile
        try:
            print("Form kaydediliyor...")
            # Önce sayfanın en altına scroll yap
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)
            
            # Save butonunu XPath ile bul
            save_button_xpath = "//button[contains(@class, 'mdc-button') and contains(., 'Save')]"
            save_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, save_button_xpath))
            )
            
            # Butona görünür olana kadar scroll yap
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", save_button)
            time.sleep(1)
            
            # JavaScript click() kullan
            driver.execute_script("arguments[0].click();", save_button)
            print("Save butonuna tıklandı")
            time.sleep(3)
            
            # Butonun tıklandığından emin ol
            try:
                # URL değişimini bekle
                WebDriverWait(driver, 5).until(
                    lambda driver: "applicationdetails" in driver.current_url
                )
                print("Form başarıyla kaydedildi")
                return True
            except:
                # URL değişmediyse butona tekrar tıklamayı dene
                print("İlk tıklama başarısız oldu, tekrar deneniyor...")
                save_button.click()  # Normal click() ile dene
                time.sleep(3)
                return True
            
        except Exception as e:
            print(f"Kaydetme hatası: {str(e)}")
            raise
            
    except Exception as e:
        print(f"Form doldurma hatası: {str(e)}")
        return False

def check_appointment_loop(driver):
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
            print("İlk sayfa checkbox'ları işaretleniyor...")
            for checkbox_id in ["mat-mdc-checkbox-1-input", "mat-mdc-checkbox-2-input"]:
                checkbox = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, f'//*[@id="{checkbox_id}"]'))
                )
                driver.execute_script("arguments[0].click();", checkbox)
                time.sleep(1)
                print(f"Checkbox {checkbox_id} işaretlendi")
            
            # Start New Booking butonuna tıkla
            start_booking = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(.,'Start New Booking')]"))
            )
            driver.execute_script("arguments[0].click();", start_booking)
            print("Start New Booking tıklandı")
            time.sleep(2)
            
            # İkinci sayfa - Yeni checkbox'ı bekle ve tıkla
            print("İkinci sayfa checkbox'ı bekleniyor...")
            checkbox3 = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="mat-mdc-checkbox-3-input"]'))
            )
            driver.execute_script("arguments[0].click();", checkbox3)
            time.sleep(1)
            print("İkinci sayfa checkbox'ı işaretlendi")
            
            # İkinci sayfa Continue butonuna tıkla
            continue_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Continue')]"))
            )
            driver.execute_script("arguments[0].click();", continue_button)
            print("İkinci sayfa Continue butonuna tıklandı")
            time.sleep(2)
            
            # Form sayfasındaki işlemler
            if "your-details" in driver.current_url:
                user_data = {
                    'first_name': 'Yusuf',  # Kendi bilgilerinizi girin
                    'last_name': 'Aydin',
                    'gender': 'Male',
                    'nationality': 'Turkey',
                    'passport': 'U123456',
                    'country_code': '+90',
                    'phone': '5551234567',
                    'email': 'yusufaydin620@gmail.com'
                }
                if fill_form(driver, user_data):
                    print("Form dolduruldu")
            
            # Randevu seçim sayfası
            if "applicationdetails" in driver.current_url:
                try:
                    # İlk iki seçim kutusunu doldur
                    for select_id in ['mat-select-value-9', 'mat-select-value-11']:
                        dropdown = WebDriverWait(driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, f'//*[@id="{select_id}"]'))
                        )
                        dropdown.click()
                        # İlk seçeneği seç
                        first_option = WebDriverWait(driver, 5).until(
                            EC.presence_of_element_located((By.XPATH, "//mat-option[1]"))
                        )
                        first_option.click()
                        time.sleep(1)
                    
                    # Üçüncü seçim kutusunu kontrol et
                    try:
                        third_dropdown = WebDriverWait(driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, '//*[@id="mat-select-value-13"]'))
                        )
                        third_dropdown.click()
                        print("Randevu bulundu!")
                        return True
                    except:
                        # Dashboard'a dön
                        account_button = driver.find_element(By.XPATH, '//*[@id="navbarDropdown"]')
                        account_button.click()
                        dashboard_link = driver.find_element(By.XPATH, '//*[@id="navbarToggle"]/ul/li/div/a[1]')
                        dashboard_link.click()
                        print("Randevu bulunamadı, tekrar deneniyor...")
                        time.sleep(5)
                        continue  # Döngüyü baştan başlat
                        
                except Exception as e:
                    print(f"Randevu seçim hatası: {e}")
                    # Dashboard'a dön
                    account_button = driver.find_element(By.XPATH, '//*[@id="navbarDropdown"]')
                    account_button.click()
                    time.sleep(1)
                    dashboard_link = driver.find_element(By.XPATH, '//*[@id="navbarToggle"]/ul/li/div/a[1]')
                    dashboard_link.click()
                    print("Dashboard'a dönülüyor...")
                    time.sleep(5)  # Dashboard'ın yüklenmesi için bekle
                    continue  # Döngüyü baştan başlat
            
        except Exception as e:
            print(f"Döngü hatası: {e}")
            time.sleep(5)
            # Hata durumunda da dashboard'a dönmeyi dene
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

def check_appointments(driver):
    try:
        print("\nDashboard sayfası işlemleri başlıyor...")
        
        # İlk sayfa checkbox'ları
        checkboxes = {
            "Birinci": '//*[@id="mat-mdc-checkbox-1-input"]',
            "İkinci": '//*[@id="mat-mdc-checkbox-2-input"]'
        }
        
        for name, xpath in checkboxes.items():
            try:
                print(f"{name} checkbox aranıyor...")
                checkbox = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, xpath))
                )
                driver.execute_script("arguments[0].click();", checkbox)
                time.sleep(1)
                print(f"{name} checkbox işaretlendi")
            except Exception as e:
                print(f"{name} checkbox hatası: {str(e)}")
                raise
        
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
            checkbox3 = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="mat-mdc-checkbox-3-input"]'))
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
                    'last_name': 'Aydın',
                    'gender': 'Male',
                    'nationality': 'Turkiye',  # Turkey -> Turkiye olarak değiştirildi
                    'passport': 'U123456',
                    'phone': '5551234567',
                    'email': 'yusufaydin620@gmail.com'
                }
                
                if fill_form(driver, user_data):
                    print("Form dolduruldu ve kaydedildi")
                else:
                    print("Form doldurma başarısız")
                    raise Exception("Form doldurma hatası")
                
        except Exception as e:
            print(f"İkinci sayfa işlem hatası: {str(e)}")
            raise

    except Exception as e:
        print(f"\nHATA DETAYI:")
        print(f"Tip: {type(e).__name__}")
        print(f"Mesaj: {str(e)}")
        print(f"Mevcut URL: {driver.current_url}")
        print("Sayfa kaynağı kontrol ediliyor...")
        try:
            print(f"Sayfa başlığı: {driver.title}")
            print(f"Görünür elementler: {[elem.text for elem in driver.find_elements(By.XPATH, '//*[text()]')][:5]}")
        except:
            print("Sayfa detayları alınamadı")
        raise

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