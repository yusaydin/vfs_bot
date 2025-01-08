from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
from config import *

class VFSBot:
    def __init__(self):
        self.driver = webdriver.Chrome()
        self.wait = WebDriverWait(self.driver, 10)

    def check_availability(self):
        try:
            # Formun doldurulması
            self.select_appointment_center(FORM_VALUES['center'])
            self.select_category(FORM_VALUES['category'])
            self.select_subcategory(FORM_VALUES['subcategory'])

            # Tarih kontrolü
            calendar = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, SELECTORS['date_picker']))
            )
            
            # Müsait tarih var mı kontrolü
            available_dates = calendar.find_elements(By.CSS_SELECTOR, '.available-date')
            
            if available_dates:
                print("Müsait randevu bulundu!")
                # Bildirim gönderme veya ses çalma gibi ek işlemler eklenebilir
                return True
            
            return False

        except TimeoutException:
            print("Sayfa yüklenirken zaman aşımı oluştu.")
            return False
        except Exception as e:
            print(f"Hata oluştu: {str(e)}")
            return False

    def select_appointment_center(self, center):
        element = self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, SELECTORS['appointment_center']))
        )
        element.select_by_visible_text(center)

    def select_category(self, category):
        element = self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, SELECTORS['appointment_category']))
        )
        element.select_by_visible_text(category)

    def select_subcategory(self, subcategory):
        element = self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, SELECTORS['appointment_subcategory']))
        )
        element.select_by_visible_text(subcategory)

    def close(self):
        self.driver.quit()
