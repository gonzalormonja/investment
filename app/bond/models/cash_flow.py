from django.db.models import (
    Model,
    ForeignKey,
    CASCADE,
    DateField,
    FloatField,
)

from .bond import Bond


class CashFlow(Model):
    """Bond model"""

    bond = ForeignKey(Bond, related_name="cash_flows", on_delete=CASCADE)
    date = DateField()
    interest = FloatField()
    amortization = FloatField()
