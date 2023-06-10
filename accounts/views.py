from django.http import HttpResponse, HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, CreateView, ListView
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from .models import Apartment, Tenant, MaintenanceRequest, Chat, Message
from django.contrib.auth.views import LoginView
from django.contrib.auth import login
from .forms import FileSubmissionForm, MaintenanceRequestForm, UserSignUpForm, VisitForm
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Apartment
from .forms import VacancyPostingForm
from .models import WebUser
from django.shortcuts import redirect
from django.contrib.auth.forms import AuthenticationForm
from .forms import WebUserLoginForm
from django.urls import reverse
from notifications.signals import notify
from notifications.models import Notification
from sweetify import sweetify

 
from django.contrib.auth import logout
from django.views.generic import DetailView
from django.views import View


class HomePageView(ListView):
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

    def form_valid(self, form):
        apartment = form.save(commit=False)
        apartment.owner = WebUser.objects.get(username=self.request.user.username)
        apartment.save()
        return HttpResponseRedirect(reverse('profile'))

    def get_success_url(self):
        return reverse('profile')
    

@login_required
def make_request(request):
    if request.method == 'POST':
        form = MaintenanceRequestForm(request.POST)
        if form.is_valid():
            maintenance_request = form.save(commit=False)
            maintenance_request.tenant = request.user

            # Get the owner of the tenant
            try:
                owner = WebUser.objects.get(owner_unique_id=maintenance_request.tenant.owner_id)
                maintenance_request.owner = owner
            except WebUser.DoesNotExist:
                # Handle the case when the owner doesn't exist
                # You can raise an exception, redirect to an error page, or take any other appropriate action
                pass

            maintenance_request.save()
            return redirect('profile')
    else:
        form = MaintenanceRequestForm()

    context = {
        'form': form,
    }
    return render(request, 'accounts/make_request.html', context)



@login_required
def owner_requests(request):
    owner = request.user
    owner_requests = MaintenanceRequest.objects.filter(owner=owner).order_by('-created_at')

    context = {
        'owner_requests': owner_requests,
    }
    return render(request, 'accounts/owner_requests.html', context)

@login_required
def pending_requests(request):
    tenant = request.user
    pending_requests = MaintenanceRequest.objects.filter(tenant=tenant).order_by('-created_at')

    context = {
        'pending_requests': pending_requests,
    }
    return render(request, 'accounts/pending_requests.html', context)

def approve_request(request, request_id):
    maintenance_request = get_object_or_404(MaintenanceRequest, pk=request_id)
    maintenance_request.status = 'approved'
    maintenance_request.save()
    
    return redirect('owner_requests')

@login_required
def reject_request(request, request_id):
    if request.method == 'POST':
        rejection_reason = request.POST.get('rejection_reason')
        try:
            maintenance_request = MaintenanceRequest.objects.get(pk=request_id)
            maintenance_request.status = 'rejected'
            maintenance_request.rejection_reason = rejection_reason
            maintenance_request.save()
            return redirect('owner_requests')
        except MaintenanceRequest.DoesNotExist:
            # Handle the case when the request does not exist
            # You can raise an exception, redirect to an error page, or take any other appropriate action
            pass
    return redirect('owner_requests')
    
def tenants_list(request):
    owner = WebUser.objects.get(username=request.user.username, user_type='owner')
    tenants = WebUser.objects.filter(owner_id=owner.owner_unique_id)

    context = {
        'tenants': tenants,
    }

    return render(request, 'accounts/tenants_list.html', context)

def apartment_list(request):
    owner = WebUser.objects.get(username=request.user.username)
    posted_apartment = Apartment.objects.filter(owner=owner.username)

    context = {
        'posted_apartment' : posted_apartment,
        }
    
    return render(request, 'accounts/profile.html')

