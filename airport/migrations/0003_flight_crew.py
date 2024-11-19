# Generated by Django 5.1.3 on 2024-11-19 09:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("airport", "0002_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="flight",
            name="crew",
            field=models.ManyToManyField(related_name="flights", to="airport.crew"),
        ),
    ]
