from rest_framework import generics, viewsets
from rest_framework.response import Response
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from time import sleep
from selenium.common.exceptions import NoSuchElementException


class CashFlowViewSet(generics.ListAPIView, viewsets.GenericViewSet):
    # serializer_class = CashFlowSerializer

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

    def list(self, request, *args, **kwargs):
        corporate_bond_name = kwargs["corporate_bond_name"]

        driver = webdriver.Chrome(options=self.set_chrome_options())

        driver.get(
            f"https://bonds.mercapabbaco.com/bort/bondAnalysis?name={corporate_bond_name}"
        )

        login_button = driver.find_element(
            By.XPATH, "/html/body/div[1]/main/section/div/div/div/form/div[3]/button"
        )
        if login_button:
            driver.find_element(
                By.XPATH,
                "/html/body/div[1]/main/section/div/div/div/form/div[2]/div/div[1]/div/input",
            ).send_keys("fake@gmail.com")
            driver.find_element(
                By.XPATH,
                "/html/body/div[1]/main/section/div/div/div/form/div[2]/div/div[2]/div/input",
            ).send_keys("musculus19")
            login_button.click()
            sleep(15)

        payments = driver.find_elements(
            By.XPATH,
            "/html/body/div[1]/div[3]/div/div/div/div[2]/div[1]/div/div/div[3]/div[2]/div/div/div[2]/div/div[2]/table/tbody/tr",
        )
        response = []
        for index, payment in enumerate(payments):
            date = payment.find_element(By.XPATH, "td[2]").text
            interest = payment.find_element(By.XPATH, "td[3]").text.replace(",", ".")
            current_price = (
                driver.find_element(
                    By.XPATH,
                    "/html/body/div[1]/div[3]/div/div/div/div[2]/div[1]/div/div/div[1]/div[3]/div/strong",
                )
                .get_attribute("innerHTML")
                .replace(",", ".")
            )
            percentage = "{:.2f}%".format(
                (float(interest) / float(current_price)) * 100
            )
            response.append(
                {"date": date, "interest": interest, "percentage": percentage}
            )
        next_page_button = False
        try:
            next_page_button = driver.find_element(
                By.XPATH,
                "/html/body/div[1]/div[3]/div/div/div/div[2]/div[1]/div/div/div[3]/div[2]/div/div/div[2]/div/div[3]/div[2]/div/ul/li[2]/a",
            )
        except NoSuchElementException:
            pass
        if next_page_button and next_page_button.is_enabled():
            next_page_button.click()
            sleep(2)
            payments = driver.find_elements(
                By.XPATH,
                "/html/body/div[1]/div[3]/div/div/div/div[2]/div[1]/div/div/div[3]/div[2]/div/div/div[2]/div/div[2]/table/tbody/tr",
            )
            for index, payment in enumerate(payments):
                date = payment.find_element(By.XPATH, "td[2]").text
                interest = payment.find_element(By.XPATH, "td[3]").text.replace(
                    ",", "."
                )
                current_price = (
                    driver.find_element(
                        By.XPATH,
                        "/html/body/div[1]/div[3]/div/div/div/div[2]/div[1]/div/div/div[1]/div[3]/div/strong",
                    )
                    .get_attribute("innerHTML")
                    .replace(",", ".")
                )
                percentage = "{:.2f}%".format(
                    (float(interest) / float(current_price)) * 100
                )
                response.append(
                    {"date": date, "interest": interest, "percentage": percentage}
                )
        return Response(response)
