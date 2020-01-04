from django.urls import path
from . import views


"""
    for templates
    product:<name>

"""
app_name = 'product'

urlpatterns = [
    path('search/', views.Search.as_view(), name="search"),
    path(
        'proposition/<int:product_id>',
        views.Proposition.as_view(),
        name="proposition"),

    path('detail/<int:pk>', views.Detail.as_view(), name="detail"),
    path('save/', views.save_view, name="save"),
    path('favorites/', views.Favorites.as_view(), name="favorites"),
    path('delete/<int:pk>', views.DeleteView.as_view(), name="delete"),
]
