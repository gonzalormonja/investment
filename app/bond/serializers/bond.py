from rest_framework import serializers


class HistoricalPriceSerializer(serializers.Serializer):
    """Serializer for Historical Prices"""

    price = serializers.FloatField()
    date = serializers.CharField()


class BondSerializer(serializers.Serializer):
    """Serializer for Bond's"""

    bond_name = serializers.CharField()
    current_price = serializers.FloatField()
    historical_prices = serializers.ListField(child=HistoricalPriceSerializer())
