import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class LinkedInCollector:
    def __init__(self):
        service = Service("D:\\Masaüstü\\chromedriver-win64(sonchromesurumu)\\chromedriver-win64\\chromedriver.exe")
        options = Options()

        user_profile_path = "C:\\Users\\Asus\\AppData\\Local\\Google\\Chrome\\User Data"
        options.add_argument(f"--user-data-dir={user_profile_path}")
        options.add_argument("--profile-directory=Profile 5")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-popup-blocking")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("detach", True)

        self.driver = webdriver.Chrome(service=service, options=options)
        self.wait = WebDriverWait(self.driver, 10)

    def search_profiles(self, search_query):
        search_url = f"https://www.linkedin.com/search/results/people/?keywords={search_query}"
        self.driver.get(search_url)
        time.sleep(5)

    def scroll_down(self):
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        for _ in range(3):  # 3 defa kaydırma yaparak sayfanın tamamını yükle
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

    def retrieve_profiles(self, container, max_pages=5):
        for page in range(max_pages):
            self.scroll_down()
            try:
                self._get_profiles_on_page(container)
                next_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, '//button[contains(@aria-label, "Sonraki")]')))
                next_button.click()
                time.sleep(5)
            except Exception as e:
                print(f"Sonraki sayfaya geçerken hata: {e}")
                break
        print(f"Toplam {len(container)} profil toplandı.")

    def _get_profiles_on_page(self, container):
        try:
            profiles = self.wait.until(EC.presence_of_all_elements_located((By.XPATH, '//div[contains(@class, "reusable-search__result-container")]')))
            for profile in profiles:
                try:
                    name = profile.find_element(By.XPATH, './/span[contains(@class, "entity-result__title-text")]//a').text
                    title = profile.find_element(By.XPATH, './/div[contains(@class, "entity-result__primary-subtitle")]').text
                    location = profile.find_element(By.XPATH, './/div[contains(@class, "entity-result__secondary-subtitle")]').text
                    profile_link = profile.find_element(By.XPATH, './/a[contains(@href, "/in/")]').get_attribute('href')
                    container.append({
                        'name': name,
                        'title': title,
                        'location': location,
                        'profile_link': profile_link
                    })
                except Exception as e:
                    print(f'Profil verisi alınırken hata oluştu: {e}')
        except Exception as e:
            print(f"Profil verilerini çekerken hata oluştu: {e}")

    def save_to_json(self, data, filename="linkedin_profiles.json"):
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"Veriler {filename} dosyasına kaydedildi.")

    def close(self):
        self.driver.quit()

# Kullanım
search_query = 'Selçuk Üniversitesi" + "Kamu" + "Müdür" / "Başkan" / "Genel Müdür'
collector = LinkedInCollector()
collector.search_profiles(search_query)

profiles = []
collector.retrieve_profiles(profiles)
collector.save_to_json(profiles)
collector.close()

# Sonuçları terminale yazdır
for profile in profiles:
    print(profile)