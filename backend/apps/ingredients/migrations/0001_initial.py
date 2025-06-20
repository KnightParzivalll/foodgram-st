# Generated by Django 5.2.3 on 2025-06-05 20:20

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Ingredient",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        max_length=128, verbose_name="Название ингредиента"
                    ),
                ),
                (
                    "measurement_unit",
                    models.CharField(max_length=64, verbose_name="Единицы измерения"),
                ),
            ],
            options={
                "verbose_name": "Ингредиент",
                "verbose_name_plural": "Ингредиенты",
                "ordering": ("name",),
                "constraints": [
                    models.UniqueConstraint(
                        fields=("name", "measurement_unit"), name="unique_ingredient"
                    )
                ],
            },
        ),
    ]
