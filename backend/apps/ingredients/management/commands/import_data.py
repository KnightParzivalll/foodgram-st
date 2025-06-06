import json
import os

from django.core.management.base import BaseCommand
from django.db import transaction
from django.conf import settings

from apps.ingredients.models import Ingredient


class Command(BaseCommand):
    help = "Импортирует ингредиенты из файла ingredients.json"

    def handle(self, *args, **kwargs):
        path = os.path.join(settings.BASE_DIR, "data", "ingredients.json")

        if not os.path.exists(path):
            self.stdout.write(self.style.ERROR(f"Файл {path} не найден"))
            return

        with open(path, encoding="utf-8") as file:
            try:
                data = json.load(file)
            except json.JSONDecodeError as e:
                self.stdout.write(self.style.ERROR(f"Ошибка парсинга JSON: {e}"))
                return

        existing = set(Ingredient.objects.values_list("name", "measurement_unit"))

        new_ingredients = []
        skipped = 0

        with transaction.atomic():
            for item in data:
                try:
                    name = item["name"]
                    unit = item["measurement_unit"]
                except KeyError as e:
                    self.stdout.write(
                        self.style.WARNING(f"Пропущено поле {e} в элементе: {item}")
                    )
                    skipped += 1
                    continue

                if (name, unit) not in existing:
                    new_ingredients.append(Ingredient(name=name, measurement_unit=unit))
                    existing.add((name, unit))

            Ingredient.objects.bulk_create(new_ingredients)

        self.stdout.write(
            self.style.SUCCESS(
                f"Всего записей: {len(data)}, создано новых: {len(new_ingredients)}, пропущено: {skipped}"
            )
        )
