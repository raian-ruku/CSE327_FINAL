# forms.py
import base64
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import MaintenanceRequest, WebUser, Apartment
from django.contrib.auth.forms import AuthenticationForm

USER_TYPE_CHOICES = [
    ('', 'Select User Type'),
    ('owner', 'Owner'),
    ('tenant', 'Tenant'),
    ('renter', 'Renter'),
]

class UserSignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    mobile_number = forms.CharField(max_length=15)
    email = forms.EmailField(max_length=254)
    user_type = forms.ChoiceField(choices=USER_TYPE_CHOICES)
    owner_unique_id = forms.CharField(max_length=30, required=False)
    owner_id = forms.CharField(max_length=30, required=False)
    nid = forms.CharField(max_length=30, required=False)
    username = forms.CharField(max_length=150)

    class Meta:
        model = WebUser
        fields = ['username','first_name', 'last_name', 'mobile_number', 'email', 'password1', 'password2', 'user_type', 'owner_unique_id', 'owner_id', 'nid']


class VacancyPostingForm(forms.ModelForm):
    class Meta:
        model = Apartment
        fields = ['address', 'rent', 'area', 'bedrooms', 'washrooms', 'description', 'short_description']

   
       
class WebUserLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'autofocus': True}))
    password = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'current-password'}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Email or Username'

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            if '@' in username:
                # If the username contains '@', assume it's an email address
                self.user_cache = WebUser.objects.filter(email=username).first()
            else:
                # Otherwise, assume it's a username
                self.user_cache = WebUser.objects.filter(username=username).first()

            if self.user_cache is None or not self.user_cache.check_password(password):
                raise forms.ValidationError('Invalid email/username or password.')
        return self.cleaned_data 
    


class MaintenanceRequestForm(forms.ModelForm):
    class Meta:
        model = MaintenanceRequest
        fields = ['subject', 'message']
