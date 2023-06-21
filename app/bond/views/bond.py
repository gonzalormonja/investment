from rest_framework import viewsets, generics
from bond.serializers import BondSerializer
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options


class BondViewSet(generics.RetrieveAPIView, viewsets.GenericViewSet):
    """Views for Bond's"""

    serializer_class = BondSerializer

    def set_chrome_options(self) -> Options:
        """Sets chrome options for Selenium.
        Chrome options for headless browser is enabled.
        """
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_prefs = {}
        chrome_options.experimental_options["prefs"] = chrome_prefs
        chrome_prefs["profile.default_content_settings"] = {"images": 2}
        return chrome_options

    def get_object(self):
        url = "https://rava.com/perfil/AL30D"
        driver = webdriver.Chrome(options=self.set_chrome_options())
        driver.get(url)

        current_price = driver.find_element(
            By.XPATH, '//*[@id="izqCotiza"]/p[1]'
        ).text.replace(",", ".")
        historical_prices_elements = driver.find_elements(
            By.XPATH, '//*[@id="scroll"]/table/tr'
        )

        historical_prices = []
        for index, price in enumerate(historical_prices_elements):
            if index != 0:
                price_value = price.find_element(
                    By.XPATH, f'//*[@id="scroll"]/table/tr[{index+1}]/td[5]'
                ).text.replace(",", ".")
                date = price.find_element(
                    By.XPATH, f'//*[@id="scroll"]/table/tr[{index+1}]/td[1]'
                ).text
                historical_prices.append({"price": price_value, "date": date})

        return {
            "bond_name": "AL30D",
            "current_price": current_price,
            "historical_prices": historical_prices,
        }
