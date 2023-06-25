from rest_framework import serializers


class BondRatioSerializer(serializers.Serializer):
    """Serializer for Bond ratio"""

    ratio_average = serializers.FloatField()
    standard_deviation = serializers.FloatField()
    standard_deviation_limits = serializers.ListField(child=serializers.FloatField())
    actual_ratio = serializers.FloatField()
    recommendation = serializers.CharField()
