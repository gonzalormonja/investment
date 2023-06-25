from django.db.models import Model, CharField

bond_types = (
    ("corporative", "Corporative"),
    ("national", "National"),
)


class Bond(Model):
    """Bond model"""

    name = CharField(max_length=255)
    type = CharField(max_length=255, choices=bond_types)
