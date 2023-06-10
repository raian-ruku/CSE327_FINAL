# forms.py
import base64
from datetime import timezone, datetime
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import MaintenanceRequest, Visit, WebUser, Apartment
from django.contrib.auth.forms import AuthenticationForm



class UserSignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    mobile_number = forms.CharField(max_length=15)
    email = forms.EmailField(max_length=254)
    owner_id = forms.CharField(max_length=30, required=False)
    owner_unique_id = forms.CharField(max_length=30, required=False)
    nid = forms.CharField(max_length=30, required=False)

    class Meta:
        model = WebUser
        fields = ['username', 'first_name', 'last_name', 'mobile_number', 'email', 'password1', 'password2', 'owner_id', 'owner_unique_id', 'nid']

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

class VisitForm(forms.ModelForm):

    def clean_visit_date(self):
        visit_date = self.cleaned_data.get('visit_date')
        
        # Check if the visit_date is in the past
        if visit_date and visit_date < timezone.now().date():
            raise forms.ValidationError("Invalid visit date. Please select a future date.")
    class Meta:
        model = Visit
        fields = ['name', 'mobile_number', 'email', 'nid_number', 'visit_date', 'visit_time']
        widgets = {
            'visit_date': forms.DateInput(attrs={'type': 'date'}),
            'visit_time': forms.TimeInput(attrs={'type': 'time'}),
        }

class FileSubmissionForm(forms.ModelForm):
    class Meta:
        model = WebUser
        fields = ['files']