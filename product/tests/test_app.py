from django.test import TestCase, Client, TransactionTestCase
from django.db import IntegrityError
from django.urls import reverse

from .models import Category, Level, Product, Substitute
from login.models import User

from unittest.mock import patch
from django.core.management import call_command


def db_init():
    """ setUp Test """
    user = User.objects.create(email='marie@fixture.fr')
    user.set_password('@unMotdePasse')
    user.save()

    data = Category(name="Sauce")
    data.save()

    data = Level(name="High")
    data.save()

    data = Product(
        name="Mayonnaise",
        url="https://mayo.fr",
        nutriscore="c",
        category_id=Category.objects.get(name="Sauce"),
        photo="https://mayo.fr/photo.jpg",
        salt_100g="1.00",
        sugars_100g="2.00",
        fat_100g="3.00",
        saturate_fat_100g="4.00",
        level_salt=Level.objects.get(name="High"),
        level_sugars=Level.objects.get(name="High"),
        level_saturate_fat=Level.objects.get(name="High"),
        level_fat=Level.objects.get(name="High"),
        code="100200300",
        last_modified_t="1568887200"
    )
    data.save()

    data = Product(
        name="Sauce tomate",
        url="https://Sauce-tomate.fr",
        nutriscore="b",
        category_id=Category.objects.get(name="Sauce"),
        photo="https://Sauce-tomate.fr/photo.jpg",
        salt_100g="1.00",
        sugars_100g="2.00",
        fat_100g="3.00",
        saturate_fat_100g="4.00",
        level_salt=Level.objects.get(name="High"),
        level_sugars=Level.objects.get(name="High"),
        level_saturate_fat=Level.objects.get(name="High"),
        level_fat=Level.objects.get(name="High"),
        code="101201301",
        last_modified_t="10120130111"
    )
    data.save()

    data = Product(
        name="Ketchup",
        url="https://Ketchup.fr",
        nutriscore="c",
        category_id=Category.objects.get(name="Sauce"),
        photo="https://Ketchup.fr/photo.jpg",
        salt_100g="1.00",
        sugars_100g="2.00",
        fat_100g="3.00",
        saturate_fat_100g="4.00",
        level_salt=Level.objects.get(name="High"),
        level_sugars=Level.objects.get(name="High"),
        level_saturate_fat=Level.objects.get(name="High"),
        level_fat=Level.objects.get(name="High"),
        code="102202302",
        last_modified_t="1768894400"
    )
    data.save()


