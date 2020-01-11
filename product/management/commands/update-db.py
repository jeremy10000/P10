from django.core.management.base import BaseCommand
from django.core.exceptions import ValidationError
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
                'Check for updates...')
            )

        self.counter = 0

        for p in Product.objects.all():
            try:
                r = requests.get(
                    "https://fr.openfoodfacts.org/api/v0/product/"
                    "{}.json".format(p.code), timeout=5.0, verify=False).json()["product"]

                self.check_update(r, p)

            except requests.exceptions.RequestException as e:
                if STDOUT:
                    self.stdout.write(self.style.SUCCESS(
                        'Exception : "%s", %s' % (p.code, e))
                    )

        if STDOUT:
            self.stdout.write(self.style.SUCCESS(
                'Update(s) : %s.' % counter)
            )

    def check_update(self, r, p):
        """
        Args:
            r : requests response
            p : product
            counter : self.counter
        """
        if int(p.last_modified_t) < int(r.get("last_modified_t", 0)):
            try:
                n = r.get("nutriments")
                nl = r.get("nutrient_levels")

                p.name = r.get("product_name_fr", "")
                p.url = r.get("url", "")
                p.nutriscore = str(r.get("nutrition_grade_fr", "")) \
                 .replace("'", "") \
                 .replace("[", "") \
                 .replace("]", "")
                p.photo = r.get("image_url", "")
                p.last_modified_t = r.get("last_modified_t", "")

                p.salt_100g = n.get("salt_100g", "")
                p.sugars_100g = n.get("sugars_100g", "")
                p.fat_100g = n.get("fat_100g", "")
                p.saturate_fat_100g = n.get("saturated-fat_100g", "")

                p.level_salt = Level.objects.get(name=nl.get("salt", ""))

                p.level_sugars = Level \
                 .objects.get(name=nl.get("sugars", ""))

                p.level_saturate_fat = Level.objects.get(
                    name=nl.get("saturated-fat", ""))
                p.level_fat = Level.objects.get(name=nl.get("fat", ""))
                p.save()

                if STDOUT:
                    self.stdout.write(self.style.SUCCESS(
                        'Update : "Code : %s"' % p.code)
                    )
                self.counter += 1

            except KeyError:
                pass

            except ValidationError:
                pass
