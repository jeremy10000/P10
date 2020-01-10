from django.core.management.base import BaseCommand
from product.models import Product, Level

import requests


# Show messages
STDOUT = True


class Command(BaseCommand):
    """
    Update the products in the database.

    """
    help = 'Update data in the database.'

    def handle(self, *args, **options):
        """ usage : ./manage.py update-db """
        if STDOUT:
            self.stdout.write(self.style.SUCCESS(
                'Recherche des mises à jour...')
            )

        counter = 0

        for p in Product.objects.all():
            r = requests.get(
                "https://fr.openfoodfacts.org/api/v0/product/"
                "{}.json".format(p.code)).json()["product"]

            if int(p.last_modified_t) < int(r["last_modified_t"]):
                counter += 1

                n = r["nutriments"]
                nl = r["nutrient_levels"]

                p.name = r["product_name_fr"]
                p.url = r["url"]
                p.nutriscore = str(r['nutrition_grade_fr']) \
                 .replace("'", "") \
                 .replace("[", "") \
                 .replace("]", "")
                p.photo = r["image_url"]
                p.last_modified_t = r["last_modified_t"]

                p.salt_100g = n["salt_100g"]
                p.sugars_100g = n["sugars_100g"]
                p.fat_100g = n["fat_100g"]
                p.saturate_fat_100g = n["saturated-fat_100g"]

                p.level_salt = Level.objects.get(name=nl["salt"])
                p.level_sugars = Level.objects.get(name=nl["sugars"])
                p.level_saturate_fat = Level.objects.get(
                    name=nl["saturated-fat"])
                p.level_fat = Level.objects.get(name=nl["fat"])
                p.save()

                if STDOUT:
                    self.stdout.write(self.style.SUCCESS(
                        'Update : "Code: %s", "%s"' % (p.code, p.name))
                    )
        if STDOUT:
            self.stdout.write(self.style.SUCCESS(
                'Update(s) : %s.' % counter)
            )
