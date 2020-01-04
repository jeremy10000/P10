from django.shortcuts import render
from django.views.generic import FormView
from django.contrib.auth import login, authenticate, logout
from .forms import JoinForm


class Join(FormView):
    """Show form and create user if valid."""

    form_class = JoinForm
    success_url = '/'
    template_name = 'registration/join.html'

    def form_valid(self, form):
        """ if form is valid """

        form.save()
        email = form.cleaned_data.get('email')
        _password = form.cleaned_data.get('password1')
        user = authenticate(email=email, password=_password)
        if user:
            login(self.request, user)
        return super().form_valid(form)


def mypage(request):
    """ Account profile """

    return render(request, "registration/mypage.html")
