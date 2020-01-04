from django.contrib import admin
from .models import Category, Product, Substitute, Level


class SubstituteAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'product_id', 'substitute_id')


class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'category_id', 'nutriscore', 'url', 'photo',
        'fat_100g', 'sugars_100g', 'salt_100g', 'saturate_fat_100g',
        'level_salt', 'level_sugars', 'level_saturate_fat', 'level_fat')


admin.site.register(Category)
admin.site.register(Level)
admin.site.register(Product, ProductAdmin)
admin.site.register(Substitute, SubstituteAdmin)
