from rest_framework import generics, viewsets
from rest_framework.response import Response
from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from time import sleep
from selenium.common.exceptions import NoSuchElementException
from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
)
from bond.models import Bond, CashFlow
from datetime import datetime
from django.http import Http404
from typing import List


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                "bond_names",
                OpenApiTypes.STR,
                description="Comma separated list of bond names",
            )
        ]
    )
)
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

    def _get_element(
        self, driver: WebDriver, xpath: str, raise_error: bool = True
    ) -> WebElement:
        """Get element from driver and return float"""
        try:
            elem = driver.find_element(
                By.XPATH,
                xpath,
            )
        except NoSuchElementException:
            if raise_error:
                raise Http404(f"Elemento no encontrado {xpath}")
            else:
                return None

        return elem

    def _get_elements(
        self, driver: WebDriver, xpath: str, raise_error: bool = True
    ) -> List[WebElement]:
        """Get element from driver and return float"""
        try:
            elem = driver.find_elements(
                By.XPATH,
                xpath,
            )
        except NoSuchElementException:
            if raise_error:
                raise Http404(f"Elemento no encontrado {xpath}")
            else:
                return None

        return elem

    def _get_element_text(
        self, driver: WebDriver, xpath: str, raise_error: bool = True
    ) -> str:
        """Get element from driver and return float"""
        elem = self._get_element(driver, xpath, raise_error)
        if elem.is_displayed():
            return elem.text
        else:
            return elem.get_attribute("innerHTML")

    def sanitize_decimal(self, value: str) -> str:
        """Convert 32.500,00 to 32500.00"""
        return value.replace(".", "").replace(",", ".")

    def list(self, request, *args, **kwargs):
        bond_names = self.request.query_params.get("bond_names").split(",")
        response = []
        bond_status_responses = []
        for bond_name in bond_names:
            driver = webdriver.Chrome(options=self.set_chrome_options())

            bond = None
            cash_flows = []
            try:
                bond = Bond.objects.get(name=bond_name)
                cash_flows = bond.cash_flows.all()
            except Bond.DoesNotExist:
                pass

            if (
                bond is not None
                and len(cash_flows) > 0
                and bond.last_scrap_date == datetime.now().date()
            ):
                processed_cash_flow = map(
                    lambda x: {
                        "date": x.date,
                        "interest": x.interest,
                        "percentage": "{:.2f}%".format(
                            (float(x.interest) / float(bond.last_scrap_price)) * 100
                        ),
                        "bond_name": bond_name,
                    },
                    cash_flows,
                )
                response = response + list(processed_cash_flow)
            else:
                bad_gateway = True
                tries = 0
                while bad_gateway and tries <= 10:
                    driver.get(
                        f"https://bonds.mercapabbaco.com/bort/bondAnalysis?name={bond_name}"
                    )
                    bad_gateway = True if "Bad Gateway" in driver.page_source else False
                    tries += 1
                if bad_gateway is True:
                    bond_status_responses.append(
                        {"bond_name": bond_name, "status": "bad gateway"}
                    )

                login_button = self._get_element(
                    driver,
                    "/html/body/div[1]/main/section/div/div/div/form/div[3]/button",
                    False,
                )

                if login_button is not None:
                    self._get_element(
                        driver,
                        "/html/body/div[1]/main/section/div/div/div/form/div[2]/div/div[1]/div/input",
                    ).send_keys("fake@gmail.com")
                    self._get_element(
                        driver,
                        "/html/body/div[1]/main/section/div/div/div/form/div[2]/div/div[2]/div/input",
                    ).send_keys("musculus19")
                    login_button.click()
                    sleep(10)

                bad_gateway = True
                tries = 0
                while bad_gateway and tries <= 10:
                    loaded = self._get_element(
                        driver,
                        "/html/body/div[1]/div[3]/div/div/div/div[1]/div/h2/strong/strong",
                        False,
                    )
                    tries += 1
                    if loaded is not None:
                        bad_gateway = False
                    else:
                        sleep(10)
                if bad_gateway is True:
                    bond_status_responses.append(
                        {"bond_name": bond_name, "status": "loading"}
                    )
                else:
                    current_price = self.sanitize_decimal(
                        self._get_element_text(
                            driver,
                            "/html/body/div[1]/div[3]/div/div/div/div[2]/div[1]/div/div/div[1]/div[3]/div/strong",
                        )
                    )
                    current_tir = self.sanitize_decimal(
                        self._get_element_text(
                            driver,
                            "/html/body/div[1]/div[3]/div/div/div/div[2]/div[1]/div/div/div[1]/div[1]/div/strong",
                        )
                    )
                    current_duration = self.sanitize_decimal(
                        self._get_element_text(
                            driver,
                            "/html/body/div[1]/div[3]/div/div/div/div[2]/div[1]/div/div/div[1]/div[2]/div/strong",
                        )
                    )
                    current_parity = self.sanitize_decimal(
                        self._get_element_text(
                            driver,
                            "/html/body/div[1]/div[3]/div/div/div/div[2]/div[1]/div/div/div[1]/div[4]/div/strong",
                        )
                    )
                    currency_code = self._get_element_text(
                        driver,
                        "/html/body/div[1]/div[3]/div/div/div/div[2]/div[1]/div/div/div[1]/div[3]/div/span[2]/span[1]",
                    )

                    if bond is not None:
                        if cash_flows is not None and len(cash_flows) > 0:
                            processed_cash_flow = map(
                                lambda x: {
                                    "date": x.date,
                                    "interest": x.interest,
                                    "percentage": "{:.2f}%".format(
                                        (float(x.interest) / float(current_price)) * 100
                                    ),
                                    "bond_name": bond_name,
                                },
                                cash_flows,
                            )
                            response = response + list(processed_cash_flow)

                    if bond is None:
                        bond_type = self._get_element_text(
                            driver,
                            "/html/body/div[1]/div[3]/div/div/div/div[1]/div/h2/strong/small",
                        )
                        bond = Bond.objects.create(
                            name=bond_name,
                            type="corporative"
                            if "Obligación Negociable" in bond_type
                            else "national",
                            last_scrap_date=datetime.now(),
                            last_scrap_price=current_price,
                            last_scrap_tir=current_tir,
                            last_scrap_duration=current_duration,
                            last_scrap_parity=current_parity,
                            currency_code=currency_code,
                        )
                    if len(cash_flows) <= 0:
                        payments = self._get_elements(
                            driver,
                            "/html/body/div[1]/div[3]/div/div/div/div[2]/div[1]/div/div/div[3]/div[2]/div/div/div[2]/div/div[2]/table/tbody/tr",
                        )
                        for payment in payments:
                            date = payment.find_element(By.XPATH, "td[2]").text
                            interest = (
                                payment.find_element(By.XPATH, "td[3]")
                                .text.replace(".", "")
                                .replace(",", ".")
                            )
                            percentage = "{:.2f}%".format(
                                (float(interest) / float(current_price)) * 100
                            )
                            amortization = (
                                payment.find_element(By.XPATH, "td[4]")
                                .text.replace(".", "")
                                .replace(",", ".")
                            )
                            CashFlow.objects.create(
                                bond=bond,
                                date=datetime.strptime(date, "%d/%m/%Y"),
                                interest=interest,
                                amortization=amortization,
                            )
                            response.append(
                                {
                                    "date": date,
                                    "interest": interest,
                                    "percentage": percentage,
                                    "bond_name": bond_name,
                                }
                            )
                        next_page_button = None
                        try:
                            next_page_button = self._get_element(
                                driver,
                                "/html/body/div[1]/div[3]/div/div/div/div[2]/div[1]/div/div/div[3]/div[2]/div/div/div[2]/div/div[3]/div[2]/div/ul/li[2]/a",
                            )
                        except NoSuchElementException:
                            pass
                        if (
                            next_page_button is not None
                            and next_page_button.is_displayed()
                            and next_page_button.is_enabled()
                        ):
                            next_page_button.click()
                            sleep(2)
                            payments = self._get_elements(
                                driver,
                                "/html/body/div[1]/div[3]/div/div/div/div[2]/div[1]/div/div/div[3]/div[2]/div/div/div[2]/div/div[2]/table/tbody/tr",
                            )
                            for payment in payments:
                                date = payment.find_element(By.XPATH, "td[2]").text
                                interest = (
                                    payment.find_element(By.XPATH, "td[3]")
                                    .text.replace(".", "")
                                    .replace(",", ".")
                                )
                                percentage = "{:.2f}%".format(
                                    (float(interest) / float(current_price)) * 100
                                )
                                amortization = (
                                    payment.find_element(By.XPATH, "td[4]")
                                    .text.replace(".", "")
                                    .replace(",", ".")
                                )
                                CashFlow.objects.create(
                                    bond=bond,
                                    date=datetime.strptime(date, "%d/%m/%Y"),
                                    interest=interest,
                                    amortization=amortization,
                                )
                                response.append(
                                    {
                                        "date": date,
                                        "interest": interest,
                                        "percentage": percentage,
                                        "bond_name": bond_name,
                                    }
                                )
            bond_status_responses.append({"bond_name": bond_name, "status": "ok"})
            driver.quit()
        return Response(bond_status_responses)
