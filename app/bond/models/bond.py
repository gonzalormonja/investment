from django.db.models import Model, CharField, DateField, FloatField
from datetime import datetime

bond_types = (
    ("corporative", "Corporative"),
    ("national", "National"),
)


class Bond(Model):
    """Bond model"""

    name = CharField(max_length=255)
    type = CharField(max_length=255, choices=bond_types)
    currency_code = CharField(max_length=255, default="usd")
    last_scrap_date = DateField(default=datetime.now())
    last_scrap_price = FloatField(default=0)
    last_scrap_tir = FloatField(default=0)
    last_scrap_parity = FloatField(default=0)
    last_scrap_duration = FloatField(default=0)
