from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django import forms
from django.forms.widgets import PasswordInput, TextInput, EmailInput
from .models import User


class JoinForm(UserCreationForm):
    """ Registration """

    class Meta:
        model = User
        fields = (
            'email',
            'first_name',
            'last_name',
            'password1',
            'password2')

    email = forms.EmailField(
        label="Adresse mail",
        widget=EmailInput(attrs={'class': 'form-control'}),
        error_messages={
            'required': 'Il faut renseigner un email',
            'invalid': 'Cet email est invalid',
            'unique': 'Cet email existe déjà.'})

    password1 = forms.CharField(
        label="Mot de passe",
        widget=PasswordInput(attrs={'class': 'form-control'}))

    password2 = forms.CharField(
        label="Confirmation du mot de passe",
        widget=PasswordInput(attrs={'class': 'form-control'}))

    first_name = forms.CharField(
        required=False,
        label="Prénom (facultatif)",
        widget=TextInput(attrs={'class': 'form-control'}))

    last_name = forms.CharField(
        required=False,
        label="Nom (facultatif)",
        widget=TextInput(attrs={'class': 'form-control'}))


class LoginForm(AuthenticationForm):
    """ LoginView and CSS """

    # username = email
    username = forms.EmailField(
        label="Adresse mail",
        widget=EmailInput(attrs={'class': 'form-control'}))

    password = forms.CharField(
        label="Mot de passe",
        widget=PasswordInput(attrs={'class': 'form-control'}))
