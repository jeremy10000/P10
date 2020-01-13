from decimal import *

from django.test import TestCase, Client, TransactionTestCase
from django.db import IntegrityError
from django.urls import reverse

from product.models import Category, Level, Product, Substitute
from login.models import User

from unittest.mock import patch
from django.core.management import call_command
from django.core.exceptions import ValidationError


class CmdTest(TransactionTestCase):
    """ Test all commands """

    def setUp(self):
        """ Config """

        data = Level(name="high")
        data.save()
        data = Level(name="moderate")
        data.save()
        data = Level(name="low")
        data.save()

        data = Category(name="Boissons")
        data.save()

        data = Product(
            name="Thé au jasmin",
            url="https://the-jasmin.fr",
            nutriscore="a",
            category_id=Category.objects.get(name="Boissons"),
            photo="https://the-jasmin.fr/photo.jpg",
            salt_100g=1.00,
            sugars_100g=2.10,
            fat_100g=3.78,
            saturate_fat_100g=11.22,
            level_salt=Level.objects.get(name="low"),
            level_sugars=Level.objects.get(name="low"),
            level_saturate_fat=Level.objects.get(name="high"),
            level_fat=Level.objects.get(name="high"),
            code="10012020",
            last_modified_t="1000"
        )
        data.save()

    @patch("product.management.commands.add-level.STDOUT", new_callable=bool)
    def test_add_level_errors(self, mock):
        """ TypeError """
        mock = False

        with self.assertRaises(TypeError):
            call_command("add-level", level=10)

        with self.assertRaises(TypeError):
            call_command("add-level")

    @patch("product.management.commands.add-level.STDOUT", new_callable=bool)
    def test_add_level_success_and_integrity_error(self, mock):
        """ integrity_error """
        mock = False

        self.assertEqual(Level.objects.all().count(), 3)

        call_command("add-level", level="Very Low")
        self.assertEqual(Level.objects.all().count(), 4)

        call_command("add-level", level="Very Low")
        self.assertEqual(Level.objects.all().count(), 4)

    @patch("product.management.commands.add-product.STDOUT", new_callable=bool)
    def test_add_product_errors(self, mock):
        """ TypeError """
        mock = False

        with self.assertRaises(TypeError):
            call_command("add-product", nutriscore="o")

        with self.assertRaises(TypeError):
            call_command("add-product", category=12)

    @patch("product.management.commands.add-product.requests.get")
    @patch("product.management.commands.add-product.STDOUT", new_callable=bool)
    def test_add_product_success_and_error(self, mock, mock_json):
        """ integrity error """
        mock = False

        mock_json.return_value.json.return_value = {
            'products': [{
                'nutrient_levels': {
                    'sugars': 'low',
                    'salt': 'low',
                    'fat': 'high',
                    'saturated-fat': 'moderate',
                },
                'nutriments': {
                    'salt_100g': '1.1',
                    'sugars_100g': '1.09',
                    'fat_100g': '22.15',
                    'saturated-fat_100g': '10.2',
                },
                'image_url': 'https://image.fr',
                'nutrition_grade_fr': ['a'],
                'url': 'https://url.fr',
                'code': '900800800',
                'last_modified_t': '10120130222',
                'product_name_fr': 'Nom du Produit Mock', },

                {
                'nutrient_levels': {
                    'sugars': 'low',
                    'salt': 'low',
                    'fat': 'high',
                    'saturated-fat': 'moderate',
                },
                'nutriments': {
                    'salt_100g': '1.1',
                    'sugars_100g': '1.09',
                    'fat_100g': '22.15',
                    'saturated-fat_100g': '10.2',
                },
                'image_url': 'https://image2.fr',
                'nutrition_grade_fr': ['a'],
                'url': 'https://url2.fr',
                'product_name_fr': 'Nom du Produit Mock 2',
                'code': '900900800',
                'last_modified_t': '1012013012',
            }]
        }

        self.assertEqual(Product.objects.all().count(), 1)
        self.assertEqual(Category.objects.all().count(), 1)
        call_command("add-product", nutriscore="a", category="Desserts")
        self.assertEqual(Product.objects.all().count(), 3)
        self.assertEqual(Category.objects.all().count(), 2)
        call_command("add-product", nutriscore="a", category="Desserts")
        self.assertEqual(Product.objects.all().count(), 3)
        self.assertEqual(Category.objects.all().count(), 2)

    @patch("product.management.commands.update-db.requests.get")
    @patch("product.management.commands.update-db.STDOUT", new_callable=bool)
    def test_update_sucess(self, mock_stdout, mock_json):
        """
            mock_stdout : Do not display messages during testing.
            mock_json : requests response

        """
        mock_stdout = False

        self.assertEqual(Product.objects.all().count(), 1)

        mock_json.return_value.json.return_value = {
            'product': {
                'nutrient_levels': {
                    'sugars': 'moderate',
                    'salt': 'moderate',
                    'fat': 'moderate',
                    'saturated-fat': 'moderate',
                },
                'nutriments': {
                    'salt_100g': 1.45,
                    'sugars_100g': 1.09,
                    'fat_100g': 22.15,
                    'saturated-fat_100g': 10.22,
                },
                'image_url': 'https://image.fr',
                'nutrition_grade_fr': ['b'],
                'url': 'https://url.fr',
                'code': '10012020',
                'last_modified_t': "1568887300",
                'product_name_fr': 'Thé Mock', }
        }
        mock = mock_json.return_value.json \
                        .return_value["product"]["last_modified_t"]

        product = Product.objects.get(code="10012020")
        self.assertEqual(product.name, "Thé au jasmin")
        self.assertEqual(product.last_modified_t, "1000")

        if product.last_modified_t < mock:
            update = True
        self.assertTrue(update)

        call_command("update-db")

        product = Product.objects.get(code="10012020")
        self.assertEqual(product.name, "Thé Mock")
        self.assertEqual(product.last_modified_t, "1568887300")
        self.assertEqual(product.salt_100g, Decimal('1.45'))
        self.assertEqual(product.sugars_100g, Decimal('1.09'))
        self.assertEqual(product.fat_100g, Decimal('22.15'))
        self.assertEqual(product.saturate_fat_100g, Decimal('10.22'))
        self.assertEqual(product.url, "https://url.fr")
        self.assertEqual(product.photo, "https://image.fr")

        self.assertEqual(product.level_sugars,
                         Level.objects.get(name="moderate"))
        self.assertEqual(product.level_salt,
                         Level.objects.get(name="moderate"))
        self.assertEqual(product.level_saturate_fat,
                         Level.objects.get(name="moderate"))
        self.assertEqual(product.level_fat,
                         Level.objects.get(name="moderate"))

        self.assertEqual(product.nutriscore, "b")

    @patch("product.management.commands.update-db.requests.get")
    @patch("product.management.commands.update-db.STDOUT", new_callable=bool)
    def test_update_error(self, mock_stdout, mock_json):
        """ Test: AttributeError and ValidationError """

        mock_stdout = False

        self.assertEqual(Product.objects.all().count(), 1)

        mock_json.return_value.json.side_effect = AttributeError("Error")

        product = Product.objects.get(code="10012020")
        self.assertEqual(product.name, "Thé au jasmin")
        self.assertEqual(product.last_modified_t, "1000")

        with self.assertRaises(AttributeError):
            call_command("update-db")

        product = Product.objects.get(code="10012020")
        self.assertEqual(product.name, "Thé au jasmin")
        self.assertEqual(product.last_modified_t, "1000")

        mock_json.return_value.json.side_effect = ValidationError("Error")

        with self.assertRaises(ValidationError):
            call_command("update-db")

        product = Product.objects.get(code="10012020")
        self.assertEqual(product.name, "Thé au jasmin")
        self.assertEqual(product.last_modified_t, "1000")
