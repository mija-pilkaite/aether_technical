from django.urls import path
from .views import landing_view, project_create_view, signup_view, get_utility_tariff, utility_tariff_view, create_project

urlpatterns = [
    path('', landing_view, name='landing'),  # Set the landing view for the root URL
    path('create/', project_create_view, name='project_create'),
    path('signup/', signup_view, name='signup'),
    path('utility_tariff/', utility_tariff_view, name='utility_tariff'),
    path('utility/api/get-utility-tariff/', get_utility_tariff, name='get_utility_tariff'),
    path('api/projects/', create_project, name='create_project'),
]