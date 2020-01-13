from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView
from django.views.generic.edit import DeleteView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy

from login.models import User
from .models import Product, Substitute

from sentry_sdk import push_scope, capture_exception, capture_message


class Search(ListView):
    """ Search for Products. """

    template_name = 'product/search.html'
    paginate_by = 6

    def get(self, request, *args, **kwargs):
        """ No Server Error """
        query = self.request.GET.get("query")
        if query:
            return super(Search, self).get(request, *args, **kwargs)
        else:
            return redirect('index')

    def get_queryset(self):
        query = self.request.GET.get("query")

        product = Product.objects.filter(
            name__icontains=query).order_by('name')

        if not product:
            with push_scope() as scope:
                scope.set_tag("info", "search")
                scope.level = 'info'
                capture_message("No products.")

        return product

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get("query")
        return context


class Proposition(ListView):
    """ product proposal """

    template_name = 'product/proposition.html'
    paginate_by = 6

    def get(self, request, *args, **kwargs):
        try:
            product = Product.objects.get(pk=self.kwargs['product_id'])
            return super(Proposition, self).get(request, *args, **kwargs)
        except Product.DoesNotExist as e:
            with push_scope() as scope:
                scope.set_tag("exception", "proposition")
                scope.level = 'error'
                capture_exception(Exception(e))
            return redirect('index')

    def get_queryset(self):
        """ Products of the same category. """

        self._id = self.kwargs['product_id']
        self.product = Product.objects.get(pk=self._id)
        return Product.objects.filter(
            category_id=self.product.category_id).filter(
            nutriscore__lte=self.product.nutriscore).exclude(
            id=self._id).order_by('nutriscore')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.product.name
        context['product'] = self.product.id
        context['photo'] = self.product.photo
        return context


class Detail(DetailView):
    """ Details of the Products. """
    model = Product
    template_name = "product/detail.html"


@login_required
def save_view(request):
    """ Save Products. """

    if request.method == 'POST':

        product = request.POST['product_id']
        substitute = request.POST['substitute_id']
        page = request.POST['next']

        user_product = Product.objects.get(pk=product)
        user_substitute = Product.objects.get(pk=substitute)
        _user = User.objects.get(pk=request.user.pk)

        if user_product and user_substitute and _user:
            obj, created = Substitute.objects.get_or_create(
                product_id=user_product,
                substitute_id=user_substitute,
                user_id=_user,
            )

            if created:
                return redirect('product:favorites')
            else:
                messages.add_message(
                    request,
                    messages.INFO,
                    'Le produit est déja enregistré !'
                )
                return redirect(page)

    return redirect('index')


class Favorites(LoginRequiredMixin, ListView):
    """ User's products """

    template_name = 'product/favorites.html'
    paginate_by = 6

    def get_queryset(self):
        return Substitute.objects.filter(
            user_id=self.request.user.id).order_by("product_id")


class DeleteView(LoginRequiredMixin, DeleteView):
    """ Delete User Products """
    model = Substitute
    success_url = reverse_lazy('product:favorites')