def apartment_edit(request, apartment_id):
    apartment = get_object_or_404(Apartment, id=apartment_id)
    
    if request.method == 'POST':
        # Handle the form submission to update the apartment
        # Retrieve the updated data from the form and save it to the apartment object
        # Example:
        apartment.address = request.POST['address']
        apartment.bedrooms = request.POST['bedrooms']
        apartment.washrooms = request.POST['washrooms']
        apartment.rent = request.POST['rent']
        apartment.short_description = request.POST['description']
        apartment.save()
        
        return redirect('apartment_details', apartment_id=apartment_id)
    
    context = {
        'apartment': apartment
    }
    
    return render(request, 'accounts/apartment_edit.html', context)
@login_required
def owner_info(request):
    tenant = WebUser.objects.get(username=request.user.username, user_type='tenant')
    owner = WebUser.objects.get(owner_unique_id=tenant.owner_id, user_type='owner')

    context = {
        'owner': owner,
    }

    return render(request, 'accounts/owner_info.html', context)

@login_required
def tenant_details(request, username):
    tenant = get_object_or_404(WebUser, username=username)

    context = {
        'tenant': tenant,
    }

    return render(request, 'accounts/tenant_details.html', context)

def chat(request, chat_id):
    chat = Chat.objects.get(id=chat_id)
    messages = Message.objects.filter(chat=chat).order_by('timestamp')

    context = {
        'chat': chat,
        'messages': messages,
    }

    return render(request, 'accounts/chat.html', context)


@login_required
def start_chat(request, username):
    owner = request.user
    tenant = get_object_or_404(WebUser, username=username)

    # Check if the current user is the owner
    if owner.user_type == 'owner':
        # Create a chat between the owner and tenant
        chat = Chat.objects.create(owner=owner, tenant=tenant)
        return redirect('chat', chat_id=chat.id)

    return HttpResponseForbidden("You are not authorized to start a chat.")


@login_required
def apartment_delete(request, pk):
    apartment = get_object_or_404(Apartment, pk=pk)

    # Check if the logged-in user is the owner of the apartment
    if request.user == apartment.owner:
        # Delete the apartment
        apartment.delete()
        # Redirect to a success page or any other desired page
        return redirect('profile')
    else:
        # Handle unauthorized access or show an error message
        return redirect('apartment_details', pk=pk) 

def logout_view(request):
    logout(request)
    return redirect('home')


def plan_visit(request, apartment_id):
    if request.method == 'POST':
        form = VisitForm(request.POST)
        if form.is_valid():
            visit = form.save(commit=False)
            visit.apartment_id = apartment_id  # Assign the apartment_id
            visit.save()
            return redirect('home')
    else:
        form = VisitForm()
    
    return render(request, 'accounts/plan_visit.html', {'form': form})


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
    apartments = Apartment.objects.filter(owner__username=username)
    # get list of all apartments
    apartments2 = Apartment.objects.filter(is_vacant=True)
    # Get the chat associated with the tenant
    chat = Chat.objects.filter(tenant=web_user).first()

    context = {
        'username': username,
        'email': email,
        'first_name': first_name,
        'last_name': last_name,
        'mobile_number': mobile_number,
        'user_type': user_type,
        'owner': owner,
        'apartments': apartments,  # Pass the apartments to the template
        'apartments2': apartments2,
        'chat': chat,  # Pass the chat object to the template
    }

    return render(request, 'accounts/profile.html', context)


@login_required
def submit_files(request):
    if request.method == 'POST':
        form = FileSubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            current_user = request.user
            current_user.files = form.cleaned_data['files']
            current_user.save()
            
            return redirect('profile')
    else:
        form = FileSubmissionForm()
    
    context = {
        'form': form,
    }
    return render(request, 'accounts/submit_files.html', context)


def tenant_file(request, username):
    try:
        tenant = WebUser.objects.get(username=username)
        file_path = tenant.files.path  # Use 'path' instead of 'url'
    except WebUser.DoesNotExist:
        return render(request, 'error.html', {'message': 'Tenant does not exist'})

    return render(request, 'accounts/tenant_file.html', {'file_path': file_path})
# Add any other views you require
