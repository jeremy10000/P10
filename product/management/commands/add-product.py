from django.core.management.base import BaseCommand, CommandError
from product.models import Category, Product, Level
from django.db import IntegrityError

import requests


NUTRISCORE_FR = ["a", "b", "c", "d", "e"]
# Show messages
STDOUT = True


class Command(BaseCommand):
    """
        usage : add-product -n <nutriscore> -c <category>
        ex : add-product -n "a" -c "Produits de la mer"

    """
    help = 'Insert data in the database.'

    def add_arguments(self, parser):
        """ new argument """
        parser.add_argument("-n", "--nutriscore", type=str)
        parser.add_argument("-c", "--category", type=str)

    def handle(self, *args, **options):
        """ Insert category and products in the database """

        if not isinstance(options["category"], str):
            raise TypeError("Entrez une chaine de caractère.")

        if options["nutriscore"] not in NUTRISCORE_FR:
            raise TypeError("Entrez un nutriscore correct.")

        if options["category"] and options["nutriscore"]:
            self.category = options["category"]
            self.nutriscore = options["nutriscore"]

            self.insert_category_in_db()

            request_openfoodfacts = self.my_request()

        else:
            raise ValueError("Usage : add-product -c \"Desserts\" -n \"a\"")

    def insert_category_in_db(self):
        """ Insert category """

        try:
            data = Category(name=self.category)
            data.save()
            if STDOUT:
                self.stdout.write(self.style.SUCCESS(
                    'Category : "%s", Insertion OK' % self.category)
                )
        except IntegrityError:
            if STDOUT:
                self.stdout.write(self.style.WARNING(
                    'Category : "%s", Insertion FAIL (IntegrityError)'
                    % self.category))

    def my_request(self):
        """ Request Openfoodfacts """
        if STDOUT:
            self.stdout.write(self.style.SQL_TABLE(
                'Product request for : "%s" [ Nutriscore %s ]'
                % (self.category, self.nutriscore)))

        product_request = requests.get(
            "https://fr.openfoodfacts.org/cgi/search.pl?"
            "search_terms={}&search_tag=categories"
            "&sort_by=unique_scans_n&nutrition_grades={}"
            "&page_size=40&json=1".format(self.category, self.nutriscore))

        results = product_request.json()["products"]

        self.keep_data(results)

    def keep_data(self, data):
        """ Data required """

        for product in data:
            self.required = {}
            self.save_db = True

            level = product.get("nutrient_levels")
            nutriments = product.get("nutriments")

            self.required["product_name"] = product.get("product_name_fr", "")
            self.required["url"] = product.get("url", "")
            self.required["nutrition_grade"] = str(product.get(
                'nutrition_grade_fr', "")) \
                .replace("'", "") \
                .replace("[", "") \
                .replace("]", "")
            self.required["image_url"] = product.get("image_url", "")

            self.required["salt_100g"] = nutriments.get("salt_100g", "")
            self.required["sugars_100g"] = nutriments.get("sugars_100g", "")
            self.required["fat_100g"] = nutriments.get("fat_100g", "")
            self.required["saturated_fat_100g"] = nutriments.get(
                "saturated-fat_100g", "")

            self.required["level_sugars"] = level.get("sugars", "")
            self.required["level_salt"] = level.get("salt", "")
            self.required["level_saturated"] = level.get("saturated-fat", "")
            self.required["level_fat"] = level.get("fat", "")

            self.required["code"] = product.get("code", "")
            self.required["last_modified_t"] = product \
                .get("last_modified_t", "")

            self.check_data(self.required)

    def check_data(self, product):
        """ Check data """

        for key, value in product.items():
            try:
                if value == "":
                    self.save_db = False
                    raise KeyError("KeyError")

            except KeyError:
                if STDOUT:
                    self.stdout.write(self.style.WARNING(
                        'A Product has not been registered : KeyError "%s"'
                        % key))
                break

        if self.save_db is True:
            self.save_product(product)

    def save_product(self, product):
        """ Save product """
        try:
            data = Product(
                name=product["product_name"],
                url=product["url"],
                nutriscore=product["nutrition_grade"],
                category_id=Category.objects.get(name=self.category),
                photo=product["image_url"],
                salt_100g=product["salt_100g"],
                sugars_100g=product["sugars_100g"],
                fat_100g=product["fat_100g"],
                saturate_fat_100g=product["saturated_fat_100g"],
                level_salt=Level.objects.get(name=product["level_salt"]),
                level_sugars=Level.objects.get(name=product["level_sugars"]),
                level_saturate_fat=Level.objects.get(
                    name=product["level_saturated"]),
                level_fat=Level.objects.get(name=product["level_fat"]),
                code=product["code"],
                last_modified_t=product["last_modified_t"],
            )
            data.save()
            if STDOUT:
                self.stdout.write(self.style.SUCCESS(
                    'Product saved : "%s"' % product["product_name"])
                )

        except IntegrityError:
            if STDOUT:
                self.stdout.write(self.style.WARNING(
                    'WARNING : "%s", IntegrityError' % product["product_name"])
                )
