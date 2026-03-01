from django.contrib.postgres.operations import TrigramExtension
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("flags", "0003_difficultytierstate_tiershowncountry"),
    ]

    operations = [
        TrigramExtension(),
    ]