class ProductTest(TestCase):
    """ Test Product App """

    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.search_url = reverse('product:search')
        cls.save_url = reverse('product:save')
        cls.favorites_url = reverse('product:favorites')
        db_init()

    """
        SearchView
    """

    def test_search_url_and_template(self):
        response = self.client.get(self.search_url + "?query=TEST")
        self.assertTemplateUsed(response, 'product/search.html')
        self.assertEqual(response.status_code, 200)

    def test_search_url_404(self):
        response = self.client.get(self.search_url + "?query=Mayo&page=@")
        self.assertEqual(response.status_code, 404)

    def test_search_no_query(self):
        response = self.client.get(self.search_url)
        self.assertRedirects(
            response, '/', status_code=302, target_status_code=200)

    def test_search_context_search(self):
        response = self.client.get(self.search_url + "?query=Beurre")
        self.assertEqual(response.context_data["search"], "Beurre")

    def test_search_product_found(self):
        response = self.client.get(self.search_url + "?query=mayo")
        self.assertEqual(response.context_data["object_list"].count(), 1)

    def test_search_zero_product(self):
        response = self.client.get(self.search_url + "?query=moutarde")
        self.assertEqual(response.context_data["object_list"].count(), 0)

    """
    View : Proposition

    """
    def test_proposition_url_and_template(self):
        response = self.client.get('/product/proposition/1')
        self.assertTemplateUsed(response, 'product/proposition.html')
        self.assertEqual(response.status_code, 200)

    def test_proposition_better_nutriscore_or_equivalent_and_exclude_id(self):
        r = self.client.get('/product/proposition/1')

        self.assertEqual(r.context_data["object_list"].count(), 2)
        self.assertEqual(r.status_code, 200)

        # id=1 because self.client.get('/product/proposition/1')
        if not Product.objects.get(id=1) in r.context_data["object_list"]:
            exclude_id = True

        self.assertTrue(exclude_id)

    def test_proposition_no_products(self):
        response = self.client.get('/product/proposition/2')

        self.assertEqual(response.context_data["object_list"].count(), 0)
        self.assertEqual(response.status_code, 200)

    def test_proposition_unknown_id(self):
        response = self.client.get('/product/proposition/90')
        self.assertRedirects(
            response, '/', status_code=302, target_status_code=200)

    def test_proposition_context_data(self):
        response = self.client.get('/product/proposition/1')
        self.assertEqual(response.status_code, 200)

        # id=1 because self.client.get('/product/proposition/1')
        product = Product.objects.get(id=1)

        self.assertEqual(response.context_data["search"], product.name)
        self.assertEqual(response.context_data["product"], product.id)
        self.assertEqual(response.context_data["photo"], product.photo)

    """
    View : Detail

    """
    def test_detail_url_template_and_valid_id(self):
        response = self.client.get('/product/detail/1')
        self.assertTemplateUsed(response, 'product/detail.html')
        self.assertEqual(response.status_code, 200)

    def test_detail_invalid_id(self):
        response = self.client.get('/product/detail/90')
        self.assertEqual(response.status_code, 404)

    """
        SaveView

    """
    def test_save_valid_post_if_not_logged(self):
        user_id = User.objects.get(email='marie@fixture.fr').id
        response = self.client.post(
            self.save_url, {
                'product_id': Product.objects.get(id=1).id,
                'substitute_id': Product.objects.get(id=2).id,
                'user_id': user_id,
                'next': '/',
            }
        )
        self.assertRedirects(
            response, '/login?next=/product/save/',
            status_code=302, target_status_code=301)

    def test_save_success_and_error_if_logged(self):
        self.client.login(
            username='marie@fixture.fr',
            password='@unMotdePasse')

        user_id = User.objects.get(email='marie@fixture.fr').id

        self.assertEqual(Substitute.objects.all().count(), 0)

        response = self.client.post(
            self.save_url, {
                'product_id': Product.objects.get(id=1).id,
                'substitute_id': Product.objects.get(id=2).id,
                'user_id': user_id,
                'next': '/',
            }
        )

        self.assertEqual(Substitute.objects.all().count(), 1)
        self.assertRedirects(
            response, '/product/favorites/',
            status_code=302, target_status_code=200)

        response = self.client.post(
            self.save_url, {
                'product_id': Product.objects.get(id=1).id,
                'substitute_id': Product.objects.get(id=2).id,
                'user_id': user_id,
                'next': '/',
            }, follow=True
        )

        self.assertEqual(Substitute.objects.all().count(), 1)

        self.assertRedirects(
            response, '/', status_code=302, target_status_code=200)

        message = list(response.context.get('messages'))[0]
        self.assertEqual(message.tags, "info")
        self.assertTrue(message.message, "Le produit est déja enregistré !")

    def test_save_invalid_post(self):
        user_id = User.objects.get(email='marie@fixture.fr').id
        with self.assertRaises(Product.DoesNotExist):
            response = self.client.post(
                self.save_url, {
                    'product_id': Product.objects.get(id=10).id,
                    'substitute_id': Product.objects.get(id=2).id,
                    'user_id': user_id,
                }
            )

    """
        Favorites

    """
    def test_favorites_redirect_if_not_logged(self):
        response = self.client.get(self.favorites_url)
        self.assertRedirects(
            response, '/login?next=/product/favorites/',
            status_code=302, target_status_code=301)

    def test_favorites_if_logged_and_zero_product(self):
        self.client.login(
            username='marie@fixture.fr',
            password='@unMotdePasse')

        response = self.client.get(self.favorites_url)

        self.assertTemplateUsed(response, 'product/favorites.html')
        self.assertEqual(response.context_data["object_list"].count(), 0)
        self.assertEqual(response.status_code, 200)

    def test_favorites_if_logged_and_one_product(self):
        self.client.login(
            username='marie@fixture.fr',
            password='@unMotdePasse')

        user_id = User.objects.get(email='marie@fixture.fr').id

        response = self.client.get(self.favorites_url)
        self.assertEqual(response.context_data["object_list"].count(), 0)

        response = self.client.post(
            self.save_url, {
                'product_id': Product.objects.get(id=1).id,
                'substitute_id': Product.objects.get(id=2).id,
                'user_id': user_id,
                'next': '/',
            }
        )

        response = self.client.get(self.favorites_url)
        self.assertEqual(response.context_data["object_list"].count(), 1)
        self.assertEqual(response.status_code, 200)

    """
        DeleteView

    """
    def test_delete_if_not_logged(self):
        response = self.client.post("/product/delete/1000")
        self.assertRedirects(
            response, '/login?next=/product/delete/1000',
            status_code=302, target_status_code=301)

    def test_delete_if_logged_and_unknown_id(self):
        self.client.login(
            username='marie@fixture.fr',
            password='@unMotdePasse')

        response = self.client.post("/product/delete/1000")
        self.assertEqual(response.status_code, 404)

    def test_delete_success(self):
        self.client.login(
            username='marie@fixture.fr',
            password='@unMotdePasse')

        user_id = User.objects.get(email='marie@fixture.fr').id

        response = self.client.get(self.favorites_url)
        self.assertEqual(response.context_data["object_list"].count(), 0)

        response = self.client.post(
            self.save_url, {
                'product_id': Product.objects.get(id=1).id,
                'substitute_id': Product.objects.get(id=2).id,
                'user_id': user_id,
                'next': '/',
            }
        )

        response = self.client.get(self.favorites_url)
        self.assertEqual(response.context_data["object_list"].count(), 1)
        self.assertEqual(response.status_code, 200)

        response = self.client.post("/product/delete/1")
        self.assertEqual(response.status_code, 302)

        response = self.client.get(self.favorites_url)
        self.assertEqual(response.context_data["object_list"].count(), 0)
