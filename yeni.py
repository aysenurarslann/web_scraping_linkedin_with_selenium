import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class LinkedInCollector:
    def __init__(self):
        service = Service("D:\Masaüstü\chromedriver-win64(sonchromesurumu)\chromedriver-win64\chromedriver.exe")  # Kendi driver yolunu yaz
        options = Options()

        # Mevcut Chrome profilini kullanma
        user_profile_path = "C:\\Users\\Asus\\AppData\\Local\\Google\\Chrome\\User Data"
        options.add_argument(f"--user-data-dir={user_profile_path}")
        options.add_argument("--profile-directory=Profile 5")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-popup-blocking")

        # Bot tespit edilmemesi için ayarlar
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        options.add_argument("--disable-blink-features=AutomationControlled")

        # Tarayıcıyı açık bırakmak için
        options.add_experimental_option("detach", True)

        # Tarayıcı başlatma
        self.driver = webdriver.Chrome(service=service, options=options)

    def search_profiles(self, search_query):
        """ LinkedIn'de belirli bir kelime ile arama yapar. """
        search_url = f"https://www.linkedin.com/search/results/people/?keywords={search_query}"
        self.driver.get(search_url)
        time.sleep(5)  # Sayfanın yüklenmesini bekle

    def retrieve_profiles(self, container, max_scroll=5, max_pages=5):
        """ Arama sonuçlarından profilleri toplar ve sayfalar arasında geçiş yapar. """
        wait = WebDriverWait(self.driver, 10)

        # Sayfaları gez
        for page in range(max_pages):
            try:
                # Sayfanın tüm profillerini çek
                self._get_profiles_on_page(container)

                # Sonraki sayfaya geç
                next_button = self.driver.find_element(By.XPATH, '//button[contains(@aria-label, "Sonraki")]')
                if next_button:
                    next_button.click()
                    time.sleep(3)  # Sayfa geçişi için bekleme
                else:
                    print("Sonraki butonuna tıklanamadı, son sayfadasınız.")
                    break

            except Exception as e:
                print(f"Sayfa geçişi sırasında hata oluştu: {e}")
                break

        print(f"Toplam {len(container)} profil toplandı.")

    def _get_profiles_on_page(self, container):
        """ Mevcut sayfadan profilleri toplar. """
        wait = WebDriverWait(self.driver, 10)

        try:
            profiles = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//div[contains(@class, "entity-result__item")]')))
            for profile in profiles:
                try:
                    # İsim ve profil başlığı
                    name = profile.find_element(By.XPATH, './/span[@dir="ltr"]').text
                    title = profile.find_element(By.XPATH, './/div[contains(@class, "entity-result__primary-subtitle")]').text
                    location = profile.find_element(By.XPATH, './/div[contains(@class, "entity-result__secondary-subtitle")]').text

                    # Profil bağlantısı
                    profile_link = profile.find_element(By.XPATH, './/a[contains(@href, "/in/")]').get_attribute('href')

                    # Verileri kaydet
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

    def close(self):
        """ Tarayıcıyı kapatır. """
        self.driver.quit()

# Kullanım
search_query = '"Elektrik Elektronik Mühendisi" OR "Kamu Yönetici" OR "Kamu Sektörü" AND "Selçuk Üniversitesi" OR "Konya Teknik Üniversitesi"'
collector = LinkedInCollector()
collector.search_profiles(search_query)

profiles = []
collector.retrieve_profiles(profiles)
collector.close()

# Toplanan verileri yazdır
for profile in profiles:
    print(profile)
