import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def vfs_login(email, password):
    # Undetected ChromeDriver kullan
    options = uc.ChromeOptions()
    options.arguments.extend(["--no-sandbox", "--disable-gpu"])
    driver = uc.Chrome(options=options)
    driver.maximize_window()
    
    try:
        # İlk yükleme için daha uzun süre bekle
        driver.get("https://visa.vfsglobal.com/tur/tr/pol/login")
        time.sleep(10)  # Cloudflare challenge için bekle
        
        print("Cloudflare kontrolü bekleniyor...")
        # Cloudflare geçene kadar bekle
        WebDriverWait(driver, 30).until(
            lambda x: "visa.vfsglobal.com" in driver.current_url
        )
        
        # Cookie popup'ı kapatmak için birden fazla deneme
        cookie_selectors = [
            "//button[contains(text(), 'Accept')]",
            "//button[contains(text(), 'Kabul Et')]",
            "//button[@class='mat-focus-indicator mat-button mat-button-base mat-primary']",
            "//*[contains(@class, 'cookie')]//*[contains(text(), 'Accept')]"
        ]

        for selector in cookie_selectors:
            try:
                cookie_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, selector))
                )
                cookie_button.click()
                print("Cookie popup kapatıldı")
                break
            except:
                continue

        # Sayfanın tam olarak yüklenmesi için bekleme
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "email"))
        )

        # Email alanı için birden fazla seçici dene
        email_selectors = [
            (By.ID, "mat-input-0"),
            (By.NAME, "username"),
            (By.XPATH, "//input[@type='email']"),
            (By.CSS_SELECTOR, "input[formcontrolname='username']")
        ]

        # Email girişi için tüm olası seçicileri dene
        email_field = None
        for selector in email_selectors:
            try:
                email_field = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located(selector)
                )
                if email_field.is_displayed():
                    break
            except:
                continue

        if email_field:
            driver.execute_script("arguments[0].scrollIntoView(true);", email_field)
            time.sleep(1)
            email_field.clear()
            email_field.send_keys(email)
            print("Email girildi")

        # Şifre alanı için birden fazla seçici dene
        password_selectors = [
            (By.ID, "mat-input-1"),
            (By.NAME, "password"),
            (By.XPATH, "//input[@type='password']"),
            (By.CSS_SELECTOR, "input[formcontrolname='password']")
        ]

        # Şifre girişi için tüm olası seçicileri dene
        password_field = None
        for selector in password_selectors:
            try:
                password_field = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located(selector)
                )
                if password_field.is_displayed():
                    break
            except:
                continue

        if password_field:
            driver.execute_script("arguments[0].scrollIntoView(true);", password_field)
            time.sleep(1)
            password_field.clear()
            password_field.send_keys(password)
            print("Şifre girildi")

        # Login butonu için bekle ve tıkla
        login_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']"))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", login_button)
        time.sleep(1)
        login_button.click()
        
        # Giriş işleminin tamamlanmasını bekle
        time.sleep(15)
        
    except Exception as e:
        print(f"Hata oluştu: {e}")
        print("Tarayıcı açık bırakılıyor...")
        input("Kapatmak için bir tuşa basın...")
    
    finally:
        driver.quit()

if __name__ == "__main__":
    # Önce undetected-chromedriver'ı yükleyin:
    # pip install undetected-chromedriver
    email = "yusufaydin620@gmail.com"
    password = "your_password"
    vfs_login(email, password)