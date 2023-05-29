from django.contrib import admin
from django.urls import path, include
from accounts import views
from accounts.views import HomePageView, SignUpView,  MaintenanceRequestView, SignInView, VacancyPostingView, posted_vacancies, tenants_list, ApartmentDetailsView, ProfileView

app_name = 'accounts'

urlpatterns = [
    
    path('admin/', admin.site.urls),
    path('', HomePageView.as_view(), name='home'),
    path('signup/', SignUpView.as_view(), name='signup'),
   
    path('maintenance/request/', MaintenanceRequestView.as_view(), name='maintenance_request'),
    path('login/', SignInView.as_view(), name='login'),
    path('vacancy-posting/', VacancyPostingView.as_view(), name='vacancy_posting'),
    path('posted-vacancies/', posted_vacancies, name='posted_vacancies'),
    
    path('accounts/', include('django.contrib.auth.urls')),
   path('apartment/<int:pk>/', ApartmentDetailsView.as_view(), name='apartment_details'),
   path('profile/', ProfileView.as_view(), name='profile'),
 path('accounts/profile/', views.profile, name='profile'),
 path('tenants-list/', views.tenants_list, name='tenants_list'),
    # Add other URL patterns for login, chat, notifications, etc.
]
