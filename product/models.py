from django.db import models
from purbeurre.settings import AUTH_USER_MODEL


class Level(models.Model):
    """ Level [sugar, fat, salt] (low, high, moderate) """

    name = models.CharField(
        max_length=8,
        unique=True,
        verbose_name="Level"
    )

    class Meta:
        verbose_name = "Level"

    def __str__(self):
        return self.name


class Category(models.Model):
    """ Product Categories """

    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Nom"
    )

    class Meta:
        verbose_name = "Catégorie"

    def __str__(self):
        return self.name


class Product(models.Model):
    """ Product """

    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Nom du produit"
    )
    category_id = models.ForeignKey(
        Category,
        related_name='category',
        verbose_name="Catégorie ID",
        on_delete=models.CASCADE
    )

    nutriscore = models.CharField(max_length=1, verbose_name="Nutriscore")
    url = models.URLField(verbose_name="URL")
    photo = models.URLField(verbose_name="Photo")

    fat_100g = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        null=True
    )
    sugars_100g = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        null=True
    )
    salt_100g = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        null=True
    )
    saturate_fat_100g = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        null=True
    )

    level_salt = models.ForeignKey(
        Level,
        related_name='levelSalt',
        on_delete=models.CASCADE
    )
    level_sugars = models.ForeignKey(
        Level,
        related_name='levelSugars',
        on_delete=models.CASCADE
    )
    level_saturate_fat = models.ForeignKey(
        Level,
        related_name='levelSaturateFat',
        on_delete=models.CASCADE
    )
    level_fat = models.ForeignKey(
        Level,
        related_name='levelFat',
        on_delete=models.CASCADE
    )

    code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Code produit"
    )
    last_modified_t = models.CharField(
        max_length=50,
        verbose_name="Dernière modification"
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Produit"


class Substitute(models.Model):
    """ Favorites """

    product_id = models.ForeignKey(
        Product,
        related_name='product',
        on_delete=models.CASCADE
    )
    substitute_id = models.ForeignKey(
        Product,
        related_name='substitute',
        on_delete=models.CASCADE
    )

    user_id = models.ForeignKey(
        AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['product_id', 'substitute_id', 'user_id'],
                name='unique_relation')
        ]
        verbose_name = "Favoris"
        verbose_name_plural = "Favoris"
