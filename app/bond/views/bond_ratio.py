from rest_framework import viewsets, generics, status
from bond.serializers import BondRatioSerializer
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
)
from datetime import datetime
from rest_framework.response import Response
import statistics


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter("bond_1", OpenApiTypes.STR, description="First bond"),
            OpenApiParameter("bond_2", OpenApiTypes.STR, description="Second bond"),
        ]
    )
)
class BondRatioViewSet(generics.ListAPIView, viewsets.GenericViewSet):
    """Views for Bond's"""

    serializer_class = BondRatioSerializer

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
        bond_1 = self.request.query_params.get("bond_1")
        bond_2 = self.request.query_params.get("bond_2")

        url_1 = f"https://rava.com/perfil/{bond_1}D"
        url_2 = f"https://rava.com/perfil/{bond_2}D"

        driver_1 = webdriver.Chrome(options=self.set_chrome_options())

        driver_1.get(url_1)

        historical_prices_elements_1 = driver_1.find_elements(
            By.XPATH, '//*[@id="scroll"]/table/tr'
        )

        historical_prices_1 = {}
        for index, price in enumerate(historical_prices_elements_1):
            if index != 0:
                price_value = price.find_element(
                    By.XPATH, f'//*[@id="scroll"]/table/tr[{index+1}]/td[5]'
                ).text.replace(",", ".")
                date = price.find_element(
                    By.XPATH, f'//*[@id="scroll"]/table/tr[{index+1}]/td[1]'
                ).text
                historical_prices_1[date] = price_value

        driver_2 = webdriver.Chrome(options=self.set_chrome_options())

        driver_2.get(url_2)

        historical_prices_elements_2 = driver_2.find_elements(
            By.XPATH, '//*[@id="scroll"]/table/tr'
        )

        ratios = {}
        last_ratio = {
            "date": datetime.strptime("01/01/1990", "%d/%m/%Y").date(),
            "ratio": 0,
        }
        for index, price in enumerate(historical_prices_elements_2):
            if index != 0:
                price_value = price.find_element(
                    By.XPATH, f'//*[@id="scroll"]/table/tr[{index+1}]/td[5]'
                ).text.replace(",", ".")
                date = price.find_element(
                    By.XPATH, f'//*[@id="scroll"]/table/tr[{index+1}]/td[1]'
                ).text
                date_ratio = float(historical_prices_1[date]) / float(price_value)
                ratios[date] = date_ratio
                if datetime.strptime(date, "%d/%m/%Y").date() > last_ratio["date"]:
                    last_ratio["date"] = datetime.strptime(date, "%d/%m/%Y").date()
                    last_ratio["ratio"] = date_ratio

        ratio_average = statistics.mean(ratios.values())

        standard_deviation = statistics.stdev(ratios.values())

        recommendation = "no-action"
        if last_ratio["ratio"] <= ratio_average - standard_deviation * 2:
            recommendation = "strong-buy"
        elif last_ratio["ratio"] <= ratio_average - standard_deviation * 1.4:
            recommendation = "buy"
        elif last_ratio["ratio"] >= ratio_average + standard_deviation * 1.4:
            recommendation = "sell"
        elif last_ratio["ratio"] >= ratio_average + standard_deviation * 2:
            recommendation = "strong-sell"

        standard_deviation_limits = [
            ratio_average - standard_deviation * 2,
            ratio_average - standard_deviation * 1.4,
            ratio_average + standard_deviation * 1.4,
            ratio_average + standard_deviation * 2,
        ]
        obj = {
            "ratio_average": ratio_average,
            "standard_deviation": standard_deviation,
            "standard_deviation_limits": standard_deviation_limits,
            "actual_ratio": last_ratio["ratio"],
            "recommendation": recommendation,
        }
        obj_serializer = BondRatioSerializer(obj).data
        return Response(obj_serializer, status=status.HTTP_200_OK)
