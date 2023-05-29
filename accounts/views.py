from django.shortcuts import render, redirect
from django.views.generic import TemplateView, CreateView, ListView
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from .models import Apartment, Tenant, MaintenanceRequest
from django.contrib.auth.views import LoginView
from django.contrib.auth import login
from .forms import UserSignUpForm
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Apartment
from .forms import VacancyPostingForm
from .models import WebUser
from django.shortcuts import redirect
from django.contrib.auth.forms import AuthenticationForm
from .forms import WebUserLoginForm
from django.urls import reverse

from django.contrib.auth import logout
from django.views.generic import DetailView
from django.views import View


class HomePageView(LoginRequiredMixin, ListView):
    model = Apartment
    template_name = 'accounts/home.html'
    context_object_name = 'accounts'

    def get_queryset(self):
        return Apartment.objects.filter(is_vacant=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            web_user = WebUser.objects.get(username=self.request.user.username)
            context['first_name'] = web_user.first_name
        return context
    
class SignUpView(CreateView):
    form_class = UserSignUpForm
    success_url = reverse_lazy('login')
    template_name = 'accounts/signup.html'

    def form_valid(self, form):
        web_user = form.save(commit=False)
        web_user.username = form.cleaned_data['username']
        web_user.email = form.cleaned_data['email']
        web_user.first_name = form.cleaned_data['first_name']
        web_user.last_name = form.cleaned_data['last_name']
        web_user.mobile_number = form.cleaned_data['mobile_number']
        web_user.user_type = form.cleaned_data['user_type']
        # Set other fields accordingly

        web_user.save()
        return super().form_valid(form)
    
class WebUserLoginForm(AuthenticationForm):
    class Meta:
        model = WebUser
        fields = ('username', 'password')

class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        web_user = WebUser.objects.get(user=user)
        context['web_user'] = web_user
        return context

class SignInView(LoginView):
    template_name = 'accounts/login.html'
    authentication_form = WebUserLoginForm

    def get_success_url(self):
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url  # Redirect to the URL specified in the 'next' parameter

        username = self.request.POST.get('username')  # Get the username entered in the sign-in form

        try:
            web_user = WebUser.objects.get(username=username)
        except WebUser.DoesNotExist:
            return reverse('home')  # Replace 'home' with the actual URL name for the default landing page

        return reverse('profile')  # Replace 'profile' with the actual URL name for the profile page

class OwnerDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/owner_dashboard.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.user_type == 'owner':
            return super().get(request, *args, **kwargs)
        else:
            return redirect('owner_dashboard') # Redirect to the signin page or any other appropriate URL

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['accounts'] = Apartment.objects.filter(owner=self.request.user)
        return context

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['accounts'] = Apartment.objects.filter(owner=self.request.user)
        return context
class ApartmentDetailsView(DetailView):
    model = Apartment
    template_name = 'accounts/apartment_details.html'
    context_object_name = 'apartment'
def posted_vacancies(request):
    owner = request.user
    vacancies = Apartment.objects.filter(owner=owner)
    return render(request, 'accounts/posted_vacancies.html', {'vacancies': vacancies})

class VacancyPostingView(LoginRequiredMixin, CreateView):
    form_class = VacancyPostingForm
    template_name = 'accounts/vacancy_posting.html'
    success_url = '/owner/dashboard/'  # Update with the appropriate URL

    def form_valid(self, form):
        apartment = form.save(commit=False)
        apartment.owner = self.request.user

        

        apartment.save()
        form.save_m2m()
        return super().form_valid(form)
    
class TenantDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/tenant_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['maintenance_requests'] = MaintenanceRequest.objects.filter(tenant__user=self.request.user)
        # Add any other data you want to pass to the template
        return context

class MaintenanceRequestView(LoginRequiredMixin, CreateView):
    model = MaintenanceRequest
    fields = ['subject', 'description']
    template_name = 'accounts/maintenance_request.html'
    success_url = reverse_lazy('tenant_dashboard')

    def form_valid(self, form):
        tenant = Tenant.objects.get(user=self.request.user)
        form.instance.tenant = tenant
        return super().form_valid(form)
def TenantDetailView(request):
    owner_unique_id = request.user.owner_unique_id
    tenant = WebUser.objects.get(owner_unique_id=owner_unique_id).tenant
    context = {'tenant': tenant}
    return render(request, 'accounts/tenant_detail.html', context)

def logout_view(request):
    logout(request)
    return redirect(reverse('home'))
@login_required
def send_notification(request):
    # Handle notification sending logic here
    pass

@login_required
def chat(request):
    # Handle chat functionality here
    pass


@login_required
def profile(request):
    web_user = request.user

    username = web_user.username
    email = web_user.email
    first_name = web_user.first_name
    last_name = web_user.last_name
    mobile_number = web_user.mobile_number
    user_type = web_user.user_type

    # Retrieve the owner information
    owner = WebUser.objects.filter(owner_unique_id=web_user.owner_id).first()

    context = {
        'username': username,
        'email': email,
        'first_name': first_name,
        'last_name': last_name,
        'mobile_number': mobile_number,
        'user_type': user_type,
        'owner': owner,  # Pass the owner information to the template
    }

    return render(request, 'accounts/profile.html', context)





# Add any other views you require
